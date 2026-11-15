# t398 PALETTE FIDELITY — working file (stream findings here before each probe)

Session start state: ruling server LIVE (pid 646702, :8613). Ring
t368_ring_turn parsed=20/20 max_turn=1254 = same sitting as t380..t397 ->
r1_t85g_sitting.py NOT run. Tree clean. D11 USER lines intact (11:37:07);
the 11:40:35 "selftest = ok" block from t397b's scratch-port self-test was
STRIPPED from DECISIONS.md but server.log still shows it — harness artifact,
no ledger meaning (banked as observation; server never touched the real file).

## S0 TARGET (the seam being closed)
blitShape (rewrite/src/ui/vendortext.cpp:104) colours every .shp index through
a luminance ramp `lum = 40 + idx*185/255` — the cause of every D11
"greyscale/wrong art" verdict (rail icons, bottom-right cluster, hide/show box,
New Game bottom row). Seam banked boot.md §PALETTE: "no cited palette exists
for the menu .shp libs".

## S1 THE PALETTE EXISTS AND IS NAMED BY THE EXE [verified]
work/ascend_payload.bin string census (exact bytes, NUL-delimited):
- 0x83579: `DATA\game.pal` (referrer context `.. \corn.cpp`, adjacent
  `resume.gam`, `GIF SCRATCH`, `DATA\0OPENING.GIF`) — the corn.cpp title/screen
  init cluster loads game.pal.
- 0x84207: `DATA\game.pal` again, context `.. \flicwin.cpp` / `FONT TRANSLATE`
  / `.. \font.cpp` — the flic/font cluster.
- 0x834c6: `data\logo.pal` + `data\logo.gif` pair — logo.pal belongs to the
  logo.gif path, NOT the chrome.
File: extracted/ascend01/data/game.pal, 768 B = 256 RGB triples, every channel
<= 63 (6-bit DAC), 18 grey / 238 colourful entries.
docs/re/loader.md §5 already lists `palette game.pal` among the DATA\ load
templates. game.pal was tried ONLY as a title-screen palette and refuted there
(title-art.md §4) — the chrome was never tested against it. The boot.md seam
prose ("no cited palette exists for the menu .shp libs") conflated the title
refutation with the chrome question.

