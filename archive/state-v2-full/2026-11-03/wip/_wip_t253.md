# WIP t253 — LIVE SCREEN SWEEP 2: SHIP DESIGN + FLEET (2026-11-01)

Harness: scripts/r1_t253_screen.py (copy of the proven t252 primitive, OUT ->
work/screens/t253/). Run with ~/.hermes/hermes-agent/venv/bin/python (PIL only
there). Baseline: healthy galaxy screen, ring turn 1255, in_game=True.

## Static windows.txt dossier (cr-stripped extracted/ascend00/windows.txt)

SHIPDESSCREEN block (preceded by TYPE 100 banner STATENUMBER 8 / SHAPEFILE
DATA\8SHIPDES.SHP at line ~865):
- SHIPDESSCREEN PARENT NONE STATE "1 8" rect 7,114-476,472 MOUSEFOCUS 0
  SENDMESSAGE 1 p1 1 p2 1 HELPINDEX shipdes. (NOTE: the task text said
  "8 category tabs" — windows.txt has SEVEN tabs; measured below.)
- GIZLIST PARENT SHIPDESSCREEN TYPE 10 rect 485,86-632,471 SHAPEFRAME 7 msg 0
- WEAPONS  TYPE 0  rect 485,7-515,37   SHAPEFRAME 2 msg 51 help weapon
- HULL     TYPE 0  rect 524,7-593,37   SHAPEFRAME 3 msg 50 help hull
- DEFENSES TYPE 0  rect 602,7-632,37   SHAPEFRAME 4 msg 52 help defense
- ENGINES  TYPE 0  rect 485,46-515,76  SHAPEFRAME 5 msg 54 help engine
- SENSORS  TYPE 0  rect 524,46-554,76  SHAPEFRAME 6 msg 53 help scanner
- ENERGY   TYPE 0  rect 563,46-593,76  SHAPEFRAME 7 msg 55 help energy
- SPECIAL  TYPE 16 rect 602,46-632,76  SHAPEFRAME 8 msg 57 help special
  (tab grid = 2 rows x 3/3/1: row1 WEAPONS|HULL|DEFENSES, row2
   ENGINES|SENSORS|ENERGY|SPECIAL — SPECIAL is TYPE 16 unlike the others)
- STATE "1 8" is EXCLUSIVE to these nine windows (measured: no other window in
  windows.txt carries state 1 8) — state 8 == ship-design screen.

FLEETWND block:
- FLEETWND PARENT NONE TYPE 17 STATE "1 18" rect 7,7-632,472 SHAPEFRAME 0
  msg 0 HELPINDEX fleetwin ("Ship Status Screen")
- STATSHIPLST PARENT FLEETWND TYPE 10 rect 7,46-632,472 SHAPEFRAME 7
  (the ship list fills the whole screen below the 39px header)
- Entry point: sidebar FLEET "Ships" rect 474,169-632,199 SENDMESSAGE 1
  SENDPARAM1 18 (== STATE 1 18 of FLEETWND — the msg/param pair selects the
  screen state; same shape as RESEARCH p1 20 == RESWIN STATE 1 20, t252).

help.txt entries (cr-stripped):
- help shipdes (line 810): "used to design ships for construction at planetary
  Shipyards" + ship-maintenance-count proportional to controlled star systems
  (a species controls a system by having the ONLY colonies there).
- help weapon/hull/defense/... per-tab blurbs (range/strength/numUses/power).
- help fleetwin (line 1648): "Ship Status Screen ... left-click on a ship's
  entry to go to its current location, or right-click to bring up a display of
  its contents." => FLEET list rows: LEFT-CLICK = camera jump (safe),
  RIGHT-CLICK = contents display (safe-ish, opens sub-display).
- help shipdesx (line ~3180): "Your species does not yet have ship building
  technology" — the guard dialog if design is locked.

gizhelp.txt = the gizmo help corpus: records "#Name^Lines" + parameter line
"#Cat Power Range Level NumUses Industry Special1 Special2 ResReq {flag_list}"
+ help gizmoNN text + "shape 0 0 75 57" — the in-game gizmo popup geometry is
75x57 at the gizmo origin; the parameter line IS the gizmo table law input
(cross-ref ai-dossier/combat.md S2f dispatcher 0x4cd90).

