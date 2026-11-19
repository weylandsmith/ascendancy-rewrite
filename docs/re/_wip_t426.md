# t426 WIP — GALAXY MAP VISUALS CYCLE

Assignment (STATE.md 2026-11-18): map BORDER missing; PLAYER ICON UPPER LEFT
(user verbatim 2026-11-17); HOME STAR = player icon + TWO rings at game start
(derive which condition paints each, do NOT copy the guess); chrome texture per
t422. Authority: docs/assets/refcap/original-strategic-map.png, png = screen+40,
palette-PURE (R-t425c: do NOT read race-strip/slot pixels from it — clipped).
scratchpad/galaxymap-original.png = 642x481 identity, NOT palette-pure.

## F0 — orientation
- Port draw site: rewrite/src/ui/ui.cpp ~1000-1120 (mapVisible block): bevel =
  two SDL rects (kBevelMid outset at kCosmosWnd-1, kBevelIn at the window rect),
  home marker = WHITE SQUARE ring at r+3 (named seam, ui.cpp:1103-1113).
- No sitting since last iteration (timeline tail 12 recs, turn 1254 == floor).

## F1 — BORDER measurement [VERIFIED, scripts/t426_border_measure.py]
Cosmic-frame law in the PURE refcap (note: my conv map used *255//63 floor;
vendor renders at round(v*255/63) — OFF(77,113,117)==idx19 raw(19,28,29),
OFF(89,134,138)==idx24 etc; treat OFF labels as +1-scale palette px):
- TOP BAND screen rows 0..6 = CHROME TEXTURE full width (x60..420 scan):
  y0-1 bright teal ramp (idx 6/19/24/56/176 + grey 81,81,81=idx~?), y2 mid
  (grey 52/53 + 157/201 accents), y3..y6 DARKENING to near-black teal
  (48/49/2/1/200, (40,65,69)); screen row 7+ = PURE BLACK (BACKGRNDCOLOR 0).
- LEFT BAND screen cols 0..6 = chrome, same gradient law (col0-1 bright teal
  29/27/22%, col6 dark 49:32% 3:27% (40,65,69):20%); col 7.. = 100% black
  rows 60..460. [t411's "x7 (49,54,53)" scan was the SCRATCHPAD — the pure
  refcap says col7 is black; the two-line flat bevel is NOT vendor.]
- RIGHT transition: cols 460..465 black, col 466+ chrome at y100/200/300/400
  (sidebar). COSMOSWnd x1=465 exact.
- BOTTOM: screen rows 473.. = chrome (scratchpad rows 473..477 non-pure but
  same ramp families; refcap CLIPS screen 440..479 — bottom law must come
  from the scratchpad + top/bottom symmetry).
- PORT DEFECT: ui.cpp:1020-1031 draws two FLAT rect lines (kBevelMid/kBevelIn)
  at the window edge; vendor has NO line — chrome texture runs INTO the window
  edge, field interior is pure black to 7,7..465,472.
- Upper-left png block y50..62 x10..24 shows a BRIGHT rounded object INSIDE
  the black field at screen ~(10..40, 10..40) with green (0,170,81)/(0,142,69)
  + idx242 + idx16 px — THE PLAYER ICON lead (F2).

