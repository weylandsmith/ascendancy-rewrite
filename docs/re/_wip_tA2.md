# tA2 CHROME LAW ROUND 2 — WIP (session start 2026-11-21)

SITTING CHECK: t368_ring_turn.py -> 20/20 saves turn=1086 (no growth, no
r1_t85g_sitting re-run needed). DECISIONS.md: no USER lines after D19.

## F0 — PAINT-PATH GREP (item (1) double-layer hunt) [verified this session]
Chrome-family paint sites enumerated (opaque layers per screen):
- ui.cpp game loop: frameTex (4 kTextureBands, textureColourAt) RenderCopy
  map+species ONLY (ui.cpp:1068-1069); statusPerimTex + statusSpeckleTex
  kScreenStatus only (1098-1105); speciesWellTex kScreenSpecies only (1072);
  shape-backdrop blitShape k0 (1088) — map excluded by design (t426).
- title.cpp: titleArt GIF (341) Title; chromePage = textureColourAt FULL
  SCREEN (407-426) RaceConfig/New Game, then cosmos black-fill (431-432).
- vendortext.cpp: introPage ONE pass margin?textureColourAt:introSpeckleAt
  (450-482) — t424b law, no double.
- title.cpp Begin-dots cluster (865-890): INLINE splitmix greys painted ON
  TOP of chromePage chrome x496..570 y390..446 — a real overpaint of one
  chrome class by another (its census is separately measured, t401).
- Legacy kBevel symmetric RenderDrawRect outlines on every RaceConfig panel
  (751/779/832/876+), chip top-half highlight fills (848-859) — item (4)
  territory.
CONCLUSION (grep stage): NO screen hosts two independent chrome GENERATORS
on the same region; every screen has exactly one backdrop pass. The D19
"almost-right bar laid ON TOP of the older rougher frame" therefore reads
as TEXTURE CHARACTER mismatch (short-run static field vs vendor long-run
mineral; the t426c top-band rows chain ALONG-band so they look like a bar
laid on the cross-band field), not a literal double RenderCopy. Verify
mechanically: pixel-exactness of our render vs textureColourAt in the band
regions (SDL ARGB8888 static copy is lossless, so any deviation = a second
painter). Paint-order log line added at each chrome RenderCopy site.

## F1 — MECHANICAL DOUBLE-LAYER VERDICT (item (1)) [verified this session]
Method (stronger than a log line): the chrome textures are STATIC ARGB
copies of textureColourAt, so our render must be PIXEL-EXACT vs a
field-dump of the generator in every band region; any deviation can only
come from a second painter. Harness: /tmp/ta2/field_dump.cpp (links
mapchrome.cpp+layout.cpp; dumps textureColourAt as RGB24 over rects).
- MAP (witness /tmp/t426c_map_crop.png via scripts/t426c_grad_witness.sh):
  left band x0..6 100.00% exact (0/3360), bottom band y473..479 100.00%,
  top band rows0..6 100.00%. Right col x466..639 42.78% — the mismatch
  row-runs are EXACTLY the windows.txt sidebar widget rects (7-43, 52-82,
  130-160, 169-199, 208-238, 247-277, 286-316, 364-394, 403-433, 442-472
  = control/flag rows at 30px pitch): CONTENT over chrome, not a chrome
  painter. NO double chrome layer on the map.
- NEWGAME (scripts/t412_newgame_shot.sh -> /tmp/t412_shots/
  t412-newgame.png): chromePage is pixel-exact vs the field EVERYWHERE it
  shows (top rows0..6 mismatch n=0; left margin mismatch n=0; gutter
  x494..501 rows60..370 mismatch 0.000). The only chrome-class overpaint
  is the Begin-box dot band x496..570 y390..446 (99.95% deviates) — the
  SEPARATELY MEASURED t401 dot census, a designed content layer.
=> grep + pixels agree: exactly ONE chrome generator pass per screen; the
   D19 "bar laid ON TOP of the older rougher frame" is NOT a second
   RenderCopy. Root cause found instead at the bar EXTENT (F2): the port
   exposes two bright chrome rows BELOW the gradient bar where the vendor
   shows a dark recess — a bar that reads as laid over a second frame.