## Live sweep log

- preflight/baseline shot: ring 1255, zero drift; vision confirms galaxy
  screen, sidebar labels Planets/Ships/Research/Special Ability/Species, no
  popup open.
- step fleet_open click (553,184) [FLEET rect center]: diff vs baseline
  116404 px, ring 1255 held. -> FLEETWND opened (details below).

## HAZARD FOUND (t253, live): stale 'Quit DOSBox-X warning' landmine on :9

xwininfo -root -tree shows window 0x1000025 "Quit DOSBox-X warning" mapped
(IsViewable) on display :9, owned by `xmessage -buttons Yes:1,No:0 -default
Yes -center "You are currently running a program or game..."` PID 461872,
PPID 1 (reparented to init), STARTED Sat Oct 31 19:40:49 — 14 h BEFORE the
current dosbox-x (PID 479968, started Nov 1 07:44:45). So it is the quit-confirm
of an ALREADY-DEAD dosbox instance, left mapped. YES IS THE DEFAULT BUTTON: any
root-coord click that lands on it kills the game (t244/S4 law restated: SIGTERM
pops this dialog, Yes default).
- Mitigations applied: (1) killed the orphan xmessage PID 461872 ONLY (never
  pkill -x xmessage, never touched dosbox); (2) tools/xsend already refuses to
  target a window whose name contains "warning" — that guard fired here and is
  why the first click3 printed "REFUSING blocker window".
- LESSON: xsend's blocker check prints but keeps searching, and STILL SENDS to
  the game window; the blocker message is a warning about a DIFFERENT window,
  not a refusal of the send. Verify dialog presence with
  `xwininfo -root -tree | grep -i warning` before a sweep, not via xsend output.

## FLEETWND (Ship Status Screen) — LIVE DOSSIER, ring 1255, zero drift

Header band (y 7..45 per FLEETWND rect 7,7-632,472): renders
"Chamachies (25 Ships, 12 more allowed)" — i.e. the header carries the OWNER
race name plus a PAIR (in-service count, remaining allowance). This is the
live instantiation of the help shipdes law "the number of ships you can
maintain is proportional to the number of star systems you control" -> the
allowance is computed and shown as headroom, not a raw cap. [vision-read text]

Rows (STATSHIPLST 7,46-632,472, SHAPEFRAME 7): 4 rows visible for 25 ships =>
the list is paginated/paged by the right-rail scroll pair. Measured row pitch
from the bright-text band analysis (~105 px per row block: bands cluster at
52-111, 128-170, 203-246, 264-323, 340-352, 370-429, 446-458 -> two text lines
per row: NAME line + status line, row block ~105 px). Blue scroll arrows
MEASURED by pixel detection (blue-dominant, x>=560): bands y 59-68 and 450-457,
x 606-635 => centres (620,63) and (620,453).
Row columns (left->right, vision): ship render (silver hull art) | ship NAME
(green) | small gizmo/cargo icons under the name | green chevron chain (>>>>) |
vertical column of blue spheres | LOCATION text (cyan).
Row text read [vision-read, treat as posture not ledger data]:
 Sparrowhawk "Orbiting Pulveran II"; Erebor "Orbiting Unterwelt III";
 Erchamion + Ignatz "In Starlane to Flammifer System ETA - 10 Days".
=> TWO location verb-forms observed: "Orbiting <Planet>" and
   "In Starlane to <System> System ETA - <N> Days". The ETA is in DAYS, same
   unit law as RESWIN (t252) and the t244 gauge popup.

