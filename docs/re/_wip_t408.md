# t408 WIP — RESEARCH SCREEN (D13 "research is empty" + "can't select a technology")

## F0 PREMISE + CONTROL PLANE
- Assignment: docs/STATE.md NEXT ACTION t408 (queue row STATE.md:1040-1045).
- Sitting check RING-FIRST: t368_ring_turn parsed=20/20 max_turn=1254 -> no new
  play, assignment stands. Tree clean at launch (d2fbaef).
- PRE-FLIGHT (owed by t407 F13): scripts/t407_mutate.sh RE-RUN. TWO bugs found
  by read + measurement (NOT just the cwd bug STATE.md named):
  (1) THE REAL VACUITY: run() grepped 'fleetlist.*FAIL' but harness.h:52 prints
      'FAIL <file>:<line>' — FAIL comes FIRST, so the grep could NEVER match;
      every mutant would read SURVIVED even with a correct cwd. Verdict is now
      the run_tests EXIT CODE with the 'fleetlist' substring filter
      (./run_tests fleetlist -> 8 tests in 0.010s — filter measured).
  (2) cwd: consumers now absolute ($ROOT/...); build dir mkdir -p.
- REFUTED-ROUTES: 'research' grep = 3 hits, none binds a rewrite-side window
  (R6 gam_probe truncation; t326/t331 research-leg re-reads = capture-side).
  t326 research leg stays do-not-re-trod (mask census, vacuous) — this task is
  the WINDOW, not the capture.

## F1 INHERITED PORT STATE (measured by read)
- kScreenResearch exists; ui.cpp:781 maps it to kResWin rect and draws header
  strip + generic vector interior ONLY — zero content, zero hit-map (the D13
  symptom, same shape as t405/t406/t407 pre-fixes).