## F2 — BAR EXTENT LAW, NEWGAME (item (2)) [MEASURED, browser shot
+1,+1 law, scratchpad/newgame-original.png; G5-legal 1:1]
Vendor row means (x8..490): 0:39.0 1:103.9 2:103.6 3:79.6 4:56.0 5:44.9
6:45.5 7:24.2 8+:0.0 — top bar = rows 0..6 gradient, row 7 DARK RECESS
((10,10,10)-class, NOT chrome), cosmos pure black rows 8..372 cols 8..492.
Edge probes (row 200): x5(62,73,74) x6(44,57,55) x7(4,6,5) x8 black;
right x492 black x493(29,34,34) x494(78,91,92) chrome. Cosmos BOTTOM:
rows 373/374/375 = (53,78,78)->(85,125,125)->(125,182,182) BRIGHT ridge
(the RAISED bevel of item (4)) BEFORE chrome resumes.
OURS (t412 shot): rows 0..6 match vendor (105/104/81/62/44/44/27), but
row 7 = 77.4 and row 8 = 91.3 BRIGHT CHROME (kNewgameCosmosRect is
{8,9,493,373}: cosmos starts one row late and overruns right+bottom by 1)
=> THE D19 SIGNATURE: bright bar rows 0..6 PLUS two stray bright rows 7-8
= "almost-right bar laid on top of the older rougher frame", and the
cosmos is 1px SHORT at top (starts y9 not y8). FIX: kNewgameCosmosRect ->
{8,8,492,372} + dark recess border (top row 7 x7..493, left col x7,
right col x493) painted by the ONE chromePage pass (no new renderer).
Map screen unaffected (its field fill already starts at row 7 — t426 law,
row7 black frac 1.000 witness). Vendor row0 of the pinned MAP refcap
(screen rows) = 104.5 mean, bar rows 0..6 full-width chrome x6..636
(>0.5 col frac n=488) — unchanged, matches our kTextureBands top row.

## F3 — RECESS/BRIDGE CENSUS, NEWGAME WELL (items (2)+(4)) [MEASURED]
Game-coord censuses on scratchpad/newgame-original.png (+1,+1 law):
- row 7 (top recess) x7..493: n=487 uniq=42 mean 24.3; top
  {24,24,24}x93 {10,10,10}x62 {21,42,35}x54 {12,12,12}x26 {32,49,53}x26
  — DARK noise (browser-resampled chrome-dark + green bleed), NOT chrome,
  NOT pure black.
- col 7 (left recess) rows 8..372: mean 6.5; top {5,7,8}x90 {6,6,6}x71
  {5,8,9}x43 — near-black dark noise.
- col 493 (right recess) rows 8..372: mean 22.9; top {0,0,0}x102
  {30,30,30}x65 {33,33,33}x40 {23,35,36}x36.
- row 373 x7..493 mean 64.5: {61,61,61}x169 {53,78,78}x108 {48,71,73}x71
  (all EXACT chrome-palette dark rungs); row 374 mean 102.8:
  {97,97,97}x169 {85,125,125}x107 {77,113,117}x70 (chrome bright rungs,
  SAME x-quantisation as 373 = the two rows are one 2-px RAISED edge:
  dark rung above, light rung below).
- pure black well rows 8..372 (row 8/372 census 100% {0,0,0}).
BEVEL LAW VERDICT (item (4)): the vendor frames wells/panels with
DARK-above/LIGHT-BELOW raised edges + dark recess noise — the port's
symmetric kBevel (97,97,97) RenderDrawRect outline (title.cpp 689/723/
780/833/877) is a fabricated class the refcaps never show at well edges.
MAP refcap button edges (pure, png+40): TOGLANES left edge x478->479
(40,65,69)->(89,24,56) NO light line; right edge x508(105,154,203-light)
x509 fill->x510(69,105,109) chrome; BELOW y395/396 (85,125,125)/(125,182,
182) and ABOVE y360..363 dark chrome ramp (48,48,40-class) = RAISED
(dark above, light below) at panel BOTTOM; at panel TOP y364 fill starts
right off dark chrome (no light line) — light appears BELOW, never above.
=> ONE law: dark-above/light-below. kBevel symmetric outline stays port
defect; replacement = measured recess/ridge per well (newgame cosmos well
FIRST; other wells = per-screen C-gate application).

## F4 — MINERAL CHARACTER CENSUS (item (3)) [MEASURED, exact-plane]
Exact-colour stats over left band x0..6 y40..479 + right strip + top band
(scripts inline; field_dump harness = C++ textureColourAt raw dump):
                     lag1h  lag1v  lag2h  lag2v  v-runs(1,2,3)  h-runs(1,2)
VENDOR left band     11.20   5.66  17.01   8.31  .611/.236/.095  .764/.192
OURS   left band     14.92   8.97  18.77  11.31  .598/.237/.098  .841/.132
VENDOR right strip   16.01   4.85  26.39   7.21  .571/.219/.118  .813/.172
OURS   right strip   18.49   8.06  26.73   9.90  .600/.217/.108  .847/.135
VENDOR top band       7.68  15.33  11.16  28.24  .824/.166/.008  .653/.231
OURS   top band      10.79  19.62  13.37  29.79  .889/.103/.008  .613/.233
(run ratios MATCH to +-0.03 everywhere; the residual is the LUMINANCE
step at lag-1/2 — ours jumps 2-3 ramp rungs per fresh draw, the vendor
~1.2 rungs: exactly the chrome.md §2 named seam "vendor fresh draws are
ramp-ADJACENT". Quantified: ours/vendor lag1v left band = 8.97/5.66 =
1.58x too jumpy; a ramp-neighbour rule is the ONLY parameter that closes
it, and it is uncited (D17 law) => NAMED CEILING CONFIRMED, numbers banked.
No new generator guessing attempted.)