BEHAVIOUR LAWS CONFIRMED END-TO-END (help fleetwin verbatim: "left-click on a
ship's entry to go to its current location, or right-click to bring up a
display of its contents"):
- LEFT-CLICK row1 (200,93): diff 109479 px; screen became a PLANET/ORBITAL
  view (top strip of 5 thumbnail panels incl. one labelled "Scientist
  Takeover"; main field = orbital structures inside a faint RED shield sphere).
  Zero turn drift. Escape -> back to FLEET list (esc1 vs baseline 116461 px,
  i.e. still the fleet screen, not the galaxy).
- RIGHT-CLICK row1 (200,93) via `tools/xsend DOSBox-X click3`: opened the
  SHIP CONTENTS DISPLAY (see next section). Zero turn drift.

## Ship contents display (right-click a fleet row) — panels measured

Pixel-edge analysis of row1_rightclick_game.png (640x480): strong column edges
at x 6/7, 307-330, 477-484, 633-634; row edges at y 2/4, 96-111, 283, 337-342,
473-477. Dark-blue panels occupy x 482-633 (full height 2..471) — the right
item list — and thin frame columns at 3-6 / 322-329 / 477.
Layout (vision): top-left panel = ship identity `Chamachies "Sparrowhawk"` +
three blue spheres + three red spheres + three gold bars; top-middle = enlarged
render of the SELECTED item ("Proton Shaver"); centre-left = big ship render in
a hangar; centre-right = equipped slots (THREE identical Proton Shaver renders);
bottom wide band = cargo hold renders; far right = item list.
Item list read top->bottom: Proton Shaver, Subatomic Scoop, Quark Express,
Van Crees Hypersplicer, Nanotwirler.

CROSS-CHECK vs VENDOR TABLE (extracted/ascend00/gizmos.txt, cr-stripped):
those five names are EXACTLY the category-4 block of gizmos.txt in file order:
  Proton^Shaver (line 169), Subatomic^Scoop (172), Quark^Express (175),
  Van^Creeg^Hypersplicer (178), Nanotwirler (181) — cat census: 76 gizmo
  records total = cat0 10, cat1 6, cat2 5, cat3 6, cat4 5, cat5 44.
=> [verified-by-correspondence] the contents-display right list is a
   CATEGORY-SCOPED gizmo list rendered in gizmos.txt file order, and category 4
   == GENERATORS (ships.md §6: "cat 4 generator -> +0x66 = POWER[+0x36]"),
   consistent with the top-middle selected-item being a power unit.
   Spelling note: live renders "Van Crees", vendor file says "Van Creeg" — the
   in-game string table is the authority for display, gizmos.txt for data; do
   NOT "fix" one to the other.

## SHIPDESSCREEN tab -> gizmo CATEGORY map: MEASURED 6/6 EXACT (the t253 core result)

Method: right-click fleet row1 -> contents display; click ONE tab per step
(window-rel coords); read the far-right GIZLIST names + the selected-item name;
compare against extracted/ascend00/gizmos.txt (cr-stripped) category field
(1st column of the parameter line) and file order.

| tab (windows.txt rect) | msg | live GIZLIST top->bottom | gizmos.txt cat | file count | verdict |
|---|---|---|---|---|---|
| WEAPONS 485,7-515,37 | 51 | Mass Barrage Gun, Fourier Missiles, Quantum Singularity Launcher, Molecular Disassociator, Electromagnetic Pulser, Plasmatron | 0 (weapon) | 10 | EXACT order |
| HULL 524,7-593,37 | 50 | (see below) | n/a | — | — |
| DEFENSES 602,7-632,37 | 52 | Ion Wrap, Concussion Shield, Wave Scatterer, Deactotron, Hyperwave Nullifier, Nanoshell | 1 (shield) | 6 | EXACT order |
| ENGINES 485,46-515,76 | 54 | Tonklin Motor, Ion Banger, Graviton Projector, Inertia Negator, Nanowave Space Bender | 2 (drive) | 5 | EXACT order |
| SENSORS 524,46-554,76 | 53 | Tonklin Frequency Analyzer, Subspace Phase Array, Aural Cloud Constructor, Hyperwave Tympanum, Murgatroyd's Knower, Nanowave Decoupling Net | 3 (scanner) | 6 | EXACT order |
| ENERGY 563,46-593,76 | 55 | Proton Shaver, Subatomic Scoop, Quark Express, Van Crees Hypersplicer, Nanotwirler | 4 (generator) | 5 | EXACT order |
| SPECIAL 602,46-632,76 | 57 | Lane Blocker, Molecular Tie Down, Intellect Scrambler, Brunswik Dissipator, Recaller, Disarmer (+ scroll arrows — 44 records) | 5 (special) | 44 | EXACT order |

CONSEQUENCES (the reason this matters):
1. CORROBORATES docs/re/ships.md §6 category dispatch independently of Ghidra:
   cat0=weapon, cat1=shield, cat2=drive, cat3=scanner, cat4=generator,
   cat5=special — six live UI tabs land on exactly the six categories the §6
   jump table (RAW at 0x49060) assigns, and the cat-4/ENERGY pairing matches
   the §6 "+0x66 = POWER[+0x36] (power supplied by the generator)" reading.
2. THE TAB->CATEGORY MAP IS NOT THE TAB ORDER AND NOT THE MESSAGE NUMBER.
   Measured permutation: msg 51->cat0, 52->cat1, 54->cat2, 53->cat3, 55->cat4,
   57->cat5, 50->HULL (no gizmo category). So SENSORS (msg 53) is cat 3 while
   ENGINES (msg 54) is cat 2 — the two middle messages are SWAPPED relative to
   category order, and msg 56 is assigned to no tab. Any rewrite that derives
   the category from the message number (or from tab index) is WRONG; the map
   must be a table. [verified by 6 live measurements + windows.txt rects]
3. The live table row count matches combat.md S2's static census: my gizmos.txt
   parse yields 76 records (10+6+5+6+5+44), the same 76 rows combat.md S2f
   measures at runtime 0x7650c stride 0x6a ("names byte-verified Mass Barrage
   Gun..Hyperfuel"). So gizmos.txt IS the vendor gizmo table the dispatcher
   reads — no re-derivation needed for the row set.
4. NAME SPELLING: live renders "Van Crees Hypersplicer" / "Brunswick
   Dissipator" where gizmos.txt says "Van^Creeg^Hypersplicer" /
   "Brunswik^Dissipator" (and one vision pass read "Deactottron" for vendor
   "Deactotron"). The vendor FILE is the data authority; vision reads are the
   noisiest instrument here (R13) — do not "fix" files toward what the
   projector appeared to say.

## HULL tab (the 7th): selection changes, gizmo list does NOT — MEASURED

Click HULL (558,22) while SPECIAL was the active category: 1973 px changed,
bbox x 524-632 y 7-76 == the tab-grid rows ONLY (GIZLIST starts at y 86). The
gizmo list area (y>=86) and the item-detail panel changed 0 px (selected name
stayed "Lane Blocker", cat 5). Vision on the 4x crop: the HULL tile (row 1,
middle = the ship silhouette, SHAPEFRAME 3) is now drawn darker/pressed.
=> LAW: a tab press always repaints the tab grid (selection highlight moves);
   the GIZLIST contents change ONLY for the six gizmo-category tabs. HULL is a
   hull-SIZE selector, not a gizmo category — matching help hull: "select a
   different hull size for the ship you are designing. Larger hulls provide
   more space and are more durable in combat, but take longer to build."
   (No hull-size list is rendered inside this window; STATE 1 8 has no other
   child, so the size choices must be drawn into the SHIPDESSCREEN canvas
   7,114-476,472 itself — the centre field that changed 0 px here. Unproven
   where the size rows live: NOTED, not claimed.)

## OQ-005 identification anchor (annotation, NOT a closure)

windows.txt SHAPEFRAME keys give the frame index of every tab tile inside
DATA\8SHIPDES.SHP: WEAPONS 2, HULL 3, DEFENSES 4, ENGINES 5, SENSORS 6,
ENERGY 7, SPECIAL 8 (GIZLIST SHAPEFRAME 7, SHIPDESSCREEN SHAPEFRAME 0). The
live tab art, read in grid order, is: row1 = explosion / ship silhouette / blue
orb; row2 = green crystal / magenta vortex / gold cylinder / pink beam+green
tip. Combining SHAPEFRAME with the MEASURED tab->category map above pins seven
8SHIPDES.SHP frames to seven semantic roles (weapon=explosion, hull=ship,
shield=blue orb, drive=green crystal, scanner=magenta vortex, generator=gold
cylinder, special=pink beam) — a concrete W3 eyeball target set for the codec
whenever R2 unblocks it. Codec itself stays blocked; OQ-005 stays OPEN.