## S2 MEASURED LAW: every in-game refcap shot is 100% inside
game.pal under the DOSBox 6->8-bit conversion c = (v<<2)|(v>>4)
(pinned docs/assets/refcap/*, self-captured vendor runs, untracked media):
  original-strategic-map.png   307200/307200 px IN   (logo.pal-conv 75.43%)
  original-species-research.png 307200/307200 IN     (logo.pal-conv 90.53%)
  original-planet-view.png     307200/307200 IN      (logo.pal-conv 82.06%)
  original-title-menu.png      27015/307200 IN (8.79%)  <- title is a DIFFERENT
                                                          palette (t386 TSV), as
                                                          t386 measured
Zero pixels outside. The three in-game shots contain the chrome the user calls
greyscale (map rail, species menu, planet view). If chrome painted from .shp
libs through any other palette existed, some chrome pixel would fall outside
game.pal. Next probe: the t386 registration CONFLICT-COUNT law per lib/rect at
the capture shift — decisive per-library, not just membership.

## S3 TOOLING + FIRST REGISTRATIONS (honest negatives banked)
New tools: scripts/t398_palette_register.py (scalar) and
scripts/t398_band_register.py (numpy; pip-installed numpy into ~/tools/revenv;
selection law = fewest conflicts THEN richest learned map, flat-background
placements flagged [VACUOUS]).
- docs/assets/refcap/original-strategic-map.png IS the in-game map screen
  (vision read of rail crop: Planets/Ships/Research/Special Ability/Species
  rows with COLOURED icon art right of labels; teal button fill (12,32,48) =
  game.pal idx 242 [verified]). Root-window shot: game rows = root rows - 40;
  teal bands land at game y 130..160/209-40... = the cited kRail rects minus
  40 shift — the +40 capture law re-confirms on chrome.
- 1starmap rail-icon records k3/k4/k5/k7 registration in the rail band: every
  placement conflict-free but FLAT or near-flat (distinct map colours 1-2) —
  the 43x22-class records do NOT register as the icon art against the shot.
  The icons in the shot are richer than those records' painted masks; either
  the icons come from other records/frames or the walk of 1starmap (heads are
  NON-VERBATIM per shp.md straggler class) misdecodes. NOT yet resolved; the
  PALETTE question does not depend on it: membership + registration of the
  CHROME zones is what decides the palette.

## S4 THE DECISIVE WITNESS (mechanical + external-vision allowed source)
PIL self-decode of 1starmap k3/k4/k5/k7 + 1starmap k19 + 10status k0 +
3cfgnew k0 THROUGH game.pal (conv (v<<2)|(v>>4)) -> /tmp/t398-gamepal-sheet.png,
external vision read: k3 = gold branching tree on green; k4 = deep-blue space
with orange body + teal planet curve; k5 = glowing orange sun + grey-blue
planet; k7 = planet with white/pink flare; k19 = dark starfield strip;
10status k0 = legible Empire-status panel. Colours judged PLAUSIBLE.
CROSS-MATCH vs the pinned refcap rail (vision): shot rail icons = Planets
(orange planet + grey moon) == k5; Research (yellow nodes on green) == k3;
Special Ability (gold flare) == k7. THE SHOT'S RAIL IS THESE RECORDS PAINTED
THROUGH game.pal. Frame->button mapping nuance (k4 ships-icon question, icon
side/size) = t400 geometry scope, NOT the palette question.
Rail fill teal (12,32,48) == game.pal idx 242 exact [verified].

## S5 REGISTRATION LAW MEASURED (colour-match, game.pal, padded refcap shot)
Method: render the record's index plane through game.pal, slide over the rail
band of /tmp/t398-map-pad.png (refcap strategic-map cropped to game coords,
shift law: root rows -40), minimise mean |RGB diff| (numpy,
scripts/t398_band_register.py sibling probe run inline):
  rec 3 (43x22) mean|diff|=6  at (584,213) 93% pixels within 12  (Research row)
  rec 4 (44x23) mean|diff|=6  at (585,175) 93%                     (Fleet row)
  rec 5 (44x27) mean|diff|=3  at (585,130) 97%  exact kRail y0=130 (Status row)
  rec 7 (45x30) mean|diff|=36 at (585,248) 64%  exact kRail y0=247 (Ability row;
      flare partly OVERPAINTED by the Intelligence row's teal fill overlap ->
      degraded match is expected, position still exact)
ICON X = 584/585 = RIGHT of the label (D11 geometry complaint confirmed;
blitShape placement law change is t400 scope). CONCLUSION [verified]: the
chrome .shp libs ARE painted through game.pal at game start; the ramp is the
defect. Frame->button mapping here came out SHAPEITEM-order-consistent for
3/5/7 (Research/Status/Ability) — k4-vs-Ships icon identity stays a seam
(t400), the PALETTE law does not depend on it.

## S6 CODE LANDED + LIVE WITNESS PASS
- rewrite/src/formats/gamepal.{h,cpp} (ascend_core): GamePalette load/parse
  (768 B refuse-not-clamp), DOSBox conv, rgb/argb (index wraps, alpha 255).
- vendortext.cpp: blitShape colour path = game.pal when loaded, ramp ONLY as
  documented degradation; loadChromePalette(dataRoot) once-per-process, prints
  `ui palette: game.pal (256 entries, 6->8 bit)` or the named degraded line.
  Wired in runCampaignUi + runTitleScreen. CMakeLists: gamepal.cpp +
  tests/test_gamepal_t398.cpp. SUITE 322/0 (318 -> +4 pins; one test-side
  arithmetic bug caught by the run: 255+242 wraps to 241, fixed 256+242).
- WITNESS scripts/t398_palette_witness.sh (Xvfb :97, RESUME one window) +
  scripts/t398_witness_census.py VERDICT PASS: palette line present, rail
  icon zone (x474..540 per OUR placement law — census follows the code, t400
  moves icons right) 131 chromatic colours, 130 inside game.pal; the ONE
  outside colour is (40,40,56) = our port's own rail FILL (by design, t264
  choice — not art). The ramp path yields EXACTLY 0 chromatic pixels, so the
  census mechanically separates the two paths (self-graded vision untouched).
- Screenshots /tmp/t398_shots/{title,map}.png for USER look-grading (D11
  re-test); copy banked work/r1/loop/t398-map.png.