## F5 — BAR EXTENT (item (2)) [MEASURED — LAW FIXED, see menulaw.h patch]
Vendor (browser shot, game rect +1,+1): TOP BAR = rows 0..6 gradient
(row-0 rung class is instance-dependent: newgame instance row0 mean 39.0
dark-chrome, pinned MAP refcap row0 104.5 bright — t433 instance law
covers it; the pure refcap settles the geometry: gradient rows 0..6,
dark row 7). RECESS row 7 x7..493 (mean 24.3, dark noise census F3),
well pure black rows 8..372 x8..492, RAISED RIDGE rows 373..374 (dark
rung row + light rung row, identical x-quantisation: grey seg
(61,61,61)->(97,97,169px), teal seg (53,78,78)->(85,125,125) 107px,
(48,71,73)->(77,113,117) 70px + minors), chrome resumes row 375+.
Ours pre-fix: well {8,9,493,373} + BRIGHT CHROME rows 7..8 = the D19
"bar on top of a rougher frame" signature + 1px cosmos misplacement
right/bottom. PITFALL BANKED: browser shot row0-vs-map-refcap row0 means
differ BY DESIGN (per-instance chrome); never infer a row-offset from a
single-row mean mismatch — xcorr on the left band gave 7.8% identity
between DIFFERENT repaint instances (floor), alignment stays +1,+1.
FIX (menulaw.h + title.cpp chromePage pass): kNewgameCosmosRect ->
{8,8,492,372}; recess + ridge drawn INSIDE the one chromePage texture
(newgameWellFrameAt/newgameWellRidgeAt in mapchrome) — G6 single renderer.

## F6 — BAR EXTENT (item (2)) [PENDING measurement]
Refcap law: png row = screen row + 40 (chrome.md §7.5a). Measure top-bar
height/width from original-strategic-map.png rows 40.. , compare
kTextureBands {7,0,465,6} top / {0,0,6,479} left / {466,0,639,479} right /
{7,473,465,479} bottom + kStatusTextureBands + kNewgameTextureBands.

## F2 — MINERAL CHARACTER (item (3)) [PENDING]
Known witness (chrome.md §2): ours lag1 h/v 0.96/0.56 vs vendor 0.62/0.40
(left band); residual = fresh draws ramp-adjacent vendor-side. Census +
grid search incl lag-2; if params cannot reach, bank named ceiling.

## F3 — BEVEL LAW (item (4)) [PENDING]
Derive RAISED from refcap panel edges; one drawBevel for all frames.

## F6 — tA2 PARTIAL CLOSE: LAW LANDED, RIDGE BIAS NAMED [verified 2026-11-21]
Implemented (build 0, ctest 100% incl. new TEST(mapchrome_tA2_well_edge_law)):
- kNewgameCosmosRect {8,9,493,373} -> {8,8,492,372} (menulaw.h, cited F5).
- mapchrome.{h,cpp}: newgameWellEdgeAt / newgameWellEdgeColourAt (recess
  row 7, cols x7/x493, ridge rows 373/374; per-edge vendor censuses verbatim;
  ridge tables = FULL 98.5%-mass censuses after the top-3 truncation was
  shown to skew dark) + newgamePanelTopAt/newgamePanelLeftAt (dark inset
  top+left, NOTHING right/bottom; censuses F3).
- title.cpp: chromePage ONE pass now paints recess+ridge (G6); the FOUR
  symmetric kBevel RenderDrawRect outlines (RACELIST, 3 config controls,
  Player Color panel) replaced by the inset law; Begin panel fill moved to
  the MEASURED visual extent kBeginPanelVisual {502,381,632,472} (hit rect
  kBeginNewGameBtn unchanged) — the gutter x494..501 no longer navy.
- Witness (scripts/t412_newgame_shot.sh, post-fix): row7 mean 22.5 (vendor
  24.3), col7 6.5 (vendor 6.5), col493 19.1 (vendor 22.9), well rows 8 and
  372 100% pure black, bright-chrome rows 7..8 DEFECT GONE.
HONEST LIMIT (row 373/374): ours 50.6/90.4 vs vendor 64.5/102.8 — the
ridge is drawn but ~14 lum too dark. NAMED ROOT CAUSE (not yet fixed):
newgameWellEdgeColourAt's repeat-up chain at y=373 recurses to (x,372),
which is NOT an edge pixel but the function draws anyway from the kLeft/
kRight RECESS tabs — ~30% of ridge pixels take dark recess colours.
tA2-CONT: restrict the chain to the ridge band (recursion anchor = row
373 for y=374; row 373 always fresh-or-left-anchored, NEVER up), rebuild,
re-witness (target row means within +-6 of 64.5/102.8), then extend
t441_screen_diff.py with chrome-band regions (top bar rows 0..6, recess
row 7, ridge rows 373/374, panel insets) and mutation-verify every tA2
constant (kNewgameCosmosRect corners, ridge/recess census weights,
kBeginPanelVisual). Map/title chrome-band application checks per the tA2
CLOSE clause also remain (title = GIF art, no kBevel sites found; map
buttons already vendor-shape). LEDGER: seam work, open=[016,019]
unchanged. Gate green this iteration.
