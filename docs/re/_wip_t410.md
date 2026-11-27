# t410 WIP — SYSTEM VIEW + MAP->PLANET CHAIN (working log)

Task: user D13 "haven't found any way to pull up the system view screen, or
planet view screen". Wire: star click on the map -> system view; planet dot
there -> t406 planet view (state 17); Escape chain depth pinned.

## F0 — PRE-FLIGHT (session health)
- Tree clean at launch (3ead597). Ring t368: parsed=20/20 max_turn=1254 ==
  same sitting as t380..t409 -> NO new play; assignment stands. Timeline
  mtime 2026-11-12 06:45 (stale feed; ring-first law honoured).

## F1 — STATE-ID CENSUS OF THE SYSTEM VIEW (windows.txt, re-parsed whole)
[verified] work/r1/t410_state_census.py over extracted/ascend00/windows.txt
(cp437, blank-line-separated records, 124 NAME+TYPE records). STATE token
counts: {0:26, 1:110, 2:2, 3:21, 4:3, 6:1, 7:21, 8:9, 9:1, 10:2, 12:1,
13:16, 14:2, 15:2, 16:20, 17:14, 18:2, 20:5}.
STATE 16 = EXACTLY 20 records, the SYSTEM-VIEW family:
  BatModeWnd TYPE 4 PARENT NONE rect 7,7-465,472 (the orbital grid viewport,
    same rect as COSMOSWnd) STATE "1 16"
  BatControlWnd TYPE 19 rect 0,0-0,0 (parent-only, NEVER a hit target - t338)
  BatListWnd TYPE 10 PARENT BatControlWnd 474,142-632,394 SHAPEFRAME 7
  camera/console children of BatModeWnd (rects cited verbatim):
    BATROTLEFT 479,403-493,433 msg50 / BATROTRIGHT 494,403-509,433 msg51
    BATZOOMIN 518,403-548,418 msg54 / BATZOOMOUT 518,419-548,433 msg55
    TOGGRID TYPE25 557,403-587,433 msg74 / TOGELEV TYPE25 596,403-626,433 msg76
    RECENTER 596,442-626,472 msg71 / ABANDON TYPE31 479,442-548,472 msg84
  right-panel buttons of BatControlWnd: My^Items 479,103-548,133 msg804,
    Other^Items 557,103-626,133 msg805, Pass 479,55-522,85 msg807,
    Auto 583,55-626,85 msg808, Repeat 531,55-574,85 msg809,
    W 479,103-509,133 msg810 / S 518,103-548,133 msg811 /
    I 596,103-626,133 msg812 / Z 557,103-587,433... (Z 557,103-587,133 msg813)
STATE 17 = EXACTLY 14 records = PLANETALLOC family (t406 shipped).
STATE 13 = NEGSCREEN/ALIENDIP/PLAYERDIP (diplomacy) + the COSMOSWnd rail
  children carry "3 1 7 13" (rail is live in states 1,3,7,13).
