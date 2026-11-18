# t422 WIP — CHROME LAW: textured frame derived from RE (root-cause row, phase 16)

## F0 Starting state (session-start facts, all previously banked)
- D17 round-4 seed defect: "chrome texture grainier/larger than original
  EVERYWHERE". Port currently uses splitmix64 hash-noise (mapchrome
  textureColourAt, menulaw §4 page texture, statusbg, title) — BANNED
  synthetic stand-in per D17 law (1).
- Vendor chrome is SHAPE ART: windows.txt (extracted/ascend00/windows.txt,
  2238 lines) declares 9 TYPE-100 SHAPEFILE headers + 124 named windows.
- windows.txt parse (this session, fresh): TYPE-100 headers in order:
  0OPENING.SHP, 1STARMAP.SHP, 3CFGNEW.SHP, 7RACESEL.SHP, 8SHIPDES.SHP,
  13NEGOT.SHP, 16BATTLE.SHP, 20RES.SHP, TESTDLG.SHP [verified by grep of
  '^SHAPEFILE' — 9 hits]. Per-window SHAPEFRAME values banked to
  /tmp/t422_bylib.json (per-screen lib -> windows -> SF table).
- windows.txt does NOT declare 2SAVEGAM/4LOADGAM/17NP/10STATUS etc. as
  TYPE-100 headers — those libs are used by code paths, not window defs.
- Prior t391 claim "vendor lacks 18*.shp": libs matching *18* under
  extracted/ascend01/data/ are ONLY black18.haz, smrace18.shp, smship18.shp
  [verified ls] — i.e. no 18frame.shp-style chrome lib; NEWGAMEWND T18 is a
  window TYPE, its art lib is 3cfgnew.shp SF=0 (t401 banked).

## Probe plan (budget ~35 calls)
P1 census the candidate chrome records: dims of 1starmap.shp k0..k2,
   3cfgnew k0, 16battle k0, 0opening k0 — the SF=0 records are the
   full-window frames (chrome) per boot.md/t401 precedent.
