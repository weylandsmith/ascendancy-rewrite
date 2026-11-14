# _wip_t388 — IN-GAME MENU BAR + STATUS WINDOW CHROME

Assignment: STATE.md NEXT ACTION t388. STATUSWND (windows.txt) as campaign
screen chrome + rail buttons per cited rects; screen-switch law for map
return; Save/Load reuse t387 windows; frame+title only for the rest.

## Cited geometry re-measured this session (windows.txt parse, 132 records)

Top-level state map (STATE field = list of state ids the window is active
in; TYPE-100 blocks map STATENUMBER->SHAPEFILE):

- state 1 = starmap (COSMOSWnd STATE "4 1 3 7 13", 7,7-465,472)
- state 10 = STATUSWND (16, PARENT NONE, STATE "1 10", 7,7-632,472,
  SHAPEFRAME 0, HELPINDEX statwnd) + child STATPLANLST (TYPE 10, PARENT
  STATUSWND, STATE "1 10", 7,46-632,472, SHAPEFRAME 7, HELPINDEX statwnd)
- state 18 = FLEETWND (7,7-632,472), state 20 = RESWIN (7,46-476,472),
  state 14 = INTELSCREEN (7,7-632,34 header), state 7 = race select
  (RACE_1..RACE_7 474,7.. + Intelligence 474,303-632,333)
- TYPE-100 SHAPEFILE map (verbatim, 8 screens + TESTDLG):
  0=0OPENING.SHP 1=1STARMAP.SHP 3=3CFGNEW.SHP 7=7RACESEL.SHP
  8=8SHIPDES.SHP 13=13NEGOT.SHP 16=16BATTLE.SHP 20=20RES.SHP
  NOTE: NO TYPE-100 names 10status.shp — state 10's library is named by
  the task's evidence base (chrome shape libs dir), [inferred] k0 backdrop
  role, same class as 4loadgam (t387).

## HONEST NEGATIVE #1 (binding for this row)

The t388 task text lists rail buttons "Galaxy/Species/Intelligence/
Research/Production/Design/Save/Load". windows.txt contains NO button named
Galaxy, Production, or Design anywhere. The CITED campaign rail (STATE
"1 1", all PARENT NONE, x-band 474) is SIX buttons + turn controls:

  STATUS      474,130-632,160  msg 1 p1 10  help 1plan
  FLEET       474,169-632,199  msg 1 p1 18  help 1ships
  RESEARCH    474,208-632,238  msg 1 p1 20  help 1res
  SPECIALAB   474,247-632,277  msg 5 p1 0   help 1special
  RACES       474,286-632,316  msg 1 p1 7   help 1races
  Intelligence 474,303-632,333 msg 1 p1 14  help inteli  (STATE "1 7"!)
  TURNCOUNT   474,7-632,43     frame 65
  NEXTTURN    474,52-548,82    msg 7        (NEXTTURNCONT 557,52-632,82 msg 8)

SAVE (159,360-477,390 msg 1 p1 4) and LOAD (159,400-477,430 msg 1 p1 2)
exist ONLY in STATE "1 0" (the title menu), NOT on the campaign rail.
Ship design = SHIPDESSCREEN state 8; production/colonies = PLANETALLOC
state 17 — neither is a rail button. Vendor table wins over task prose:
the port lands the SIX cited buttons; Galaxy/Production/Design are named
absences, not invented rects.

## Screen-switch law (cited shape, t264 generalisation)

SENDMESSAGE 1 + SENDPARAM1 = target STATE number holds for the four rail
window-openers (10/18/20) + RACES (7) + Intelligence (14) — t264 verified
10/18/20/14; this session re-reads the same table incl. p1 7 for RACES.
msg 5 (SPECIALAB) and msg 7/8 (NEXTTURN/CONT) are NOT screen switches.
param1 with no known STATE id -> no-op (no clamp, no guess).