[verified] COSMOSWnd STATE list = "4 1 3 7 13" — state 16 is NOT in it, so in
the vendor system view the galaxy-map rail/children are NOT live (matches the
t369 playtest note "NEXTTURN clicks STUCK while screen sat in SYSTEM VIEW
(button exists only on star map)" — now table-cited, not a candidate law).

## F2 — SYSTEM VIEW = STATE ID 16 (two independent citations; packed-dword
## arithmetic NOT re-resolved and NOT needed)
Prior docs quote the "mode4226" oracle 0x1 at map, 0x10 entering the system
view (t309 star0_after) and 0x11 inside it (t310/t312/t314); t318 banked the
datum as churning "0x1/0x11/0x12". This session does NOT re-derive the packed
u32 layout (winmgr+0x4226 is two u16s per t337; the 0x10/0x11 half-arithmetic
would need a fresh capture — not owed for a port that models state IDS).
What IS cited for the state identity:
  (a) windows.txt STATE lists (F1 census): the system-view family (BatModeWnd
      + BatControlWnd + BatListWnd + camera/console buttons) carries STATE
      "1 16" x20; COSMOSWnd carries "4 1 3 7 13" (no 16); PLANETALLOC family
      carries "1 17" x14. [verified]
  (b) t338 LIVE: SET-STATE fn 0x56e10 entered with edx=0x10 on core 0x2bc35c
      when the galaxy-map Icarus pip (238,282) was clicked; 13 oracle reads
      state==16 through the battery (docs/re/_wip_t338.md ln49/57-58 + ln80
      "witness edx=0x10"; ships.md S57). [verified measurement]
  (c) t337 save census: current-state word core+0x4228 histogram
      {0:122, 1:236, 16:5, 17:174} over 537 saves — 16 (system view) and 17
      (planet view) are both LIVE states in recorded play. [verified]
Port law: screen ids 16 (system view) and 17 (planet view) as the vendor's own
ids; the map->system entry is a STAR CLICK (t338 measured the entry on a pip
click; t293/t296 measured a FLEET-ROW jump into the same view).

## F3 — STATE-16 CHROME + GEOMETRY CENSUS (this session, all cited)
- TYPE-100 ln1140-1142: STATENUMBER 16 SHAPEFILE DATA\\16BATTLE.SHP — the
  system view IS art-backed (unlike FLEET, t391 no-18*.shp). BUT the lib has
  NO full-screen record: dims census work/r1/t410_16battle_dims.py (directory
  law shp.h: starts[0]=0x10+tsz, k0 dims@rec, k>=1 dims@rec+0x10): n=20;
  k0 30x30; k1 14x30; k2 15x30; k3 30x15; k4 30x14; k5/k6 30x30;
  k7 65x28; k8 67x29; k9 69x30; k10/k11/k19 173x141; k12..k15 30x30;
  k16..k18 43x30. => the blue orbital-grid plane is CODE-DRAWN (selfplay.md
  S4 description stands); the lib holds the console/button faces.
- SHAPEFRAME->record DIMS PARITY (t394 law: shape == rect minus 1) re-run on
  state 16: EXACT 14/16 — TOGGRID FR0 30x30==31x31-1, BATROTLEFT FR1 14x30,
  BATROTRIGHT FR2 15x30, BATZOOMIN FR3 30x15, BATZOOMOUT FR4 30x14,
  RECENTER FR5 30x30, TOGELEV FR6 30x30, Other^Items FR9 69x30,
  W FR12/S FR13/I FR14/Z FR15 30x30, Pass FR16/Repeat FR17/Auto FR18 43x30.
  OFF-PARITY 2/16: My^Items FR7 (65x28 vs rect-minus-1 69x30) and ABANDON
  FR8 (67x29 vs 69x30) — k7/k8/k9 is a size ladder; mapping those two is a
  NAMED SEAM (faces not blitted for them).
- help batmode VERBATIM (help.txt ln1149-1176): "The System Display is used
  to view and manipulate the contents of star systems. The controls at the
  lower right can be used to manipulate this display." + page 2: "You can
  move a selected ship by clicking on a desired destination... You can view a
  selected planet by clicking it again." (ln1170-1176 — the planet-dot click
  law, corroborates planet.txt info00 ln16 "by entering the System Display,
  and then selecting the planet by clicking on it").
- BatModeWnd ln1178-1190: rect 7,7-465,472 (== COSMOSWnd rect), CURSORSHAPE 2,
  HELPINDEX batmode. BatListWnd 474,142-632,394 SHAPEFRAME 7 (the generic
  LIST frame — STATPLANLST/RESWIN-list/PLANLIST/PLAYERDIP all FR 7).
- ABANDON TYPE 31 msg 84: DESTRUCTIVE in the vendor (t369 live: a misaimed
  console click opened "Are you sure you want to abandon Vega II?"). Port
  renders chrome, NEVER wires destruction (refusal log only).
- Ships-present census in the port: ShipInTransit{owner,from,target} is the
  ENTIRE ship state (t256c GAP ROW 16); NO per-ship position exists -> the
  system view shows NO ship rows; named seam (BatListWnd region inert + log).

## F4 — DESIGN DECISIONS (pure module ui/sysview.{h,cpp})
- STATE 16 screen id joins statuslaw (kScreenSystemView=16);
  screenShapeLib(16)="16battle.shp" — the ONLY cited art lib (TYPE-100
  ln1140-1142). Faces: SHAPEFRAME->record IDENTITY + t394 DIMS PARITY
  verified 14/16 buttons (F3); My^Items FR7 / ABANDON FR8 off-parity =
  named seam (no face).
- ENTRY LAW: single LEFT click on a projected star on the map (t338 live:
  SET-STATE edx=0x10 on the pip click; NOT double-click — no vendor record
  or witness says double). Empty-space clicks stay silent+inert (t404).
- ESCAPE CHAIN: ONE level per press [verified t252 pixel-diff 82k->3.4k
  intel->species->galaxy; corroborated t369 system-view]. Implemented as a
  pure ScreenStack (map always at bottom; push truncates if already
  present); 1 -> 16 -> 17: Esc 17->16, Esc 16->1, Esc 1 = standing quit.
  [tESC-1 CORRECTION 2026-11-27: "Esc 1 = standing quit" was a PORT default
  mislabelled as law — the vendor's ESC arm 0x54e96 calls ONLY pop
  FUN_00057020 and at the map level ejects to the TITLE menu with the
  campaign alive (t285 witness + asm, docs/re/_wip_tESC1.md P1-P4). Port
  now matches: ui.cpp toTitle handoff + main() title<->campaign loop. The
  ScreenStack model itself is CONFIRMED at bytes: pop = tombstone 0xffff +
  depth-- at 0x5706b/0x5707c.]
  escapeToMap() keeps its t388/t405 meaning (a level exists to unwind).
- ORBITAL LAYOUT: PORT LAW (no vendor per-planet position datum exists in
  the rewrite model): centre = viewport centre, ring radius
  kOrbitBase+kOrbitPitch*i, angle = i*golden-angle constant (deterministic,
  ZERO rng), rotated/zoomed by a second Camera3d whose bounds are
  kBatModeWnd. Colonised dot = index 0 iff star owned (t406 one-PlanetState-
  per-star model), owner colour + ring (CVD shape redundancy).
- CONSOLE: rotate/zoom/recenter DRIVE the system camera; TOGGRID toggles
  grid lines (port default ON — t244 wireframe witness); TOGELEV seam
  (no elevation model); ABANDON (TYPE 31 msg 84) REFUSAL-ONLY (t369 live
  destroyed-planet hazard); ship-order widgets (My^Items/Other^Items/W/S/I/
  Z/Pass/Auto/Repeat) seam-log: per-ship selection is the OQ-019 hole and
  t312 MEASURED that sprite clicks select nothing in the vendor view either.
  Hit precedence = windows.txt file order, last-match-wins (t264 law),
  which resolves the W/S-inside-My^Items overlap exactly.
- BatListWnd: honest-vector frame + zero rows (t256c: ShipInTransit is the
  entire ship state; no per-ship presence). Named seam.
- Campaign changes: NONE needed (starOwner/planetAt/galaxy() suffice) ->
  seed md5s untouched by construction.

## F5 — LANDED CODE + PINS (suite 384 -> 391/0)
- NEW ui/sysview.{h,cpp} (pure): ScreenStack (push=truncate-to-existing,
  escape=pop-one, bottom=false); kSysCtl[17] verbatim table (Auto included —
  first draft dropped it, census re-run ln1400 caught it); sysCtlFor
  last-match-wins (W/S beat My^Items span); sysCtlShapeRecord = SHAPEFRAME
  identity EXCEPT MyItems/Abandon (-1 named seam); orbitAngle/Radius +
  systemOrbits (colonised == index 0 iff owned; zero rng) + hitOrbitDot.
- statuslaw: kScreenSystemView=16 joins the known set; screenShapeLib(16)=
  "16battle.shp" (TYPE-100 EXPLICIT); screenName: 16="System Display"
  (help.txt ln1149 verbatim), 17="Planet Display" (help ln1501-7 — Escape
  log lines now name both ends).
- ui.cpp: map star click pushes 16 (silent, t404 law); state-16 click chain
  (console -> camera/grid; ABANDON refusal-only; order family seam-log;
  colonised dot -> push 17; bare body -> seam line, NEVER a fabricated
  readout); Escape branch = stack.escape() with from->to names; paint branch
  (wireframe rings+spokes iff gridOn, stalks, owner-colour dots, colonised
  white ring, console faces via blitShape with vector fallback, BatListWnd
  frame + honest-zero seam line); 16battle.shp joins kLibs (7 entries,
  libFor loop 6->7); HOME-STAR DIAGNOSTIC printf (display-only) so a witness
  clicks the entry without guessing.
- PINS test_sysview_t410.cpp x7 (chain + no-duplicate + console table +
  SHAPE identity/parity on the REAL 16battle.shp + layout + campaign dots +
  screen law). ONE pin bug caught by running: duplicate-level test expected
  depth 3, correct is 4 (t252: intel opened FROM species menu Escapes TO the
  menu — rail-opened screens STACK above what was open; only re-entering a
  PRESENT screen truncates). Fixture ctor copied wrong first (Campaign
  takes a generated Galaxy, not the table refs) — build error, fixed.

## F6 — WITNESS scripts/t410_sysview_witness.sh VERDICT PASS + OWN-GRADE
- Chain markers in log order: home-star diag (Amoroso 254,438) -> click ->
  "ui system view Amoroso (state 16)" -> TOGGRID "grid 0" -> "abandon
  refused" -> "ui system planet Amoroso I -> planet view (state 17)" ->
  "Planet Display -> System Display (esc)" -> "System Display -> map (esc)"
  -> zero laser01. Shots /tmp/t410_shots/{sys-open,planet-open,back-map}.png.
- NATIVE VISION GRADE (sys-open): concentric blue wireframe rings + 8
  spokes, two dots on yellow stalks, colonised dot ringed, console faces
  blit on the right column (real 16battle art, game.pal colours), list
  frame + seam text, "Amoroso [yours]" bottom-left. DEFECT FOUND+FIXED:
  BatListWnd seam text clipped at the list edge -> shortened "ships: seam
  (t256c)". planet-open: t406 readout intact ("Amoroso I (Small Husk
  Planet)", Population 2/7 working 1, No Project) — the chain's far end
  renders real data.
- t404 witness RE-RUN PASS after the change (map click (100,240) hits no
  star on seed 5 -> stays silent+inert; rail/next-turn click08 intact).

## F6 — MUTATION CAMPAIGN 9/9 CAUGHT (scripts/t410_mutate.py)
M1 stack-duplicate-stacked, M2 escape-pops-past-bottom, M3 toggrid-rect-drift,
M4 first-match-wins (overlap), M5 shape-identity-offset, M6 seam-faces-accepted,
M7 colonised-index-shifted, M8 orbit-pitch-drift, M9 hit-radius-law-dead —
each caught by NAMED test_sysview_t410.cpp failures (verdict = run_tests exit
code per t407-F13). AFTER-RESTORE clean: 391/0.
PITFALL (new): the FIRST campaign run was killed by the 420s FOREGROUND tool
timeout mid-mutant (M7 applied, restore never ran) -> the background re-run
snapshotted an ALREADY-MUTATED file: M7 reported PATCH-MISS and AFTER-RESTORE
reported CAUGHT (2 fails) with a healthy-looking md5. Recovery: reconstruct
from the pin (test 237/238 = index 0 colonised), fix, re-verify 391/0, then
run M7 standalone inside execute_code (apply->build->run->restore ALWAYS in
one python block). LAW: mutation campaigns over 3-4 mutants must run inside
execute_code or background-with-restore-guard; a killed foreground run poisons
the snapshot.
