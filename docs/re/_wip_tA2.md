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
tA2-CONT: restrict the chain to the ridge band, extend t441_screen_diff.py
with chrome-band regions, mutation-verify every tA2 constant, bank
map/title application checks. LEDGER: seam work, open=[016,019].

## F7 — RIDGE CHAIN-ANCHOR FIX [MEASURED 2026-11-21, tA2-CONT item (1)]
Fix in newgameWellEdgeColourAt (mapchrome.cpp): the repeat-up recursion now
excludes BOTH ridge rows (`y > 7 && y != 373 && y != 374`). Two rejected
variants, both reasoned BEFORE building:
- 374 recurses to 373 (band-internal carry): stationary expectation
  0.7*102.8 + 0.3*64.4 ~ 92.7 — outside the +-6 window. The vendor census
  settles it independently: each ridge row holds its OWN rung family in
  matching counts (grey 169/169, teal 108/107, 71/70) = per-row draws from
  the rung-shifted tables, NOT a vertical carry.
- Recess columns keep chaining up within their own column (witness col7
  6.5 == vendor 6.5 before and after — the guard doesn't touch them).
WITNESS (scripts/r1_tA2c_witness.py, run via ~/tools/revenv/bin/python —
NOTE: repo .venv has NO numpy/PIL; t441 harness runs under revenv too):
post-fix shot /tmp/t412_shots/t412-newgame.png (scripts/t412_newgame_shot.sh):
  row7 22.5 (vendor 24.3, tol 6) PASS
  col7 6.5 (6.5) PASS; col493 19.1 (22.9, tol 6) PASS
  row373 64.4 (64.5, delta -0.1) PASS; row374 103.1 (102.8, +0.3) PASS
  well rows 8/372 blackfrac 1.000 PASS  -> WITNESS PASS, exit 0.
The ~14-lum ridge defect is CLOSED at measurement; the census tables were
already correct (tab means 64.40/102.82 computed from source).

## F8 — t441 HARNESS CHROME-BAND REGIONS [VERIFIED 2026-11-21, item (2)]
scripts/t441_screen_diff.py EXTENDED (not re-homed): new region kind
"band" = mean-lum window + census-family share on BOTH sides (vendor crop
= ground truth for the law; ours = the render). Family = pixel within
<=10/channel of a cited top-3 census colour; fam_min sums family shares
(ridge rows score up to ~1.7 = grey+teal rungs). 10 new regions on
newgame: topbar rows1-6 (window 66.4+-15), topbar row0 (geometry-only —
per-instance chrome law t433 makes a mean window meaningless: ours 105.8
vs vendor instance 39.0 BOTH inside 20..220), recess row7 (23.4+-3 +
fam 0.90), recess col7 (6.5+-2.5), col493 (21.0+-3.5), well rows 8/372
(mean <=0.5 pure black), ridge 373 (64.5+-6 + fam 1.40), ridge 374
(103.0+-6 + fam 1.30), panel-top381 (30.5+-4.5 + fam 2.20). Windows set
from scripts/r1_tA2c_bandprobe.py BOTH-SIDE measurement (ours/vendor:
row7 22.5/24.3, ridge 64.4/64.5 + 103.1/102.9, panel381 29.5/31.6 —
every band inside its window with >=1.5 lum margin both sides).
VERDICT: newgame 17/17 PASS (7 tA1 + 10 bands), planetslist 2/2 PASS
unchanged (/tmp/ta1c_shots/status-open.png vs
work/r1/loop/vendor-planetslist-t3-640.png, exit 0).

## F9 — MAP/TITLE APPLICATION VERDICTS [CITED 2026-11-21, item (4)]
- MAP: frameTex (kTextureBands + textureColourAt, ui.cpp:1068) is 100.00%
  pixel-exact vs the generator field dump in the left/bottom/top bands (F1);
  right-column deviations coincide exactly with windows.txt sidebar widget
  rects = content over chrome, not a second chrome painter. NO CHANGE.
- TITLE: title screen = 0opening.gif decode (title.cpp:77 buildTitleTexture
  -> gifDecodeFile; 341 single RenderCopy). No kBevel site, no chromePage on
  Title (chromePage begins at RaceConfig/New Game, title.cpp:407-426). The
  only kBevel use left in title.cpp is the racering FALLBACK ring (741) —
  dead whenever the shape lib loads (dimscheck witness 109x109). NO CHANGE.
Both verdicts banked chrome.md 3a.

## F10 — PIN STRENGTHENING + MUTATION CAMPAIGN [2026-11-21, item (3)]
Pin (test_mapchrome_tA2_well_edge_law) strengthened: band means (m373
58..71, m374 96..110, m7 17..28, ml 4..9.5, mr 14..26, mp 21..33, mql
27..40) + EXACT-COLOUR share windows vs tab marginals (n24 0.16..0.45,
n61/n97 0.21..0.50, n578 0.25..0.55, n000 0.27..0.57, npl 0.17..0.52,
n12_24_34 0.19..0.50) + exact kBeginPanelVisual {502,381,632,472} +
kNewgameCosmosRect.x0==8. Why: per-pixel bounds alone are BLIND to weight
mutations (chain preserves the marginal; a near() distance window was also
wrong — all kLeft families sit within dist 30 of each other — exact eq()
counts are provably chain-invariant). Checkpoints a77c789 + 2 more BEFORE
first mutant. Campaign scripts/r1_ta2c_mutate.py (working-path keys,
md5-verify restore + abort, os.utime, background+notify per skill):
VERDICT 12/12 CAUGHT, every one naming mapchrome_tA2_well_edge_law:
M1/M2/M3 cosmos rect y0/x1/y1 (exact pins, lines 134-136); M4/M5 ridge
grey weights 169->60 (n61/n97 share windows — MEAN was blind, shares
caught); M6 recess-top 93->20 (n24); M7 recess-left 90->20 (n578); M8
recess-right 102->20 (mr + n000); M9 kBeginPanelVisual.x0 502->494 (exact
+ gutter pins); M10 ridge table swap (dark-above/light-below + m373/m374,
5 FAILs); M11 CHAIN-REVERT 'y>7' (the fixed defect re-appears, m373/m374
— the anchor law is pinned, not just witnessed); M12 recess L/R table
swap (ml/mr). AFTER-RESTORE build 0, 472 tests 0 failed; md5sum -c
pristine OK all three files.

## F11 — tA2 CLOSE VERDICT [2026-11-21]
tA2-CONT items (1)-(5) all landed: ridge chain fixed + witnessed within
+-6; harness bands 17/17 + planetslist 2/2; mutation 12/12; map/title
application cited (F9, chrome.md 3a); banked here + chrome.md. LEDGER:
seam work, touches no OQ row, open=[016,019] unchanged. tA2 STAYS OPEN
as a row ONLY for its named D19-deferred residue (mineral lag-1 ceiling,
chrome.md 4); the chrome LAW + harness clause is CLOSED in substance.