- THE ENGINE SIDE IS ALREADY COMPLETE (unlike t407's census problem):
  Campaign holds ownedTech[o] (vector<bool> by Tech id), queuedTech[o] (id or
  -1), techProgress[o] (double), res[o] stockpile; researchPhase()
  campaign.cpp:1425-1484: player pick = cheapest runtimeCost (tie -> lowest
  row) ONLY when queuedTech<0 || already-owned; techProgress += res, res=0;
  completion at runtimeCost -> owned + event + queue cleared.
  Accessors EXIST: playerTechs() campaign.h:298, isTechQueuedFor/:473,
  techRowOwnedFor/:474, setQueuedTechFor/:475 (law-pinning hook — the click
  path can reuse it), resources(owner) :2269, tree via Campaign (tree_).

## F2 VENDOR WINDOW LAW (windows.txt cited this session)
- STATE 20 IS THE RESEARCH SCREEN: TYPE-100 L1755-1758 binds DATA\20RES.SHP;
  RESWIN TYPE 9 rect 7,46-476,472 STATE "1 20" (t388's known-id set already
  includes 20? -> check statuslaw kScreenResearch value).
- FOUR CHILD BUTTONS (all STATE "1 20", MOUSEFOCUS 1, SENDPARAM1 999):
  RESROTLEFT   524,442-539,472 SHAPEFRAME 0 msg 50  (rotate tree left)
  RESROTRIGHT  540,442-554,472 SHAPEFRAME 1 msg 51
  RESMOVEUP    563,442-593,457 SHAPEFRAME 2 msg 52
  RESMOVEDOWN  563,458-593,472 SHAPEFRAME 3 msg 53
  -> the tree view is a PAN/ROTATE viewport, not a flat list. 20res.shp EXISTS
  on disk (extracted/ascend01/data/20res.shp) — unlike fleet, chrome art real.
- help reswin (help.txt:1668-1690 verbatim): "Disks containing pictures
  represent technologies you have discovered, and empty disks represent
  technologies you can choose to study. @@You can click on an empty disk to
  make it your current topic of study." -> THE SET LAW is vendor-documented
  prose: click empty disk (available tech) -> current study.
- rail RESEARCH button: windows.txt L437-456 rect 474,208-632,238 msg 1 p1 20
  (screen switch per t388 screenAfterRailPress — already works).

## F3 DATA LAW (banked, reuse — do NOT re-measure)
- restree 66 main rows live (OQ-013 CLOSED, research.md §6c); runtimeCost law
  §6b (file cost x (2*row-20) row>10 clamp 65000) — rewrite Tech::runtimeCost.
- prereqs fields[2:-1]; available() = not owned && all prereqs owned.
- static.txt getter index law: marker-driven '// N' reader (F10 fleet-screen).

## F4 SCOPE (locked, mirrors t402/t407 shape)
(a) ui/researchview.{h,cpp} PURE: rowsFor(Campaign, tree, owner) partition
    owned/available/blocked (prereq-missing), current study + progress
    (techProgress vs runtimeCost), setStudy law (click available -> queued;
    click owned/blocked -> NO-OP silent), geometry (viewport pan per the four
    buttons: rotate = horizontal, move = vertical), hit map.
(b) ui.cpp: research screen paints the partition + current study + progress
    bar; click sets study (log 'ui research study <name>'); arrows pan; Esc.
(c) pins test_researchview_t408.cpp (REUSE marker-driven static reader if any
    static.txt text is asserted; REQUIRE_DATA() on every data-reading test —
    t403 law); headless assertion: set study -> turn-end resolves (queue row's
    named closer).
(d) witness scripts/t408_research_witness.sh (Xvfb, boot -> rail Research ->
    click an empty disk -> log line -> next turns -> researched event).
NAMED SEAMS (not invented): 20res.shp disk-art registration (decode + conflict
census if budget; else honest-vector disks WITH the help reswin citation), the
vendor tree LAYOUT (which tech sits where; the pan buttons prove a viewport but
the layout record is uncited), rotate semantics beyond 'pan'.
NO OQ ROW CLOSES (strict-close; D13 chrome has no OQ owner — same honest
negative as t405/t406/t407).

## F5 PRE-FLIGHT RESULT — t407 MUTATION CAMPAIGN RE-RUN (real run, exit-verified)
scripts/t407_mutate.sh fixed + run from repo root: M1 CAUGHT (named FAIL lines
fleetlist_t407.cpp:224/225/226), M2-M6 CAUGHT rc=1 (grep -E '^ *FAIL ' shows the
harness indents FAIL lines with leading spaces — M1's lines prove the grep
works; M2-M6 rc=1 is the exit-code verdict), final rebuild 368 tests 0 failed,
MUTATION CAMPAIGN DONE fails=0. THE t407 PINS ARE NOW PROVEN, NOT JUST GREEN.
fleet-screen.md F13 updated accordingly.

## F6 VENDOR SCREEN LAW — NATIVE-VISION GRADE OF THE BANKED CAPTURES (D13 policy)
work/screens/t268/reswin_game.png (no current project) + work/screens/t252/
research_open_game.png (project active), both 640x480 native, original game:
- HEADER: green centred "Chamachies Knowledge" y~17 over the mottled band;
  small species-crest box at (0..32, 0..32) LEFT (1starmap k3 analog slot).
  static.txt #130 (reswin.cpp pool) = "%s Knowledge %s" — a SECOND %s exists
  that the screenshots never show filled -> port renders name+" Knowledge"
  with the second slot EMPTY; seam named.
- TREE FIELD: black, framed panel x 7..476 y 46..472 (the RESWIN rect exact).
  NODES = rings ~50 px diameter at organic (non-grid) positions; connecting
  lines thin blue between dependent nodes. STATES: DISCOVERED = ring filled
  with gizmo art; AVAILABLE = EMPTY ring (blue-grey); IN PROGRESS = ring with
  GOLD/ORANGE rim (t252 node ~(283,183)); one node at the t268 bottom edge
  (362,462) has a RED rim (the t268 dossier's red-ringed Megagraph read).
- RIGHT PANEL x 484..632 (its own frame; OUTSIDE the RESWIN rect — the table's
  7,46-476,472 covers the TREE only): t252 verbatim lines, all green,
  CENTRED in the panel:
    "Current Project:"            y~21   == static #122
    <disk icon ~46px>             y~60   (gold-rimmed gizmo face)
    "Accel Energy" / "Replenishment"  y~113/129 (word-wrapped name)
    "(16 days)"                   y~145  == static #124 "(%d day%s)"
    "Allows"                      y~162  == static #125
    "Lush Growth Bomb"            y~178  (first Allows entry, wrapped)
    <planet art ~60x46>           y~215
  t268 (no project): panel FULLY BLANK -> "(No Progress)" (#123) is the
  NO-PROGRESS string but renders nowhere in this shot [honest observation:
  vendor shows NOTHING; port renders nothing when queue empty, #123 pinned
  as data only].
- PAN WIDGETS bottom-right OUTSIDE the tree panel: horizontal double-arrow
  box ~(524,442)-(554,472) (the two RESROT buttons, SHAPEFRAMEs 0/1 =
  20res.shp faces) + vertical double-arrow box ~(563,442)-(593,472) (RESMOVE
  up/down, frames 2/3). A third arrow pair exists at ~(600,442) [vision] that
  NO windows.txt record covers -> [inferred] minimap-move or dead art; seam.
- t268 CLICK LAWS (already banked ui-runtime.md 6d, binding for this port):
  click EMPTY disk -> SETS current topic, 900px change confined to the disk
  bbox, NO confirm popup; click DISCOVERED disk -> dossier readout only, no
  state change; the "(N days)" line renders ONLY for the in-progress topic.
- ALLOWS LAW 3/3 [verified banked]: Allows list = reverse join gizmos+
  planitems whose tech field == restree idx (row N -> idx N-3 == all() index
  == rewrite Tech row). rewrite Gizmo.resReq + PlanetItem.reqByte ARE the
  tech field (economy.h) -> the join is computable port-side TODAY.

## F7 PORT MODULE DESIGN (locked after F6)
ui/researchview.{h,cpp} PURE (statuslist/fleetlist precedent):
- partition(owned) -> per row: Owned | Study (queued) | Available (unowned,
  all prereqs owned) | Blocked (else). Vendor renders empty disks for the
  studyable set; blocked-node rendering in the captures is INDETERMINATE
  (all visible rings were available) -> port renders blocked DIM, seam named.
- setStudy law: Available -> setQueuedTechFor(kPlayer,row) + true; Owned/
  Study/Blocked -> false, silent (the captures show no reject feedback).
- panel text: header via static #130 first-%s law; "Current Project:" #122;
  days #124 "(%d day%s)" singular iff 1; "Allows" #125; allows list = the
  reverse join (gizmos+items, table order, names with ^ -> space).
- ETA [labelled PORT DEFAULT]: days = ceil(remaining / last-turn rate) with
  rate<=0 -> 0; the vendor rate law is UNMEASURED (n=2 dossier points prove
  days is NOT cost-only). Campaign needs ONE new read accessor
  techProgressFor(owner) + techQueuedFor(owner) (same posture as t407 fleet()).
- layout: depth-x (longest-prereq-chain depth, the t3 restree table) x row-
  order y, pitch constants port-derived; pan offsets from the four buttons
  (rotate pair = horizontal, move pair = vertical per t252 pixel-diff: the
  arrows pan the FIELD; the t252 diff also showed the minimap column reacts).
  VENDOR NODE POSITIONS ARE UNKNOWN (restree.txt carries no coordinates;
  respan.bin = ascend02 runtime data, not a layout file) -> port layout is a
  LABELLED deterministic derived layout, seam named with the witness that
  would close it (pointer-law capture of the reswin node table).

## F8 IMPLEMENTATION LANDED (build green, suite 376/0 = 368 + 8)
- ui/researchview.{h,cpp} PURE: researchNodes partition / setStudy /
  researchHeaderText / allowsList (gizmos-then-items table order, '^'->' ') /
  researchDaysLine (#124, singular iff 1, ceil ETA port default) /
  researchDepth (iterative memo, longest chain) / researchNodePos (derived
  layout, pan-added) / researchHit (pan rects FIRST -> nodes r30 nearest).
- Campaign read surface (ALL display-only, zero rng): researchTree(),
  techProgressFor, techRateFor + techRate_ member written next to
  techProgress in researchPhase; gizmoAt/gizmoCount beside planetItem.
- ui.cpp: kScreenResearch header now centred #130-join (generic rail label
  suppressed for 20 like 10), content painter = clipped tree field (edges
  thin blue, rings r30/27: owned filled blue, study GOLD rim, available
  empty blue-grey, blocked DIM [port choice, seam named]), the four pan
  arrow boxes at the verbatim rects, RIGHT panel x484..632 code-drawn
  (#122, wrapped name ~18 cols, days, #125, Allows <=6; BLANK when no
  project per the t268 witness — #123 pinned as data only).
- Click chain: research branch BEFORE the planet branches (mutually
  exclusive screens anyway); study -> 'ui research study <name>', owned ->
  'ui research readout <name>', blocked SILENT; pan -> 'ui research pan X Y'.
- CMake: researchview.cpp in ascend_ui AND the run_tests ui list (t399
  pitfall); test file added. REQUIRE_DATA census: every data-reading TEST
  guarded (days_line + geometry read no files) — t403 law held.

## F9 WITNESS VERDICT PASS + NATIVE-VISION GRADE (D13 self-grade law)
scripts/t408_research_witness.sh (Xvfb :97, dummy audio, seed 5, boot ->
rail Research -> click depth-column centres (40+d*96, 76)):
  log: "ui screen map -> Research (RESEARCH)" / "ui research readout Orbital
  Structures" / "ui research readout Interplanetary Exploration" / "ui
  research study Spacetime Surfing" / "ui research pan 96 0" / "pan 96 -78"
  / "pan 192 -78"; zero laser01. PASS x3, VERDICT PASS.
NATIVE GRADE of the post-study frame (/tmp/t408_study.png): header "Player
Knowledge" green centred; gold-rimmed ring at (232,76) = the study node,
distinct from the empty blue-grey rings and the three filled discovered
discs; thin blue prereq lanes; right panel "Current Project: / Spacetime
Surfing / (0 days) / Allows / Star Lane Drive" all green centred; two red-
arrow pan boxes bottom-right at the cited rects; "Esc: return to galaxy"
footer. D13 symptom "research is empty" FIXED; "can't select a technology"
FIXED (click sets the topic, panel + gold ring follow).
RACE FORENSICS (two witness bugs, both fixed in the script):
  (1) grep race: the study line lands asynchronously -> sleep 0.4 before
      grep; (2) SHOT race: a screenshot at +0.1 s post-click was
      md5-IDENTICAL to the pre-click frame; +1.0 s held the new frame ->
      sleep 1.2 before shot research-study. (3) NEVER echo into app.log:
      the app's own stdout file-offset OVERWRITES appended bytes (probe
      state goes to probe.log).
## F10 MUTATION 9/9 CAUGHT + SUITE/SEED/GATE GREEN
scripts/t408_mutate.py (anchor-guarded count==1, revert by FILE COPY from
/tmp/t408-snap, verdict = filtered run_tests exit code + named FAIL lines):
M1 setStudy-accepts-owned CAUGHT (:244 study==1); M2 setStudy-accepts-
blocked CAUGHT (:244); M3 header-join CAUGHT; M4 days-plural-inverted
CAUGHT (:174); M5 days-floor CAUGHT; M6 allows-order-reversed CAUGHT
(:288 Accutron first-vs-second); M7 MoveUp-extent-widened CAUGHT (:315 the
554..563 gap semantics); M8 pan-precedence-dropped CAUGHT; M9 Study-
merged-into-Available CAUGHT. Restore rebuild 8/8 green.
SUITE 376/0 (368 + 8). SEED REGRESSION: seeds 1/2024/23 md5
7e794a6d/332a8cf3/0a6b7876 == the banked record EXACTLY (techRate_ is a
display-only write; zero rng consumption, transitivity law t396 + direct
re-measurement this session). GATE_EXIT=0; ledger audit OK; index check OK
(17 closed / 3 open).
## F11 LEDGER — HONEST NEGATIVE (strict-close)
NO OQ row closed. The D13 research-screen complaints have no OQ owner (same
disposition as t405/t406/t407). NAMED SEAMS left open, each with the
witness that would close it: (S1) vendor node POSITIONS (organic, non-grid;
needs a pointer-law capture of the reswin node table or a full-tree vendor
screenshot); (S2) the #130 second %s (never rendered in any capture);
(#123 "(No Progress)" renders nowhere in the t268 no-project capture —
pinned as data only); (S3) the vendor ETA/rate law (n=2 dossier points
prove NOT cost-only; port = ceil(remaining/last-rate), labelled default);
(S4) 20res.shp arrow-face blit + restree.shp disk art (geometry cited,
palette registration owed); (S5) the third vision-observed arrow pair at
~(600,442) with NO windows.txt record; (S6) blocked-node rendering (dim =
port choice; captures never show one); (S7) panel wrap width 18 (labelled).
