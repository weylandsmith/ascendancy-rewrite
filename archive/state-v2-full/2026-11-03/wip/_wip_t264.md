# _wip_t264 — REWRITE LAYOUT WIRING (pure code)

Task (STATE queue): fold the t252/t253 live measurements into
rewrite/src/ui/layout.cpp — sidebar rects, button icons (1starmap.shp
SHAPEITEM frames), ship-design tab->gizmo-category map; tests pin the map.

## S1 — Primary-source re-derivation (this session, not dossier inheritance)

Re-parsed extracted/ascend00/windows.txt (cr-stripped) with a block parser
(132 TYPE blocks). Every rail control (X0==474) dumped with
rect/STATE/SENDMESSAGE/SENDPARAM1/SENDPARAM2/SHAPEFRAME/HELPINDEX/WINITEMS:

  STATUS      474,130-632,160  '1 1'  msg 1 p1 10  frame -1  1plan     items 2
  FLEET       474,169-632,199  '1 1'  msg 1 p1 18  frame -1  1ships    items 2
  RESEARCH    474,208-632,238  '1 1'  msg 1 p1 20  frame -1  1res      items 2
  SPECIALAB   474,247-632,277  '1 1'  msg 5 p1 0   frame -1  1special  items 2
  RACES       474,286-632,316  '1 1'  msg 1 p1 7   frame -1  1races    items 1
  Intelligence 474,303-632,333 '1 7'  msg 1 p1 14  frame -1  inteli    items 0
  NEXTTURN    474,52-548,82    '1 1'  msg 7        frame 65  1next1    items 0
  TURNCOUNT   474,7-632,43     '1 1'  msg 0        frame 65  turncnt   items 0

All six dossier rects (ui-runtime.md §6a) match verbatim. NEW facts the
dossier did not carry: the SENDPARAM1 == target-window STATE-number law is
confirmed for the two dossier-pinned pairs (FLEET p1 18 == FLEETWND '1 18'
line 1725; RESEARCH p1 20 == RESWIN '1 20' line 1763) AND extends: STATUS
p1 10 == STATUSWND '1 10' line 1020, Intelligence p1 14 == INTELSCREEN
'1 14' line 1109, RACES p1 7 == the '1 7' STATE class (RACE_* buttons
lines 724-843 carry STATE '1 7' p1 13 -> racesel; the Intelligence item is
part of that same STATE class, which is why §6a marked it "hidden until
Species menu"). [inferred] label kept on the general law: 4/4 checked
instances + the STATE-class shape; no code-side verification.

SHAPEITEM child lines (exact file text, the icon law):
  RESEARCH   -> SHAPEITEM 1 data\1starmap.shp 3 109 0
  FLEET      -> SHAPEITEM 1 data\1starmap.shp 4 109 0
  STATUS     -> SHAPEITEM 1 data\1starmap.shp 5 109 0
  SPECIALAB  -> SHAPEITEM 1 data\1starmap.shp 7 109 0
  RACES      -> TEXTITEM 0 Species 0 2 2 only (WINITEMS 1, NO shape)
Intelligence has WINITEMS 0 (no items at all). => the four icon buttons are
{3=Research, 4=Ships, 5=Planets, 7=Special}; frames 0-2 belong to the
library's other users (window-class art), NOT to RACES/Intelligence. A
rewrite that assumed "every sidebar button has an icon" is wrong.

## S2 — gizmos.txt parse + the tab->category map

Parsed extracted/ascend00/gizmos.txt (records after the '#' marker at
physical line 87, name-line + numeric-line pairs): 76 records, cat counts
{0:10, 1:6, 2:5, 3:6, 4:5, 5:44} — identical to the t253 dossier AND to the
rewrite's own loadGizmos invariant (economy.cpp:128 hard-checks 76).
FILE ORDER of the category blocks: 0,1,2,3,4,5 contiguous (blocks in file
order = ['0','1','1'...] walk; first-appearance order 0..5). So the GIZLIST
per-category order == the file order == gizmosByCategory() order
(economy.cpp:234-239 walks file order). [verified file-level]

Ship-design tabs (windows.txt lines 897-1002, PARENT SHIPDESSCREEN,
STATE '1 8', 30x30 tiles, row 1 y7-37 / row 2 y46-76):
  WEAPONS   485,7-515,37   frame 2  msg 51  -> cat 0  [t253 measured]
  HULL      524,7-593,37   frame 3  msg 50  -> NOT a gizmo category [t253]
  DEFENSES  602,7-632,37   frame 4  msg 52  -> cat 1  [t253]
  ENGINES   485,46-515,76  frame 5  msg 54  -> cat 2  [t253]
  SENSORS   524,46-554,76  frame 6  msg 53  -> cat 3  [t253]
  ENERGY    563,46-593,76  frame 7  msg 55  -> cat 4  [t253]
  SPECIAL   602,46-632,76  frame 8  msg 57  -> cat 5  [t253]
The msg->cat map is NOT monotone (53->3, 54->2; msg 56 belongs to no tab)
— t253's measured conclusion, re-corroborated structurally here: the tab
file order (WEAPONS HULL DEFENSES ENGINES SENSORS ENERGY SPECIAL) differs
from the msg order (50 51 52 53 53/54 swapped: HULL 50 WEAPONS 51 DEFENSES
52 SENSORS 53 ENGINES 54 ENERGY 55 SPECIAL 57). A derivation from msg or
from tile index is wrong; the table is data.

## S3 — Module shape (decision)

Followed the t263 poppanel template: a dedicated pure header
ui/hudlayout.{h,cpp} (no SDL, compiled directly into run_tests like
layout.cpp/poppanel.cpp) rather than crowding layout.h. Contents:
- kRailRects[6] + railButtonFor(Pt) (inclusive-hit law; rail x-band
  474..632; Intelligence inside RACES -> enumeration order decides, pinned);
- SidebarIcon {shapeFile, frame} + sidebarIcon(name) — 1starmap.shp frames
  3/4/5/7, nullopt for RACES/Intelligence;
- kShipTabTable[7] + gizmoCatForShipTab(msg) + shipTabForGizmoCat(cat)
  (HULL msg 50 -> -1; Special -> Special cat 5);
- gizmoListOrder(gizmos, msg) == gizmosByCategory(cat) identity asserted
  via the file-order law (S2);
- TURNCOUNT/NEXTTURN constants already lived in layout.h — untouched.
Pin test tests/test_hudlayout_t264.cpp: constants vs windows.txt, rail hit
map, icon law, the 6/6 tab map + HULL negative + msg-56 negative, and the
live-file join (loadGizmos on extracted/ascend00/gizmos.txt: per-category
sizes {10,6,5,6,5,44}, head names Mass Barrage Gun / Ion Wrap / Tonklin
Motor / Tonklin Frequency Analyzer / Proton Shaver / Lane Blocker == the
t253 live GIZLIST first rows).
