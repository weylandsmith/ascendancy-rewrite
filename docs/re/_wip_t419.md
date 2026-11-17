# t419 WIP — RESEARCH SCREEN: CPU STALL FIX + 3D TREE REBUILD + CORNER EXIT (2026-11-17)

## F0 Context (control plane read)
- Assignment docs/STATE.md:233-259 (queue row ~1492). Phase 15, D15 addendum
  (DECISIONS.md:384-410) is the user spec: screen pegs one core, input/close
  queue MINUTES ("ui research readout Orbital Structures" console spurt),
  "another 3d rotating dealie" + info frame right + controls lower right
  (rotation about Z + scroll up/down), "derive the rendering from RE".
  Corner "Exit <ESC>" popup (D15 DECISIONS.md:354-383: census the shp libs).
- No new sitting: live-timeline.jsonl mtime 2026-11-12 06:45 predates HEAD
  (f3302aa, 2026-11-17). Assignment stands.

## F1 STALL ROOT CAUSE (static-cited, confirmed by read this session)
- researchview.cpp:99-125 researchDepth(): `static thread_local memo;
  memo.clear();` then re-walks ALL mainCount rows (66) with the DFS stack
  EVERY call. Cost per call ~ O(n x edges).
- researchview.cpp:127-138 researchNodePos(): calls researchDepth(row) once
  PLUS researchDepth(r) for every r < row => O(n) memo-full-walks per node.
- ui.cpp paint (kScreenResearch block ~1731-1800): researchNodePos per node
  (66) + per prereq edge, EVERY frame; SDL_WaitEventTimeout(16) loop
  (ui.cpp:398) => ~60 fps x O(n^2 x graph). ui.cpp:601-615 researchHit
  repeats the sweep per click (and researchHit itself calls
  researchNodePos per node = O(n^2) inside one click).
- => one core pinned painting the research screen; queued events drain in a
  burst when the loop finally yields = the observed console spurt + "trapped,
  Esc doesn't work" (reclassified per D15 addendum).

## F2 FIX LAW (port, labelled)
- Add researchDepthTable(tree) -> vector<int> (one full memoised pass,
  O(n+e)); researchNodePosAt(depths, row, panX, panY) pure pure offset fn.
- researchNodePos(tree,...) keeps its signature (pins) but delegates to a
  table built ONCE per call (still O(n+e) per call, not O(n^2 x graph)).
- ui.cpp + researchHit build the table ONCE per frame / per click and use
  researchNodePosAt. Frame-budget pin: full-tree position pass < 5 ms
  steady_clock inside the test.

## F3 3D REBUILD (reuse t416 Camera3d basis API)
- t416 SEAM law (cam3d.h:6-49): dials LATCH (pressSpin/pressTilt/pressZoom,
  dialLatch law), pump tick() applies deg-rotations about WORLD axes on the
  basis; NO yaw/pitch fields. Research buttons msg 50..53 == cosmos dial
  msgs 50..53 (windows.txt verbatim) — same control family.
- Mapping (user D15 verbatim + t408 pan law): ROTLEFT/ROTRIGHT (msg 50/51)
  -> pressSpin(+1/-1) turntable; MOVEUP/MOVEDOWN (msg 52/53) -> SCROLL
  (resPanY), NOT tilt (user spec: "scrolling (up/down)").
- Tree field: x = depth column, z = slot row (XZ plane, the t416 cosmos
  plane mapping), y = scroll. Projection = t399 pinhole (cam3d.h:39-40
  FUN_00053374 law) via a generic projectPointCam helper; research standoff
  = port default sized so the rest bbox fits the RESWIN interior (labelled).
- Depth -> scale/brightness: pinhole scale focal/Z; dim ramp reuses the
  t411 depthDim posture (port default, labelled).

## F4 CORNER EXIT POPUP
- Art EXISTS and DECODES: mouse.shp k4..k7 = ONE 78x47 "Exit <ESC>" glyph at
  four screen-corner anchors (t344 S27; t367 S28 corner-anchor fallback in
  shp.cpp:149-160 decodes k5/k6/k7; D1 ruling KEEP; _wip_d1page.md: planes
  byte-identical md5 b2d049bbf5b5, white+lime text, beveled frame).
- Port law: track SDL mouse motion; cursor inside a kCornerProbePx box at
  any screen corner -> blit the glyph inset in that corner; leaving clears.
  Esc already unwinds (t410 chain law) — the popup is the affordance hint.

## F5 pins / witness plan
- tests/test_researchview_t419.cpp: depth-table == per-row researchDepth
  equivalence (all 66 rows); nodePosAt vs nodePos equality; frame-budget
  < 5 ms; 3D projection rest-basis equality with 2D law where z=0 plane;
  corner hit law pure fn (cornerFor / glyphRectFor).
- Witness: scripts/r1_ui_walk.sh research shots t419-*.png + ps -o pcpu
  sampling during the research screen (must NOT peg) + own-eyes grade (D13).

## F6 DESIGN (locked this session, pre-edit)
- RE LEG HONEST NEGATIVE FIRST: grep of on-disk disasm windows + docs for a
  reswin/ressearch paint chain finds NONE (the rotation engine t416 recovered
  lives in the COSMOSWnd family 0x27a18/0x283e4/0x53xxx; the reswin draw
  chain was never in a captured window). Port therefore reuses the t416
  BASIS API verbatim (pressSpin latch + pump tick, 2 deg/tick) on a flat XY
  tree field — NAMED SEAM (vendor reswin draw law unrecovered; user spec
  "derive from RE" satisfied only at the mechanism level).