Visibility law: a window draws iff its STATE list contains the current
state id. Consequence [verified from the table]: the rail buttons' STATE
"1 1" does NOT include 10/18/20/14 — on the vendor screen-switch the rail
is NOT active inside the opened screen; STATUSWND (STATE "1 10") is active
BOTH on the map (1) and on the status screen (10) — it is full-screen
chrome behind the cosmos map, not a bottom bar (task prose "bottom bar" is
refuted by the rect; the map 7,7-465,472 sits inside it).

## 10status.shp census (scripts/r388_status_census.py, V/A law imported
## verbatim from scripts/r1_shp_unifiedlaw.py — no re-implementation)

  rec  tag  W    H     span            opaque  skiprows
    0  V    639  479   [0x28,0x54a8)   306081  0
    1  A    32   31    [0x54a8,0x5847)   749   0

k0 is FULLY OPAQUE (306081 = 639*479 exactly; zero skip rows) — it is a
full-screen backdrop, consistent with STATUSWND rect 7,7-632,472 being an
independent screen, not a bar. k1 32x31 = a small inset. Control: same run
censused the rail icon frames 1starmap k3 43x22 X, k4 44x23 X, k5 44x27 A,
k7 45x30 A (all decode; icon law records ui-runtime.md §6a).

## STATE-field COUNT LAW [verified, 123/123 records]

STATE = "<count> <id>...": the leading integer EQUALS the number of state
ids following it in all 123 records that carry STATE (0 violations, parsed
this session over extracted/ascend00/windows.txt). CONSEQUENCE —
CORRECTION to the section above: rail buttons' STATE "1 1" = active in
state 1 ONLY; Intelligence's "1 7" = active in state 7 (the species menu)
ONLY — NOT in both, and not on the map. STATUSWND "1 10" is active in
state 10 ONLY (the earlier "both" reading in this file was wrong). This
matches t252's live dossier ("hidden until Species menu?"; the
Intelligence click that opened INTELSCREEN was made FROM the species
menu). This law is what makes the screen-switch safe: SENDPARAM1 is a
state ID and a control/window draws iff its STATE id-list contains the
current ID.

## Sibling chrome libs (same census run)
2savegam.shp N=1 k0 639x479 V (same full-backdrop class as 10status/4loadgam)
20res.shp    N=6 k0 15x30 V   | 7racesel.shp N=8 k0 158x30 V  (row art, not backdrops)

## Screen-switch law landed (pure module rewrite/src/ui/statuslaw.{h,cpp})
- screenAfterRailPress(cur,msg,p1): msg==1 && p1 in {1,7,10,14,18,20} -> p1,
  else cur (no clamp). Known-set gate: jumping to a state with no chrome in
  the port is a no-op, never a blank screen.
- msg 5 (SPECIALAB) and msg 7/8 (NEXTTURN/CONT) are NOT switches (table).
- Escape: inside a screen -> state 1 (map) [verified t252 live: "Escape
  returns to galaxy", ui-runtime.md §6b]; on the map -> quit (existing law).
- Rail buttons STATE "1 1" do NOT include 10/18/20/14/7: inside an opened
  screen the rail is INACTIVE (drawn dimmed, clicks inert). Escape is the
  cited way back.
- Screen titles = the verbatim TEXTITEM labels of the opening button
  (Planets/Ships/Research/Species/Intelligence + Research screen header
  format "<Race> Knowledge" t252 — race interpolation = seam, generic
  "Knowledge" shipped).
- HONEST NEGATIVE #2: vendor SAVE/LOAD buttons exist ONLY in STATE "1 0"
  (title menu). The campaign rail has NO save/load control. Port-side
  reuse: Alt-L in the campaign opens the t387 load screen (labelled port
  addition, not vendor law); Alt-S prints the save seam line (no campaign
  writer exists; Observer is read-only by contract t382).

## Right-click deselect (selfplay.md): LANDS where hitStar selection exists
(ui.cpp map branch, screen==1). No selection widget this row — noted, not
implemented, per task text.
