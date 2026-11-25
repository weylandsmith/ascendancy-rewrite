# _wip_tPF2.md — TILE POPUP CHAIN (D28 P3/P4/P5) — WIP

Task: STATE.md NEXT ACTION tPF-2. USER REFCAPS ARE AUTHORITY (they refute
our shipped two-step no-popup flow from tPL-B1b). Derive from windows.txt +
the planet-window msg map; port the t428 content-dependent popup law.

Sitting check ran FIRST: r1_t85g_sitting.py on the shared playcap dir RC=0
(work/r1/tPF2_pre_sitting.out) — relation snapshots run to t1273+, states
stable (t1254 one-turn alliance blip t1087-class), no new decisive event
requiring adjudication before this task; assignment stands.

## F1 — REFCAP READ [measured, vision on scratchpad PNGs]
- original-planet-screen-click-on-square-adjacent-to-structure.png:
  mineral-framed popup (~330x210, centered over the globe), title line
  "White Square", body "White squares are ordinary habitable surface
  squares.", BOTTOM BAR with TWO buttons "Build" (left) and "Cancel"
  (right) on a full-width strip.
- original-planet-screen-popup-after-clicking-non-adjacent-square.png:
  IDENTICAL frame/title-position/body ("Blue Square" / "Blue squares
  increase the effectiveness of research-producing structures.") but the
  bottom strip holds ONE centered "OK" button.
- => the CONTENT (title+body) is square-class driven; the BUTTON SET is
  context driven (adjacent-to-structure => Build+Cancel; else OK).

## F2 — STRING LAW CLOSED [verified, extracted/ascend00/static.txt]
getter(n) == nth quoted string (t96 law). Exact strings behind the refcaps:
 - #89 "%s Square"            (title template)
 - #91 "White squares are ordinary habitable surface squares."
 - #92 "Black squares are uninhabitable.  Most structures cannot be built on them."
 - #93 "%s squares increase the effectiveness of %s-producing structures."
 - colour nouns #75 White #76 Black #77 Red + #78 industry / #79 Green +
   #80 prosperity / #81 Blue + #82 research; #83 "Orbital".
 - buttons: #30 "OK"  #57 "Cancel"  #60 "Build".
Builder bodies (objdump work/ascend_restored.bin, GAP fn 0x3db80 msg-50
builder — same fn the tPL-B2 key-3 SQUARE case lives in):
 - 0x3de5a key-3 entry: cell = u16[widget+0xab]; >=0xffff -> 0x3e4db (no
   square lines); cell4 = [0x43508+0x10]+cell*4; item=BYTE[cell4+1].
 - 0x3df1f tail: cell >= planet+0x18 -> getter(83) "Orbital".
 - 0x3e1c7..0x3e2a1: cell-class = BYTE[cell4]&7:
     cell >= +0x18          -> getter(90) orbital text
     class==1 (WHITE)       -> getter(91) verbatim
     class==0 (BLACK)       -> getter(92) verbatim
     else                   -> sprintf getter(93) with colour noun +
                                producer noun (2/74/82 legs)
   title = sprintf getter(89) colour+" Square".
 - 0x3e12f: cell byte &8 (ruins) + owner==player -> getter(88) "Xenoarcheological
   Ruins" line (hold 0x14); build-progress lines getter(86)/(87) when a
   build is in progress on the cell (0x394d8+0x47010 legs).
 [all verbatim objdump'd this session; tPL-B2 _wip P3/P4 already banked the
  frame law: popup RECT = (wrec+10, wrec+10)..(wrec+0x145, wrec+0xcf)]

## F3 — WHICH PATH ARMS THE SQUARE POPUP [verified asm]
- The popup builder 0x3db80 dispatches on ds:0x74528 (key) via table
  0x28fb8; key 3 = SQUARE case. ds:0x74528 writers (full-image census,
  ONLY 3): 0x3d2b4 (init: fills 0x74528..0x7453c with static.txt 41..60 —
  NOT a key write), 0x3d811 (msg-50 arm, tPL-B2), 0x3dc48 (builder read).
- msg-1 leg of the PLANETALLOC handler 0x3d397: sets win+0x39/-1,
  win+0x35=-1, then `cmp ds:0x74528,3` — the SQUARE-key consumer leg.
- Paint body 0x3b96c (widget paint, msg-2 repaint path) reads the SAME
  fields: 0x3ba72 BYTE[widget+0xab], 0x3ba91 WORD[widget+0xac] (hover
  cell), calls checker 0x3830c per grid cell (0x3bab7/0x3c2da) and
  HIGHLIGHTS the hover cell when legal (0x3c2f1 cmp ebx==esi then
  0x61770 draw with style 4, gated on item==0xff and eax==-1).
  => the paint-side "valid location" highlight law (planet.txt info02)
  is HERE — honest negative: no direct store of key=3 found statically
  (t333 (2): composition is parse-time; static invisibility is by law,
  the jump table at 0x28fb8 is relocated code). The D28 refcaps are the
  LIVE witness that a tile click arms key=3 with cell=widget+0xab.
- Button-set law [inferred from refcaps + strings, seam named]:
  Build+Cancel iff the cell could host a build (adjacent-to-structure
  per planet.txt info02 "Squares adjacent to existing structures ...
  indicate valid locations" + refcap P3); OK otherwise. Cancel/OK both
  dismiss. Build -> opens the build list (the PLBUILD list window) with
  the cell ARMED so the list pick lands as rec+0xb2 (the tPL-B1b order
  step-2 path then orders on the cell click).

## F3b — SQUARE-CASE CONTENT LAW, FULL [verified objdump 0x3de5a..0x3e2c8]
Entry 0x3de5a: cell=WORD[widget+0xab]; <0 -> 0x3e4db (no lines).
cell4 = [0x43508+0x10] + cell*4; item = BYTE[cell4+1].
1. COLOUR/PRODUCER words (0x3dedb..0x3df1f): default +0x66=getter(75)
   "White"; table cs:[0x28fa4] on BYTE[cell4]&7 (ja>4 skips):
   BLACK -> getter(76); RED -> getter(77)+getter(78)"industry";
   GREEN -> getter(79)+getter(80)"prosperity"; BLUE -> getter(81)+
   getter(82)"research". cell >= planet+0x18 -> +0x66 = getter(83)
   "Orbital" (0x3df34). Class map agrees with tileEdgePaletteIndex law
   (0 black, 1 white-default, 2 red, 3 green, 4 blue).
2. ITEM LINE (0x3df46, item != 0xff): name = planitem record +0xa
   (stride 40, 0x73e40 base); Ship item 23 appends race via 0x396cc +
   fmt 0x1fea; automated = WORD[cell4+2] bit1 (0x3dfbf and al,2) ->
   getter(84)"Automated " else raw 0x1ff2; composed with getter(85)
   " on %s Square" (0x3e026 sprintf chain); pushed hold 0xf; then
   word+2 != 0 -> EXIT (0x3e078 jne) — an occupied cell shows ONLY the
   item line. [port seam: race-append + Automated prefix not modelled —
   campaign has no per-item automation flag.]
3. EMPTY-CELL PROGRESS LINE (0x3e07e..0x3e125): 0x394d8(0xff, ind/day
   +0x44, buildAcc +0x50) -> 0x47010; 0xffff -> getter(86)"No progress"
   else sprintf getter(87)"%d day%s until completion"; hold 0x32.
   [port seam: NOT rendered — the D28 refcaps show title+body only;
   queue-consumer order unrecovered (TPLB2 seam family).]
4. TITLE (0x3e12f): BYTE[cell4]&8 (ruins) && owner==player(0x7458e) ->
   getter(88)"Xenoarcheological Ruins" as the LINE, and 0x3e1c1 jne ->
   NO BODY. Else sprintf getter(89)"%s Square" colour. Push hold 0x14.
5. BODY (0x3e1c7..0x3e2c8): cell >= +0x18 -> getter(90) orbital text;
   class==1 -> getter(91) WHITE verbatim; class==0 -> getter(92) BLACK
   verbatim; else sprintf getter(93)"%s squares increase the
   effectiveness of %s-producing structures." colour+producer.
Refcap agreement: "White Square"/#91 and "Blue Square"/#93-research are
EXACTLY the refcap texts (vision oracle this session).

## F3c — BUTTON LAW [refcap authority + seam-named inference]
Adjacent-to-structure popup (P3 refcap) -> bottom strip "Build"(getter60)
+ "Cancel"(getter57); non-adjacent (P5 refcap) -> single "OK"(getter30).
Gate [inferred, planet.txt info02 "Squares adjacent to existing
structures ... indicate valid locations" + the checker adjacency leg
0x385b7..0x386fc already ported]: Build iff cell is a SURFACE cell,
EMPTY (no active item), with an ACTIVE NEIGHBOUR. Occupied/ruins/orbital
-> OK only (no refcap; honest default, seam-named). Build opens the
build list with the cell ARMED (pick orders on that cell directly —
merges the refcap flow with the msg-0x1c01 step-2 law). Cancel clears
cell+popup; OK clears popup.
Popup RECT: same builder law (F2 frame), clicked widget = PLSQUARE
(152,120,487,375) windows.txt ln1519 -> indicatorPopupRect =
(162,130)..(477,327). Arm composition key=3 statically invisible per the
t333 (2)/(4) laws; the refcaps are the live witness.

## F4 — PORT LANDED (code + pins) [verified by build+suite]
 - indpopups.{h,cpp}: squareBuildable (surface+empty+active-4-neighbour)
   + squareInfoLines (title/body class table, ruins leg, orbital leg,
   holds 0x14/0x50) — law F3b/F3c verbatim.
 - ui.cpp: tile click WITHOUT pick now ARMS the square popup
   (planetSquarePopup + rect = indicatorPopupRect(PLSQUARE 152,120) =
   (162,130)..(477,327)); popup BUTTON STRIP below the text rect
   (y1+2..+30): Build (left quarter) opens PLANLIST with the cell ARMED
   (planetCellArmed) so the list pick orders on that cell via the
   msg-0x1c01 step-2 arms; Cancel clears cell+popup; OK dismisses. The
   msg-50 indicator popups keep planetSquarePopup=false (no buttons).
   Fresh-open + panel + pick arms clear the square flag.
 - pins tests/test_squarepopup_tpf2.cpp (2 tests, CMake wired): content
   law all 5 classes + ruins + orbital + out-of-domain; button law
   empty/occupied/neighbour/far. Suite 543->545/0/0.
 - LOG LINES: "ui planet tile N selected (<Title> BUILD| OK)",
   "ui planet popup build cell N" / cancel / ok,
   "ui planet project <planet> <item> (ordered|rejected armed cell N)".

## F5 — LIVE WITNESS [INCOMPLETE — carried to next iteration]
 - scripts/tPF2_witness.sh written (probe lattice tile centres via the
   tPL-V1 center law until a BUILD cell and an OK cell are found; then
   Build->list->armed-order and OK->dismiss paths; PID-only kill law).
 - Attempt 1: app reached planet view ("ui status select Amoroso I ->
   planet view (state 17)") but the probe clicks never produced a
   "ui planet tile" line and the app died (X connection broken) before
   any shot. NOT a refutation — the click path was never witnessed.
   NEXT iteration: re-run the script; if clicks still don't land, check
   xsend timing vs the screen-swap (the planet view opens ~1 s after the
   row click; the tPL-B2 witness slept 1 s and worked, so suspect the
   probe-loop's first click racing, then the winpos/import failure
   killing Xvfb via a stale lock).
 - Unit-level verification IS real: 545/0 suite incl. the two new pins.
- Tile click WITHOUT pending pick (existing arm at ui.cpp ~:997 that only
  sets planetCell): ALSO build the square-info popup lines via a NEW pure
  fn squareInfoLines(cellClass, isOrbital, ...) in indpopups.{h,cpp}
  (same file as the msg-50 builder law) — title getter89 + body
  getter91/92/93/90 verbatim; button set per F3.
- Tile click WITH pending pick: keep the tPL-B1b order path (msg 0x1c01
  law stands for the ORDER step; the popup refutes only the no-pick
  silence).
- Build button -> open project list with cell armed; pick -> order on
  that cell (reuse orderProject path). Cancel/OK -> clear planetCell +
  popup.
- Pins: squareInfoLines class table (all 5 classes incl. orbital),
  button-set gate, verbatim strings. Witness: scripted walkthrough both
  paths (adjacent => Build/Cancel lines + order lands; non-adjacent =>
  OK only).

## F6 — tPF-2b LIVE WITNESS PASS (2026-11-25, attempt 3)
- ATTEMPT-1 ROOT CAUSE (MEASURED): the probe loop walked offsets around
  tileCenter(size,row=0,col=0)=(410,127). For size class 2 the vendor grid
  (planitem.txt B/C tokens, economy.cpp tok 45..194) has ZERO valid cells
  in rows 0..3 — C[size2]=rows4..10 (1 4 4 5 4 4 1), centres y 212..382.
  All 15 probes hit empty space -> tileHitFor -1 -> zero 'ui planet tile'
  lines. NOT an app bug, NOT an X race: the app stayed alive the whole
  time ("X connection broken" = our own kill at script end; xsend's
  "window died before release" is a benign artifact of its press/release
  loop — it prints for EVERY click).
- FIX: probe enumerates REAL cell centres from the B/C tables (embedded in
  scripts/tPF2_witness.sh) keyed off the app's own 'home-cb ... size S'
  line; plus a need() guard that fails loud if navigation doesn't land.
- WITNESS LOG (seed 5, /tmp/tpf2_shots/app.log):
    tile 2 (White Square OK) / tile 5 (Black Square BUILD)
    'ui planet popup build cell 5' -> PLANLIST open -> row 0 pick
    'ui planet project Amoroso I Factory (ordered armed cell 5)'
    re-click tile 2 -> 'ui planet popup ok'
- SHOTS (vision-checked): popup-build.png = "Black Square"/"Black squares
  are uninhabitable.  Most structures cannot be built on them." + Build |
  Cancel strip, white outline on the selected tile; popup-ok.png = "White
  Square"/#91 text + centred OK; after-pick.png = NO popup + Factory art
  on cell 5 next to Colony Base + PLBUILD panel shows "Factory".
  MATCHES the D28 P3/P5 refcaps (title+body+button strip law).
- VERDICT tPF-2 chain: WITNESSED PASS.

## F7 — PLANLIST ART DELTA (tPF-2 remainder) — refcap measured
- scratchpad/original-planet-screen-build-list.png (vision oracle):
  * each row = isometric ART thumb (planitemLib record, same art as the
    tile blit) at LEFT, name text to its right, NO cost column visible;
  * SELECTED row = TEAL full-width band (Factory top row in refcap);
  * SCROLL ARROWS: up/down buttons at the RIGHT edge (up at list top,
    down at list bottom), mineral-framed triangles in small boxes;
  * rows are widely spaced (~60px pitch, 4 visible in the refcap window
    which spans roughly the PLBUILD column area) — our 24px pitch and
    12 rows is a PORT default seam (planetview.h kProjectRowPitch).
- ours (list-open.png): text-only rows "Name   cost N", no art, no teal,
  no arrows. planitemLib is already loaded in ui.cpp (tile art) — blit
  record == itemIdx per the t428 1:1 law.

## F8 — PLANLIST ART LANDED + WITNESSED (tPF-2b close, 2026-11-25)
- PORT (planetview.h/.cpp + ui.cpp): row pitch 24->72, visible 12->4
  (refcap-measured, F7); arrow column x>=482 owns the right edge
  (projectRowFor refuses there); rows paint planitemLib record==itemIdx
  art thumb left + name right, cost column DELETED (none in refcap);
  TEAL band rgb(16,69,77) (refcap-measured over navy rgb(12,32,48)) on
  the hover row (SDL_MOUSEMOTION -> projectHover) or the committed pick;
  framed up/down vector arrows (t407 precedent) at (482,125..157)/(482,
  388..420); click arms scroll projectFirst +-1 clamped to n-4.
- MUTATION CAUGHT BY THE WITNESS: first arrow draft drew BOTH boxes
  v-shaped (widen-with-y in both branches inverted the up triangle);
  zoomed vision check caught it, fix = narrow-at-pointed-end, re-ran.
- WITNESS run3 (seed 5): full chain + 'project-list scroll down 1' +
  'scroll up 0' + ordered armed cell 5 + popup ok; shots list-hover.png
  (art + teal band row 1 + arrows) and list-scrolled.png (rows 1..4);
  arrow zooms confirm up-triangle up, down-triangle down.
- PINS: squarepopup_planlist_geometry_tpf2b (pitch/visible/arrow-column/
  disjointness/first-thread). Suite 545 -> 546/0/0.
- tPF-2 FULLY CLOSED (law+port+pins+WITNESS+refcap art). Remaining
  honest seams: selected-row band colour is the MEASURED rgb but the
  vendor's selection-vs-hover distinction is unrecovered (port bands
  both); arrow chrome is vector (no vendor arrow art identified); row
  pitch 72 is a single-refcap measurement (one capture scale 0.825).
