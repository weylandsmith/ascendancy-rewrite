# CHROME LAW (t422) — the vendor chrome texture is a screen-fixed Markov
# noise field, not shape art and not hash noise

Scope: the mottled grey-teal "chrome" the port paints on the map left
margin + right column (t400), the New Game page bands (t401), the status
perimeter (t417b), the title bands (t411/t354). D17 round-4 defect:
"chrome texture grainier/larger than original EVERYWHERE".

## 1. What the vendor chrome IS [MEASURED, this iteration]
All statistics below measured with numpy over the PINNED 640x480 vendor
captures docs/assets/refcap/original-{strategic-map,planet-view,
species-research}.png (NEVER the scaled 642x481 scratchpad shots — F3
pitfall: interpolation invents 7903 "colours" in a 176-colour zone).

1. SCREEN-FIXED FIELD, not window/shape art: the left band x1..6 is
   83.2% pixel-identical between strategic-map and planet-view, 99.1%
   between planet-view and species-research, all at ZERO shift (shift
   +-1 drops to 0.42). A per-window SHAPEFRAME tiling cannot produce
   cross-screen pixel identity at fixed screen coordinates. windows.txt
   SHAPEFRAME therefore governs WIDGET frames (buttons/listboxes), not
   this backdrop. (Cross-check F6: 13negot.shp has N=2 records yet
   PLAYERDIP carries SHAPEFRAME 7 — SHAPEFRAME indexes the window TYPE's
   generic widget lib, e.g. T10 listbox -> listbox.shp, not the screen
   lib. [inferred from the impossibility; exact table not yet cited].)
2. NOT a repeating tile: y-periodicity k=8..240 all at the noise floor
   (0.22-0.24 vs 0.053 iid floor) — no 8/16/32 spike.
3. NOT iid colour sampling and NOT a coarse cell grid. Vendor left band
   (rows 40..479, x1..6): vertical run-length distribution
   k=1:0.616 k2:0.234 k3:0.092 k4:0.026 k5:0.014; iid sampler of the
   same census gives 0.907/0.08/0.011. Lag-1 luminance ratio h 0.62 /
   v 0.40; iid = 1.36/1.36; the port's old per-pixel hash = 1.46/1.21
   (= TV static — THE ROOT CAUSE of "grainier than original").
   t411's 6x6-cell law was calibrated on band x474..632 which is
   CONTAMINATED by sidebar widget art (true vendor pure-band lag-1 v is
   0.40, not 0.23); the cell grid is REFUTED on the pure band.
