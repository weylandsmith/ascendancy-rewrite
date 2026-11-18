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