## F2 — PLAYER ICON upper-left [CLOSED ON EVIDENCE 2026-11-19]
THE PLAQUE IS raceflag.shp RECORD k0 — 100.0% EXACT-EQUAL on opaque px
(vendor round(v*255/63) palette scale, tol<=3/px) at png (10,52) == SCREEN
(10,12), 14x24. scripts/t426_plaque_match.py over EVERY record of EVERY
extracted/ascend01/data/*.shp (dims 10..40 x 15..40, offsets -6..+6);
runner-up 52.3% (8shipdes k0) — no ambiguity. (probe 2's bbox was chrome
contaminated: it cropped from screen (2,2) and swallowed the top/left bands;
its ASCII "object" rows 50..74 were png rows == screen 10..34, and the
"green rounded thing" is this plaque, nothing else is non-black inside the
field above screen row 40 except the race-strip band at png rows 80..86.)
PLAQUE COMPOSITION [verified, grid in probe output]: border ring idx19
(0,170,81), interior idx242 navy (12,32,48), glyph strokes idx16/17/18
(0,85,40)/(0,113,56)/(0,142,69) — i.e. the species flag face for the
PLAYER's species at game start. k0 = first record; census which species
k-index maps to (raceflag lib order) before wiring a per-species index.

## F2b — PLAQUE FRAME LAW [VERIFIED, exact — SUPERSEDES the +2-offset draft]
raceflag k0 header law: k0 stream sits at rec+8 (NOT rec+0x18; that is the
k>=1 offset — t425b law, and my probe's k0 decode was wrong until corrected
by the C++ decoder's disagreement). Correct k0 decode: EVERY row opaque;
row 0 = 14x idx19 (green top line), col 0 = idx19 every row, navy + glyph
interior — the record IS a 14x24 half-frame. LAW (identical at both
anchors, probe /tmp/ph.py): vendor draws 15x25 idx19 outline + navy
interior at anchor A, blits raceflag k<specnum> AT THE SAME A:
  k0@A  = 336/336 opaque px EXACT (tol<=3), residual 39 = frame right
          column (25) + bottom row (14), both idx19.
  k0@A+2 = 322/322 "exact" was the same pixels shifted (47.8% at A) — the
          +2 draft is VOID; anchors are A=(10,10) plaque, (285,77) crest.
Plaque A = screen (10,10) — the frame's bottom/right lines complete the
record's half-frame. [correction trail: pd.py row-scan + ph.py soff test.]

## F3 — HOME STAR marker [MEASURED 2026-11-19]
Pure refcap home star: core-dot centroid (idx97/39/99/100, n=20) png
(114,292) == SCREEN (74,292).
- WHITE RING: idx15 n=22, abs extent png y108..116, x286..298 — flat top
  (y108 x290..294), sides to x286/x298 at y112..116; bottom hidden under
  the crest frame (png 117+). NOT a shape record (census over all 8..20px
  records: best 37.1% mouse.shp junk) -> code-drawn ellipse centre
  (starx, stary-2) rx 6 ry 4.
- CREST: frame+raceflag k0 at png (285,117) == SCREEN (285,77) ==
  (starx-7, stary+3) — 336/336 EXACT at the SAME anchor (F2b law).
- idx111 (150,215,255) diagonal up-right + idx115 (142,0,0) rows 113-114
  LEFT are TRANSIT/LANE TRACES through the home star, not marker rings.
VERDICT on "player icon + TWO rings" (user verbatim): MEASURED = ONE white
ellipse ring + the raceflag crest; the apparent second ring is the lane-
trace diamond around the star in the same shot [inferred]. No vendor ring at
any other constant radius exists in the palette-pure shot (census by radius
from the dot: only crest colours idx16/17/18/19/242 at r 5..27 and traces).

## F4 — PORT + PINS + WITNESS [SHIPPED 2026-11-19]
PORT (ui.cpp mapVisible block):
(i) BEVEL REMOVED (F1 law): the two kBevelMid/kBevelIn rect lines are gone;
    the field is a pure-black FILL at 7,7..465,472 and the clip rect is the
    field itself. kBevelMid/kBevelIn constants stay in mapchrome.h (the
    t411 pin test still reads them) but are no longer painted.
(ii) FRAME TEXTURE extended to FOUR bands (mapchrome.h): top rows 0..6 x
    7..465 and bottom rows 473..479 x 7..465 join the left/right bands;
    frameTex build loop is generic over kTextureBandCount. The in-band
    luminance GRADIENT toward the field edge (F1: y0-1 bright -> y3..6
    near-black) is NOT modelled (textureColourAt is a flat census mix) —
    NAMED SEAM.
(iii) PLAQUE: 15x25 navy fill + idx19 (chromePaletteArgb(19)) outline rect
    at (10,10) + raceflag k<playerSpecies> blit at the SAME anchor, inside
    the field clip. human (-1) = honest-empty frame (rail precedent).
(iv) HOME MARKER: white-square seam replaced by (a) white ellipse ring
    centre (q.x, q.y-2) rx 6 ry 4 (64-point parametric; idx15 law) and
    (b) the same plaque frame+flag composite at (q.x-7, q.y+3).
PINS rewrite/tests/test_plaque_t426.cpp x3: palette colours named (idx19
(0,170,81), idx242 (12,32,48)); raceflag k0 decode law (14x24, row 0 = 14x
idx19, col 0 idx19 every row, all px nonzero rows 0..23, count 21) — this
pin is what CAUGHT my probe's wrong k0 stream offset; composite geometry
(anchors, residual 39 = 25+14). SUITE 434/0/0 (+3; test_rail_t400 band
count updated 2->4 with the law comment).
WITNESS scripts/t426_plaque_witness.sh (--species 0 = the refcap's own k0):
top band y3 360/360 nonblack, bottom band y473 360/360, plaque outline 76
green px, crest frame 76 green px at the LOGGED home-star anchor
(254,438)->(247,441), and THE BAR: plaque 15x25 block exact-diff vs the
palette-pure refcap = 375/375, ZERO residual. VERDICT PASS.
MUTATION x2: plaque anchor 10->11 FAILS (166/375); bottom band y0 473->474
FAILS (band black at y473 — first sample row was y476, which survived the
mutant; tightened to the measured edge row).

## F5 — ledger + residuals
- OQ rows: galaxy-map visuals have NO OQ owner (t414..t425c precedent);
  closes NOTHING — honest negative. OQ-027 stays open pending the final
  hearing verdict; OQ-016/OQ-019 DEFERRED per assignment.
- NAMED SEAMS left open: (a) top/bottom band in-band gradient; (b) the
  ring's exact ellipse params under projection (vendor code-drawn ring law
  not decompiled — Ghidra instance not running this iteration; the
  64-point ellipse reproduces the measured idx15 extent png y108..116
  x286..298 at the rest pose); (c) raceflag k-index <-> species mapping for
  species != 0 (t401 uses k<specnum> verbatim at (9,10) in the newgame
  DESC panel — same convention adopted here, unverified for this site).

## F6 — CYCLE 2: BAND GRADIENT LAW (start note 2026-11-19)
Question (STATE.md NEXT ACTION): the in-band luminance gradient of the four
chrome bands. (a) per-row WEIGHT reweighting of the census colour set
(D17-legal inside textureColourAt) vs (b) deterministic per-pixel ramp
(needs vendor generator — static route EXHAUSTED, R-t422c). Bar: per-row
census chi-square vs vendor rows, not hand-tuning. Probe
scripts/t426c_band_gradient.py: per-row census of pure-refcap top band
(png rows 40..46 = screen 0..6, x 60..420 clean zone + x 7..59 / 421..465
edge zones for x-dependence), scratchpad bottom rows 473..479 (non-pure,
identity), left band per-ROW check (must be flat if the column law holds),
right strip cols 466..472 per-row, and the CROSS-SCREEN top-band identity
test (map vs planet-view vs species-research) — if the top band is
screen-fixed like the left band (chrome.md F1), the gradient belongs to the
same field and a row-keyed weight table is the honest shape.

### F6.1 probe 1 results (scripts/t426c_band_gradient.py, RC=0, floor-scale
labelling — OFF buckets are the vendor's rounded rgb vs *255//63 truncation,
re-mapped in probe 2):
- TOP band per-row census IS strongly row-dependent (x60..420): row0-1
  {6,56,176 bright}, row2 {53,52}, row3 {52,49,53,3,48}, row4-5 {48,49,2,1},
  row6 {2,1,48,49,200}; row7+ 100% black idx0. Mean-lum profile
  106.5/106.2/83.7/65.5/45.3/46.9/28.3 -> 0. The gradient is EDGE-NORMAL.
- DECISIVE cross-screen test (D): top band rows 0..6 x0..465 map-vs-
  planet-view AND map-vs-species (planet/species identical to each other):
  row0 99.8%, row2 96.6, row3 93.1, row4 93.1, row5 92.3 (rows 1/6/7 lower
  = overlay content shifts between shots). The GRADIENT IS PART OF THE SAME
  SCREEN-FIXED FIELD as the left band (chrome.md F1) -> option (b)
  deterministic-ramp-decompile is NOT needed; a row-keyed census table
  inside the Markov chain is the measurement-supported law shape (option a).
- LEFT band has NO row gradient: per-row censuses rows60..460 are flat
  (56:6.4-11.8, 53:6.8-10.4 stable). The gradient law is per-band-edge,
  NOT global: left band = per-COLUMN (t422 F7), top band = per-ROW.
- RIGHT strip x466..472 shows NO darkening toward the field (mean lum
  88-113 rows 2-12) — the right edge carries no edge-normal gradient in the
  interior rows (honest negative; sidebar chrome is the flat kRight law).
- Top band h-run k1 0.61-0.64 (vs left band v-run k1 0.616) — consistent
  with the same noise run statistics along the band direction.

### F6.2 probe 2 (scripts/t426c_chi2.py, RC=0) — GRADIENT = (a) PER-ROW
CENSUS REWEIGHTING, chi2-proven; chain must run ALONG-BAND.
(pitfall banked: first run mapped PAL[3*j] instead of PAL[3*i+j] — 100%
OFF garbage; round scale round(v*255/63) tol<=1 gives ~0 OFF everywhere.)
- TOP band per-row census (round space, x7..465) — the kTopRow table:
  row0 55:32.5 6:22.7 56:21.6 57:11.5 176:8.1 58:2.2 5:1.5
  row1 55:44.0 56:19.6 6:17.2 176:9.6 57:8.7 58:0.7 5:0.2
  row2 53:34.2 54:15.5 52:13.9 157:12.6 4:10.0 55:4.8 51:3.5 201:2.4 56:2.0
  row3 50:28.5 51:23.7 49:16.1 52:15.5 53:7.0 3:3.3 48:3.1 2:2.0 55:0.7
  row4 48:29.6 49:24.0 2:15.7 50:13.9 51:7.2 1:4.8 52:2.2 200:2.0 0:0.4
  row5 48:26.1 49:25.5 50:16.8 2:13.3 51:8.7 1:6.8 52:2.2 200:0.4
  row6 2:32.9 1:27.2 48:20.7 49:9.8 200:7.0 50:2.2 0:0.2
  Rows are colour-DISJOINT families: bright (55/56/6/57/176) -> mid
  (53/54/52/157/4) -> dark (48/49/49/50/51) -> near-black (2/1/200).
- SIDEBAR TOP rows 0..6 x466..639 carries the SAME per-row gradient
  (census shape matches) -> rows 0..6 use the row table at FULL WIDTH;
  the y-branch must precede the x-branch in textureColourAt.
- CHI-SQUARE (gen vs vendor per-row, n=459/row): CURRENT flat-kRight law
  {78,208,1771,7405,666,567,334} (df~10, p<<1e-6 — the flat law is REFUTED
  for the band); per-row table + edge-normal chain 5/25
  {14,7,147,182,168,23,59}; per-row table + ALONG-BAND chain (copy-left
  25%/repeat-up 30%) {17,7,45,14,23,31,20} <- best.
- RUN-LENGTH ANISOTOTROPY (round space): TOP band h-run k1 0.653 (along-
  band repeat ~0.354) / v-run k1 0.824; LEFT band h-run k1 0.767 / v-run
  k1 0.605 (along-band repeat ~0.380). THE SAME NOISE FIELD, ROTATED:
  repeat probability runs ALONG the band in both. Port replay along-band
  h-run 0.606 vs vendor 0.653.
- RIGHT EDGE BAND x466..472 has its OWN per-column census (rows 60..460,
  n=401/col): col466 {5:37.7 176:34.4 53:20.4 54:7.5}, col467/468 bright
  {58:~53 173:~25 59:~18}, col469..472 mixed — NOT the flat kRight set
  (58/173/59 absent from kRight). The right field-edge band is the mirror
  of the left band (per-column law), t422 F7 covers only x0..6.

### F6.3 probe 3 tuner (scripts/t426c_tune.py) — chain shape DECIDED
- TOP band per-row table replay, chain sweep (copy-left, repeat-up) %:
  (5,25) chi2 {12.9,6.8,146.8,181.6,167.8,23.3,59.4} hrun k1 0.788
  (25,25) chi2 {17.4,15.0,17.6,13.7,11.8,26.4,16.4} hrun k1 0.609 <- SHIP
  (35,25) {18.1..28.8} hrun 0.522 (over-long runs); (45,25)/(55,25) worse;
  (25,30) {17.6,6.6,45.3,...} mid. VENDOR hrun k1 0.653 k2 0.231 k3 0.078.
  LAW: top band = copy-left 25%, else fresh draw from kTopRow[y] (no
  repeat-up). Edge-normal chain (5/25) is what makes rows 2-4 chi2-explode.
- BOTTOM band (scratchpad rows 473..480 x60..420, round space): per-row
  OFF 24.4-100% — THE SCRATCHPAD CANNOT YIELD A COLOUR LAW (interpolation,
  chrome.md F3 pitfall re-confirmed at the bottom edge). Measured facts
  only: mean-lum profile s473 65.4 -> s475 160.4 (ridge) -> s479 104.2;
  dark at the FIELD edge (agrees with the top band's edge-normal
  directionality) but a BRIGHT RIDGE at 475 and the mirror of the top
  profile (bright at 479) is NOT supported. NO pure source exists: every
  refcap is png=screen+40 clipped at screen 439 < 473. DECISION: bottom
  band STAYS the flat kRight law (cycle-1 state); gradient existence banked
  as a named seam needing a pure bottom capture (user play-shot or live
  frame-pair). Replay of scratchpad-count tables aborted (empty row 473) —
  the table itself is unbuildable, which IS the finding.
- RIGHT FIELD-EDGE STRIP x466..472 (probe 2 §C, pure refcap rows 60..460,
  n=401/col, round space): its OWN per-column tables — col466
  {5:37.7 176:34.4 53:20.4 54:7.5}, col467 {58:54.1 173:25.4 59:17.0},
  col468 {58:51.9 173:25.4 59:19.2}, col469 {57:34.2 7:29.2 58:13.2 56:9.7
  6:8.7}, col470 {54:23.4 6:16.7 56:16.2 55:15.2 57:11.2 176:9.2}, col471
  {53:17.7 55:16.0 54:12.7 157:12.2 51:10.5}, col472 {55:18.7 157:13.2
  53:11.7 51:10.5 54:9.2}. 58/173/59 are NOT in kRight -> the flat kRight
  law is REFUTED for the first 7 sidebar columns. NOTE the right edge is
  BRIGHT at the field edge (col467-468 idx58) while the LEFT edge col6 is
  DARK (49/3/50/48) — the four edges do NOT share a symmetric gradient;
  per-EDGE tables are the law shape, not a mirror formula.

### F6.4 SHIPPED (rewrite/src/ui/mapchrome.cpp textureColourAt)
(i) y-DISPATCH FIRST: rows 0..6 = kTopRow[y] (10-entry vendor count
tables, round-palette RGB, full width incl corners x0..6 and the sidebar
span x466+); (ii) ALONG-BAND CHAIN for rows 0..6: copy-left 25%, NO
repeat-up; other classes keep the t422 5/25 chain; (iii) kRightEdge[7]
per-column tables for x466..472 (col467/468 idx58/173/59 ridge).
PIN statistics (measured on the shipped law via the identical python
replay, then verified in-suite): row0/1 bright>70 frac 1.000 (vendor
1.000), row6 dark<60 frac 1.000 (vendor 1.000 — every row-6 census colour
is <60 lum; the flat-kRight mutant sits at 0.13), row-mean envelope
l0/l3 1.69 (vendor 1.63), l3/l6 2.25 (vendor 2.31), h-repeat row3 0.406
(vendor 0.347, edge-normal mutant 0.212, iid floor ~0.15), band v-repeat
0.126 (anisotropy pin vrep/vtot < (2/3) hrep). right_edge_ridge pin:
col467/468 mean lum >=100 (vendor 133.6/133.7 rows 60..460) + idx173 mauve producible
(0 under the flat law). SUITE 437/0/0 (+3 test_bandgrad_t426c).
HONEST RESIDUALS: (a) bottom band rows 473..479 stays flat kRight — no
pure colour source on disk (scratchpad census 24-100% OFF; refcaps clip
at screen 439); mean-lum profile banked (65 -> ridge 160@475 -> 104);
(b) our h-repeat 0.406 vs vendor 0.347 — copy-left 25% is the tuner's
chi2-best, run-length slightly long (25/30 variant chi2 {18,7,45,14,23,
31,20} vs 25/25 {17,15,18,14,12,26,16}: kept 25/25 on rows 2-4 chi2).