4. COLOUR LAW: every band pixel is an exact game.pal entry (within the
   +-3 tolerance of the 6-bit*255//63 scale). The field dithers between
   the grey ramp idx 2..6 (28/48/64/80/97) and the teal ramp idx 48..58
   (24,48,40 -> 97,145,145) plus accents idx 157 (72,72,85) and 201
   (60,52,56). Per-column census banked in _wip_t422.md F7 — the band is
   a left-BRIGHT -> right-DARK luminance gradient (col mean lum
   105.9,105.9,96.8,88.1,78.6,78.6,51.7) dithered with the two ramps.
5. NOISE LAW (port implementation): per-pixel Markov chain —
   P(copy pixel LEFT)=0.05, else P(repeat pixel ABOVE)=0.25, else fresh
   weighted draw from the per-column census. Fit by grid search over 8
   statistics (h_eq, v_eq, lag1 h/v, run1/2 h/v); scripts/t422_fit.py
   re-run output: best PH=0.05, PV in [0.25,0.30], mean abs deviation
   0.074 (PV=0.25 within seed noise of 0.30; alternatives tested: iid
   floor dev ~0.3, 6x6-cell ~0.2, exclusion model worse). Deterministic
   purity preserved: chain decisions are splitmix64(x,y), recursion to
   the fresh-draw anchor — no rng_, no state
   (rewrite/src/ui/mapchrome.cpp textureColourAt).

## 2. Witness (mechanical, this iteration)
OUR render after the change (work/r1/loop/walk/map_t422.png left band):
  lag1 h/v 0.96/0.56, h_eq 0.172, v_eq 0.405, v-run 0.603/0.233/0.098
VENDOR:
  lag1 h/v 0.62/0.40, h_eq 0.201, v_eq 0.398, v-run 0.616/0.234/0.092
Run-length + vertical correlation now MATCH vendor; the residual gap is
lag-1 luminance (0.96 vs 0.62 h): our fresh draws are census-iid, the
vendor's tend to land ramp-ADJACENT (a dither-of-noise the vendor's own
generator produced; no on-disk evidence identifies its exact neighbour
rule — named seam, see §4). The old law's gap was 1.46/1.21 vs
0.62/0.40 AND stripes-free run statistics were absent entirely.
Off-palette (120,120,120) frame-line pixels: 0 (F5 class removed — the
remaining "off-palette by 1" values are the vendor's own rounded rgb,
e.g. 19*255//63=76 truncation vs vendor 77; the census stores VENDOR
pixels, which is what the user's screen shows).

## 3. Migration status
ONE shared generator (textureColourAt) feeds every chrome class in the
port: map bands (ui.cpp:302, status perimeter ui.cpp:330 via
kStatusTextureBands), the New Game page (vendortext.cpp:411), title
(title.cpp:368). All migrated in this row by construction. The status
HEADER SPECKLE (statusbg.cpp statusSpeckleAt) is a DIFFERENT measured
class — per-pixel noise lag-1 1.304 [t417b measurement] — deliberately
NOT Markov; leave as-is unless a pure-band re-measurement refutes it.

## 4. Named seams (honest negatives)
(a) [CYCLE 2 UPDATE] The EXACT vendor pattern (which pixel gets which
    colour) cannot be replicated from still captures, and the STATIC
    DECOMPILE ROUTE IS NOW EXHAUSTED (t422 CONT cycle 2, _wip F11-F16):
    the only RNG in the exe is the Borland LCG at 0x7824f
    (state*0x41C64E6D+0x3039, return (state>>16)&0x7fff) and NONE of its
    59 call sites is a chrome/backdrop paint path (all sim/init); the
    hinted blitter FUN_0005d5a1 is an affine shape-record stretch blit
    (cache 0x9f10c, 255-transparent key) with zero noise math; there is
    no on-disk pattern table (single 13-byte run image-wide); and the
    F8 stretched-buffer hypothesis is REFUTED (row-identity has no
    plateau at any k=1..440, scripts/t422c_rowperiod.py). Where the
    field's pixels are BORN remains uncited: F1's cross-screen identity
    says one screen-space surface painted once; F13 says the hinted
    blitter only stretches decoded records (no noise math); no static
    generator or table exists to feed it. Closing the encoder would be
    OQ-005-class codec work and blind sweeps are forbidden. STATISTICAL
    LAW IS THE CEILING — SS1.5
    stands; swapping the fresh draw for an uncited neighbour rule would
    violate the D17 derive-from-RE law. Remaining conceivable decider
    (NOT queued): live debugger frame-pair of the backdrop surface.
(b) SHAPEFRAME widget-lib table (which lib each window TYPE uses for
    its frame records) — census contradiction found (F6); needs the
    winmgr table decompile. This is the t423+ chrome-framing question,
    NOT this backdrop class.
(c) 1starmap k0 (158x75) remains REFUTED for the band (t400), and the
    10status/2savegam/4loadgam 639x479 records are STATE-10 backdrops
    (t388/t394), not the chrome field.

## 5. Pins
rewrite/tests/test_maplook_t411.cpp TEST(mottle_field_law_t422)
(supersedes mottle_cell_law_t411): determinism, non-degeneracy, vertical
correlation window [0.10,0.45] (iid floor / stripes ceiling), cell-
quantisation ABSENT (cell-grid mutant caught at 100% vs <60% pin).
Suite 421/0/0.

## 6. t426c BAND GRADIENT LAW — the field is EDGE-NORMAL and per-EDGE
[MEASURED 2026-11-19, docs/re/_wip_t426.md F6.1-F6.4; probes
scripts/t426c_band_gradient.py + t426c_chi2.py + scripts/t426c_tune.py]

The t422 flat per-column mix is REFUTED for two classes of the field:
1. TOP BAND (screen rows 0..6, FULL WIDTH incl. corners and over the
   sidebar): per-ROW census, colour families bright (55/6/56/57/176) ->
   mid (53/54/52/157/4) -> dark (50/51/49/48) -> near-black (2/1/200);
   mean-lum 106.5/106.2/83.7/65.5/45.5/46.9/28.3 then 100% black row 7+.
   Cross-screen identity vs planet-view AND species-research rows 0..6
   x0..465: 99.8/69.5*/96.6/93.1/93.1/92.3/66.1% (*rows 1/6/7 carry
   shifted overlay content) -> the gradient is the SAME screen-fixed
   field, so census tables (not a ramp generator) are the law shape.
   CHAIN ORIENTATION: noise repeats ALONG the band — copy-left 25%, no
   repeat-up (vendor h-run k1 0.653; edge-normal 5/25 replay 0.788 blows
   rows 2-4 chi-square: 147/182/168 vs 17/14/12).
2. RIGHT FIELD-EDGE STRIP x466..472: per-COLUMN census (rows 60..460,
   n=401/col); col467/468 carry the bright idx58/173/59 ridge (col means
   133.6/133.7) — colours absent from kRight, and the right edge is
   BRIGHT at the field edge while the left col6 is dark: NO symmetric
   mirror law; per-edge tables only. Chain stays 5/25 (strip v-run k1
   0.574 == along-band orientation for a vertical strip).
3. BOTTOM BAND rows 473..479: mean-lum profile exists (scratchpad 65 ->
   ridge 160@475 -> 104) but the scratchpad census is 24-100% OFF-palette
   interpolation and every pure refcap is png=screen+40 clipped at screen
   439 — NO colour table derivable on disk. Stays flat kRight. NAMED SEAM
   (closer: a pure bottom-edge capture, e.g. a live frame grab).
4. Left band x0..6 rows 40..479: NO row gradient (per-row censuses flat
   across y) — the t422 per-column law stands; rows 0..6 of columns 0..6
   belong to the top-band table (vendor corner px are the bright family).
Port: mapchrome.cpp textureColourAt dispatches y-first (kTopRow[7] rows
0..6, chain 25/0), then kRightEdge[7] (x466..472), then kLeft/kRight.
Pins tests/test_bandgrad_t426c.cpp x3, mutation-verified x4 (edge-normal
chain CAUGHT hrep+vrep; flat top CAUGHT dark+envelope; flat right strip
CAUGHT x4 named FAILs; AFTER-RESTORE 437/0/0). Witness
scripts/t426c_grad_witness.sh + t426c_witness_census.py VERDICT PASS on
our render (row means 109.0/106.7/82.8/64.6/46.4/46.2/28.8 vs vendor
106.5/106.2/83.7/65.5/45.3/46.9/28.3; strip 87.0/131.2/133.2/121.8 vs
vendor 86.1/133.6/133.7/120.7). Residual: our h-repeat 0.406 vs vendor
0.347 (copy-left 25% slightly long; 25/30 scored worse on row chi2).

## 7. t433 MEMORY-SURFACE VERDICT — MANY DETERMINISTIC INSTANCES, NO SURFACE
[MEASURED 2026-11-20, docs/re/_wip_t433.md F0-F7; probes
scripts/t433_surface_probe.py, t433_canonical_probe.py,
scripts/t433_instance_relation.py, scripts/t433_fb_resident_probe.py]

1. SS4(a)'s "which pixel gets which colour cannot be replicated from still
   captures" holds, but the companion premise behind t433 (ONE canonical
   memory surface exists to be extracted) is REFUTED. The field comes in
   INSTANCES that are a deterministic function of UI/repaint state. A 49-shot
   sweep of work/screens/{t252,t253,t268} (left band screen x0..6 y40..439,
   palette-index plane) lands every shot on one of a few instances at 100.0%
   identity: the strategic-map instance (t252 baseline/species_menu, t253
   baseline, t268 baseline/races — three independent sessions, byte-identical,
   and identical to ref-map); a window-open instance (t252 intel_open, t268
   intel_row, t253 fleet_open, = ref-planet; planet-vs-species refcaps agree
   99.1%); a research-window instance (= ref-species: t252 research_open/
   res_pan_v*, t268 node_*/reswin); a design-screen instance (all 10 t253
   tab*/design*/reopen shots at exactly 75.1/85.5/85.5 vs map/planet/species);
   a diplomacy instance shared by t252 sel_orfa and t268 neg_orfa
   (78.7/65.7/66.2). Repainting DOES happen — SS1.1's "painted once" is
   painted-once-per-repaint — and each repaint reproduces ITS instance exactly.
   [verified]