P2 Ghidra: find the generic window chrome paint (window manager draws
   SHAPEFRAME record of the window's lib at window rect). Decompile it;
   extract the tiling/scale law (whole-record blit vs corner+edge+tile).
P3 md5 identity: decode the cited record, compare against vendor pixels
   (existing captured vendor screenshots where available).
P4 Implement shared drawFrame() off derived records ONLY, or name
   per-screen migration debt; grade one frame 1:1.

## F1 [MEASURED] The chrome mottle is a FIXED SCREEN-SPACE FIELD, shared
## across screens — not per-window tile art (tools: numpy over refcap PNGs).
- Left chrome band x1..6 rows 0..479 (capture-shift-corrected +40 on the
  pinned captures) compared pairwise across three vendor originals:
  strategic-map vs planet-view 83.2% pixel-IDENTICAL at zero shift;
  map vs species-research 84.1%; planet-view vs species-research 99.1%.
  Cross-shift profile peaks sharply at shift 0 (0.83 vs 0.42 at ±1) —
  the pattern is anchored to SCREEN coordinates, not window rects.
  => CHROME LAW (1): the mottle is a screen-fixed backdrop field; a
  per-window tiling law is REFUTED for this class.
- y-periodicity k=8..240 all at noise (0.22-0.24 vs 0.053 baseline floor
  from 19 distinct colours) => NOT a small repeating tile (no 8/16/32
  spike); the field is aperiodic (or period >= field height).
- Palette census (pinned map left band, 19 distinct colours): EXACTLY
  two adjacent game.pal ramps — greys idx 2,3,4,5,6 (28/48/64/80/97)
  and teals idx 48..58 (24,48,40 -> 97,145,145) — plus idx 157
  (72,72,85) and 201 (60,52,56). All 19 within dist<=3 of exact palette
  entries (6-bit *255//63 scaling). The mottle = dither over a GREY RAMP
  + a TEAL RAMP.
## F2 [MEASURED] ROOT CAUSE of "grainier than original" (D17):
- Vendor PURE chrome (left band): lag-1 luminance h 0.62 / v 0.40,
  h-adjacent-equal 0.132. t411's calibration band x474..632 (0.23) was
  CONTAMINATED by sidebar widget art — that is why the port's 6x6-cell
  mottle was tuned too smooth for the widgets yet still reads wrong.
- OUR current render (work/r1/loop/walk/map_view.png left band):
  lag-1 h 1.46 / v 1.21, h_eq 0.062 = TV static. The t411 "0.22 witness"
  does NOT hold on the pure band — ours is 2.4x grainier than the vendor
  EVEN IF the 6x6 law is active; check textureColourAt call sites next.
## F3 scale caution: scratchpad/galaxymap-original.png is 642x481
(scaled/interpolated — 7903 distinct colours in a zone where the pinned
640x480 capture shows 176). ALL chrome statistics MUST use
docs/assets/refcap/*.png (exact 640x480), never the scaled user shots.

## F4 [MEASURED] The vendor mottle is NOT iid colour-sampled — vertical
## correlation is real; the port's generator law is wrong in KIND.
- Vendor left band (pinned map, 440x6 window, palette-index space):
  vertical RUN length dist 1:0.616 2:0.234 3:0.092 4:0.026 5:0.014;
  an iid sampler of the SAME 19-colour census gives 1:0.907 2:0.08
  3:0.011. Lag-1 luminance: vendor h 0.62 / v 0.40 vs iid 1.36/1.36
  vs OUR current render 1.46/1.21 (work/r1/loop/walk/map_view.png —
  note: ours is per-PIXEL static EVEN THOUGH t411's 6x6-cell law is in
  the tree at mapchrome.cpp:72; the walk shot Nov 15 predates nothing —
  t411 landed Nov 16, shot is OLDER than the fix; re-measure after
  rebuild before trusting either).
- Field law: vertical runs ~2x longer than horizontal (v_eq 0.398 vs
  h_eq 0.201 on the left band; right zone 0.554/0.589) => the noise
  field is VERTICALLY STRETCHED (anisotropic), consistent with a
  low-res noise bitmap blitted/stretched, or noise sampled on a taller
  cell grid.
- Cross-screen: left band map-vs-planet 83% identical (F1) but right
  zone map-vs-planet 0.7-12% (widgets differ) while planet-vs-species
  88-93% — same field + same widgets => field is SCREEN-FIXED, drawn
  before widgets, NOT per-window art.
## F5 [MEASURED] OUR render paints (120,120,120) in the left band —
## NOT a game.pal colour (nearest (117,117,117) dist 9; vendor band has
## ZERO 120-greys). Off-palette stand-in to remove with the new law.
## F6 SHAPEFRAME semantics note: 13negot NEGSCREEN SF=0 but 13negot.shp
## has N=2 records only; PLAYERDIP SF=7 impossible in a 2-record lib =>
## SHAPEFRAME indexes the window TYPE's generic widget lib (T10 listbox
## -> listbox.shp k7-class), not always the screen lib. census: listbox
## k0 24x24/k1 24x24/k2,k3 14x14. [unverified which exact table]

## F7 [MEASURED] Per-column index census of the vendor left chrome band
## (pinned map, palette-index space, rows 40..479) — the band is a
## LEFT-BRIGHT -> RIGHT-DARK LUMINANCE GRADIENT dithered between the teal
## ramp (idx 48..58) and the grey ramp (idx 2..6), plus idx 157/201
## accents appearing only x>=3:
  x0: {6:98, 55:130, 56:120, 57:53, 58:8, 176:26, 5:5}
  x1: {6:46, 55:209, 56:94, 57:59, 176:28, 5:2, 58:2}
  x2: {5:42, 54:143, 55:126, 56:45, 176:76, 57:6, 157:2}
  x3: {53:58, 54:150, 55:49, 157:92, 176:53, 4:15, 5:11, 56:8, 57:2, 201:2}
  x4: {3:5, 4:47, 51:83, 53:103, 54:90, 157:92, 201:10, 55:7, 56:1, 57:2}
  x5: {4:39, 51:80, 53:117, 54:76, 157:108, 201:10, 50:1, 52:1, 55:5, 56:3}
  x6: {2:6, 3:123, 48:45, 49:143, 50:86, 51:27, 52:7, 53:1, 55:2}
  x7: 98.4% BLACK (field edge).
## F8 [INFERRED from F4 run stats] Vertical noise is a FIRST-ORDER MARKOV
## chain: vendor v-run dist 0.616/0.234/0.092/0.026/0.014 == geometric
## p=0.616 r=0.385 EXACTLY (k=1..5); h-run 0.833/0.138/0.025 == r=0.166.
## Not a cell grid, not iid: per-pixel noise with P(repeat)=0.385 vertical,
## 0.166 horizontal. [inferred] vendor generator = noise bitmap blitted
## from a smaller buffer (vertical stretch explains anisotropy) OR a
## per-pixel Markov fill. DECISIVE TEST: two vendor runs of the same screen
## -> identical field = seeded/fixed; differing = live random (then the
## LAW can only be statistical).
## F9 planet-view vs species-research left band 99.1% identical (residue =
## the 2 captures' overlay rows) => the field persists across screens;
## map-vs-them 83% => regenerated or different seed on the map screen
## [unverified which].

## F10 [MEASURED] Right-zone (x466..639) chrome census, pinned map,
rows 40..479, exact-palette (6->8 *255//63) index space, chrome-set
colours only: 55:7587 6:3514 56:3093 176:2018 57:1997 58:1483 48:1163
49:1095 2:968 53:928 (37% of the zone; the rest is widget art + navy
12,32,48 field + black). NOTE the earlier t400 "texture everywhere in
x466..639" reading is OVERSTATED: the zone is majority widget pixels;
chrome shows through in the gaps. (First census attempt used the RAW
6-bit palette -> garbage; always scale.)

## IMPLEMENTED (this iteration)
- rewrite/src/ui/mapchrome.cpp textureColourAt: t422 Markov field law
  (copy-left 5% / repeat-up 25% / per-column census fresh draw; left
  kLeft[7][10] from F7, right kRight[10] from F10; splitmix64(x,y),
  pure, no rng_). mapchrome.h header updated (t400 geometry kept,
  generator superseded).
- test_maplook_t411.cpp: mottle_cell_law_t411 REPLACED by
  mottle_field_law_t422 (determinism, >=8 colours, vrep window
  [0.27,0.45], cell-quantisation ABSENT <60%).
- scripts/t422_fit.py (tracked): parameter grid fit, re-run output
  PH=0.05 PV in [0.25,0.30] err 0.074.
- docs/re/chrome.md = the CHROME LAW deliverable (D17 queue t422).

## GRADE (native vision, work/r1/loop/walk/map_t422.png)
Left strip + sidebar gaps read as FINE per-pixel noise, no blocks, no
stripes. Mechanical: v_eq 0.405 (vendor 0.398), vrun 0.603/0.233/0.098
(vendor 0.616/0.234/0.092), h_eq 0.172 (vendor 0.201), 120-grey off-
palette pixels 0. RESIDUAL: lag1 h 0.96 vs vendor 0.62 — fresh draws
are census-iid while vendor neighbours skew luminance-adjacent; ramp-
walk variants measured WORSE on the 8-stat fit; named seam chrome.md
SS4(a) (decider: vendor noise-generator decompile). MUTATION: M1 cell-
quantisation CAUGHT (seen>=8 fails), M2 iid CAUGHT (vrep floor).
Suite 421/0/0; gate GATE_EXIT=0; ledger 17/3 (closes NOTHING — chrome
seam has no OQ owner, t414..t421 precedent).