- STALL FIX: researchDepthTable(tree) ONE memoised pass (depth[] + slot[]);
  researchDepth()/researchNodePos() delegate (signatures kept — t408 pins);
  ui.cpp paint builds the table ONCE per frame + ONE position per node;
  researchHit builds it once per click (new optional cam arg).
- 3D LAW (port, labelled): field coords F = (pos2D - bboxCentre, -(y-yC), 0)
  px units; projectPoint(cam,F,kResStandoff=1200) with resCam.focal=1200 ->
  ratio EXACTLY 1 at rest => rest projection == t408 2D law EXACTLY
  (pins + t408 witness click coords survive); spin pair msg50/51 ->
  resCam.pressSpin(+/-1) (t416 latch+pump); move pair msg52/53 -> resPanY
  scroll POST-projection (user spec "scrolling up/down"; t252 diff law kept
  as vertical); pressZoom unused (no research zoom buttons windows.txt).
- CAMERA GENERIC: cam3d.{h,cpp} gain projectPoint/pointDepth(x,y,z,standoff);
  projectStar/viewDepth refactored to call them (identical math).
- POPUP: NEW pure module ui/exitpopup.{h,cpp}: exitCornerFor(px,py,w,h,probe
  =24 [port default labelled]) + exitPopupRect (78x47 glyph INSIDE corner).
  Art [verified shp.md S27/S28 + _wip_d1page.md]: mouse.shp k4..k7 ONE
  78x47 "Exit <ESC>" glyph at four corner anchors, planes byte-identical
  md5 b2d049bbf5b5; k5 decodes via the t367 fallback -> blit record 5.
  POLLED via SDL_GetMouseState in the paint loop (title.cpp:315 precedent;
  synthetic MotionNotify is REJECTED by SDL per tools/xsend.c header — the
  warp still moves the pointer so xsend-driven witnesses work). Log
  "ui corner exit popup shown/hidden" on transitions. Esc = t410 chain law.

## F7 LANDED (this session, measured)
- Code: cam3d.{h,cpp} generic projectPoint/pointDepth (projectStar/viewDepth
  refactored onto them, identical math); researchview.{h,cpp}
  ResearchLayout one-shot (depth+slot+bbox centre), researchNodePosAt,
  researchNodeScreen (3D flat-XY field, rest scale EXACTLY 1), researchHit
  on PROJECTED centres (cam arg defaults to researchRestCam — t408 pins
  compile+pass unchanged); ui/exitpopup.{h,cpp} new pure module
  (exitCornerFor probe 24px [port default], exitPopupRect 78x47 tuck);
  ui.cpp: resCam (focal==kResStandoff==1200, bounds kResWin) + pump
  (kSpinTickMs), rotate dials pressSpin(+/-1) [t416 latch], move pair
  scrolls resPanY, painter ONE layout + ONE screen pass + depth-sorted
  paint + scaled rings; corner popup polled via SDL_GetMouseState, glyph
  mouse.shp k5 (t367 corner-anchor fallback record), transition log
  "ui corner exit popup shown/hidden".
- PINS tests/test_research3d_t419.cpp x4 suites: layout==OLD-law oracle for
  ALL rows; rest 3D equality EXACT (x,y,r==30) + scroll exact + spin moves
  view with z2 spread + dialLatch stop law + hit-map follows rotation;
  FRAME BUDGET: 60 new-law full passes 122 us (2.0 us/frame) vs OLD-law ONE
  frame 2160 us -> CHECK(old > 10x new-second) self-contained class proof;
  corner law corners/edges/interior + rect tuck. Suite 417->421/0/0, 0
  warnings.
- WITNESS scripts/t419_research3d_witness.sh VERDICT 5/5 PASS: study click
  lands at rest coordinates ("ui research study Spacetime Surfing"); popup
  shown+hidden lines present; Esc returned in 204 ms (D15 stall was
  minutes); CPU delta 138 ticks/4 s = ~35% of one core (painter ~60fps
  SDL path), NOT pegged; ps pcpu 14.7-15.3 across window.
- NATIVE-VISION GRADE (D13, own eyes): research-open.png = header "Player
  Knowledge" green centred, ~21 ring nodes + blue prereq lanes, 4 arrow
  boxes lower right, right panel blank with no project (t268 law);
  research-spin1.png = mid-spin PERSPECTIVE arrangement (non-axis-aligned,
  foreshortened columns), gold Study ring top-left, right panel live:
  "Current Project: / Spacetime Surfing / (0 days) / Allows / Star Lane
  Drive" — the 3D rebuild and info frame read correctly. PASS.
- RE LEG: honest negative banked (F6) — no reswin draw-chain FUN in any
  on-disk disassembly window; Ghidra defined-strings table returns 0 even
  for known-present strings (20res) this session -> mechanism reuse of the
  CITED t416 cosmos basis is the shipped law, seam named in researchview.h.
- LEDGER: closes NOTHING (strict-close honest negative — D15 chrome rows
  have no OQ owner; t414..t418b precedent).