2. Instances are NOT phases of one buffer: vertical shift sweep dy=-300..300
   over all 20 ordered instance pairs gains at most 2.0 identity points; no
   index offset k satisfies B == A+k (top delta is always the 0 of identity).
   One extracted surface therefore cannot be re-phased to cover them.
3. NO SURFACE ON DISK: 396 signatures of 4 stacked left-band rows (28 B) ->
   0/471 files in extracted/; a 448 B top-band block -> 0. Single 7-B rows hit
   16 files (max 147 in 7racesel.tmp/1starmap.tmp) but the same regions give 0
   at 28 B, so those are low-entropy coincidences, not a stored field.
4. NO SURFACE IN THE SAVE CORPUS: 63 28-B and 400 7-B band signatures -> 0
   hits in Memory (17,055,880 B) and Vga (2,647,348 B) of 20 saves
   (work/r1/bank-play-20261111). Vacuity gate closed: game.pal's raw 768 B IS
   in both members (Vga 0x845c5, Memory 0x28a6b3 -> phys 0x28a62b), but 45
   64-B signatures of distinctive screen content score 0/45 in BOTH — the
   displayed frame is not stored packed anywhere. Planar caveat handled by
   vertical-run testing at pitch 80/160/320/640: pitch 640 gets 183 supports
   (639/641/632/648 -> 0; shuffled-band null control -> 4), so a REAL
   640-pitch paletted buffer exists around member 0x2f69f9..0x335979 — and it
   is NOT the backdrop: 60 of its 40-B rows are found 0/60 in every refcap and
   its census is 82% black / 6.2% chrome-family.
=> SS1.5's statistical law STAYS the port's ceiling (R-t422c unchanged). The
   remaining conceivable decider is a live debugger session on the generator's
   SEED/STATE for a named UI instance — a different experiment from "extract
   the surface", and it buys at best one instance. NAMED SEAM T433-C.
5. Tooling laws for successors (each cost this iteration to learn):
   (a) refcap png row = screen row + 40; work/screens/*_game.png rows ARE
   screen rows. Mixing the two families at equal file rows silently yields
   junk identities (measured 22.8% where the aligned value is 100.0%).
   (b) THE PALETTE SCALE IS rgb = raw6*4 + raw6//16 (100.0% exact on
   original-strategic-map.png); the *255//63 scale quoted in SS1 is close but
   only 91.2% exact. Compare a refcap to a VNC grab in the INDEX plane, not
   raw rgb: the DOSBox scaler blends rgb (VNC grabs are 69.3% palette-exact,
   max distance 8) yet decodes back to the vendor index 100.0% of the time
   (tie control: game.pal has 253 unique rgb, 758/281600 ambiguous px, and
   excluding them changes nothing).
   (c) numpy index planes MUST be cast to uint8 before .tobytes() (int64 makes
   a "7-byte row" a 56-byte garbage needle), and signatures must be asserted
   non-empty — bytes.find(b'') matches every file at offset 0.
