# _wip_t311 — STATUSWND-FOCUSED DIGIT KEYS + fn 0x51834 ENTRY LEG
Fresh session, 2026-11-05 ~18:20 EST. Task per STATE.md NEXT ACTION.

## S0. Pre-flight (verified this session)
- playcap watch alive (pid 1979), production dosbox pid 1957 :9 untouched;
  live-timeline tail: turn 1086 constant across last 4 MB (44/45.sav), same
  state as t310 -> NO new sitting, assignment stands, no r1_t85g_sitting rerun.
- LEG bytes re-verified vs work/ascend_payload.bin THIS session:
  fn 0x51834 entry `56 57 55 83 ec 0c 89 c5 66 89 54 24` (matches t310 law);
  w51ac9 `89 15 04 35 04 00`; s2_1616f `ff 53 0c`; btn_hdlr `56 57 55 83 ec 04 89 c6`.
- Binding negatives honoured (REFUTED-ROUTES t309/t310 amendments): no
  ds:0x484ec-as-turn anything; no file-image class-table scans; ring channel
  dead at map idle (not re-armed); whole-log counts use fire_pats(P0+LEGS[n]).

## S1. Script changes (scripts/r299_leg_session.py)
1. LEGS += "fn51834_entry": 0x51834 — msg pre-dispatcher ENTRY for the
   STATUSWND class (class grid RAM 0x248040 slot 4, named t310 S5). Fires for
   EVERY msg delivered to the class; dx = msg id; bank_stop banks edx +
   ret_stack (ret0 = dispatch site) + magic window rec (win-name names the
   window verbatim).
2. digit-phase hardening (the t310 focus defect): after close_eventwin,
   assert_on_map IMMEDIATELY before arm; arm_census failure aborts keys (kept);
   after arm, a post-arm grab + eventwin_open re-check — if a popup re-opened
   between close and arm, log POPUP-REGUARD and skip keys rather than press
   into the wrong window again.
3. LEGSET ordering: put fn51834_entry FIRST when present so the census-ctl
   probe compares a code-entry leg (t310 lesson: store-imm leg[0] => expected
   MATCH=False noise).

## S1b. LAUNCHED 2026-11-05 ~18:26 EST (background proc_24abfe22715f, pid
## 85320, loop log work/r1/t311-loop.log). Pre-check: port 55999 free,
## production dosbox pid 1957 (:9, session.conf) untouched. py_compile OK.
## Script deltas landed: LEGS+fn51834_entry (brace bug on the s2_1616f line
## fixed); digit block MOVED above open_fleet (bare-map focus composition)
## with assert_on_map + post-arm eventwin reguard; the OLD t310 in-place digit
## block DELETED (it would have overwritten census["digit_keys"] with a
## popup-focused re-press).

## S3. RUN RESULT (run t299-leg-20261105-182822, rc=0, attempt 1, census
## MATCH=True 7/7 arms — entry-leg leg[0] law confirmed). Battery: baseline ->
## hold -> pre-turn 1086->1087 -> close_eventwin+assert_on_map on the BARE MAP
## -> digit keys 1..9 in ONE armed 60 s window (post-arm reguard passed, no
## popup) -> fleet rowjump -> sprite 48x151 -> planet 439x331 -> control
## NEXTTURN -> hold_post_turn.
- PTY WHOLE-LOG CENSUS: {fn51834_entry: 0, w43508_51a8e: 0, w51ac9: 0,
  s2_1616f: 0, btn_hdlr: 4}. Control alive -> the zeros are context.
- **BRANCH (c) IS THE MEASURED OUTCOME**: the fn 0x51834 ENTRY leg — which
  fires for EVERY msg delivered to the STATUSWND class, gate-free (dx is read
  after the cmp chain, the entry itself is unconditional) — fired ZERO across
  the entire log. STATUSWND receives NO msg traffic at all (not just no
  0x1c01) on this rig's legitimate input battery: bare-map digit keys, sprite
  select, planet click, NEXTTURN, two hot holds.
- Digit-window focus datum (the t310 defect is FIXED and MEASURED fixed):
  bare-map keys hit btn_hdlr win name='NEXTTURNCONT' (eax=0xfd6240, edx=0x3,
  ebp=0x247ca0, ret0 file 0x3177d) — NOT the 'Cancel' popup anymore. So the
  key-focused window on the bare map is a BUTTON class (class grid ends
  0x247cb8 family), NOT STATUSWND. STATUSWND is never key-focused on the map.
- Other stops (all btn_hdlr, control alive): sprite win 'PLIND' (edx=0x8);
  planet win 'Cancel' (ret0 file 0x56c77 — popup still opens on planet click
  but keys phase ran BEFORE it, so digit datum is clean); nextturn win
  'PLSQUARE' (ret0 file 0x3d391).
- Oracles: DAT_43504 constant 'Icarus' 0x256825 whole run; DAT_43508 churns
  0x26fe77 (pre-turn/bare-map) -> 0x26f00d (post-fleet), sel43510=0 throughout
  — NO destination write on any phase; digit_after gate_484ec=0x1ff (last
  mouse X unchanged from pre-turn NEXTTURN click at x=511).
- s2_1616f (the fn-0x160xx 0x1c01 RELAY site) zero whole-log: that relay path
  is dead on this battery too.

## S4. CONCLUSION (strict-close: NO row closes; honest negative)
- 0x1c01-into-STATUSWND joins REFUTED-ROUTES (t311 amendment). The entry-leg
  instrument is now LIVE-VALIDATED in the negative sense: gate-free entry,
  control btn_hdlr alive in the same windows, zero fires => the class simply
  receives nothing from map clicks/keys. The destination widget is NOT driven
  by STATUSWND-focus + digit keys.
- What the entry leg CANNOT see (honest boundary): a msg delivered to the
  STATUSWND instance via a DIRECT call fn 0x51834 (not through [ecx+4] the
  class slot). But t310's sender census found only 2 senders of 0x1c01, both
  class-table calls ([ebx+0xc] relay, [esi+8] digit-key) — so if 0x1c01 ever
  reaches fn 0x51834 it is via a class-table call the entry leg WOULD catch.
  The zero is therefore a real "msg never sent", not an instrument gap.
- INSTRUMENT SCOPE, stated precisely: a BP at fn 0x51834's ENTRY fires no
  matter WHO calls it (class-table slot, direct E8, tail-call — any route),
  so "entry zero whole-log" = fn 0x51834 was never entered, full stop. What
  was NOT armed this run: the digit SENDER 0x35696 itself — so whether the
  sender's 0x1c01 store-then-call fired is UNMEASURED; measured is that its
  only possible destination (fn 0x51834) never ran, and that the key presses
  entered the generic dispatcher (btn_hdlr stops, ret0 file 0x3177d) on the
  key-focused 'NEXTTURNCONT' window with ordinary msg ids (edx=0x3), not
  0x1c01 chains. If 0x35696 fired at all, its call [esi+8] resolved to a
  slot landing on btn_hdlr (the stop IS btn_hdlr, ebp=0x247ca0 = a class grid
  near the button family), never STATUSWND's fn 0x51834.
- The destination writers (DAT_43504/08, t309 inventory; fn 0x51b68 owns
  0x52003 + 0x51fc2, 0x51ac9 is fn 0x51834's per t310 span fix) must be
  driven by a trigger OUTSIDE the map-click/key battery: fn
  0x51b68 is a table member (t309: E8/u32-ref-less) reached via ret_stack.
  t312 route: the ORDER-PLACEMENT path — t298-B relay 0x326 (planet-order leg
  0x1bad3 dl==3, empty-order leg 0x1ba45 dl==1) is the live ship->dest order;
  watch fn 0x51b68's THREE writer legs (0x52003, 0x51ac9, 0x51fc2) with a
  real kind-4 ship selected + planet click, i.e. the r298 choreography S4
  WITH the pre-turn gate satisfied and the writer legs (not batmode legs)
  armed. t306 refuted batmode legs for map clicks, NOT the 0x51b68 writers.

LEGSET = fn51834_entry,w43508_51a8e,w51ac9,s2_1616f,btn_hdlr
Battery: baseline -> --pre-turn 1 -> close_eventwin -> digit keys 1..9 in ONE
armed window (60 s) -> sprite/planet pair (secondary) -> control_nextturn ->
hold_post_turn. port 55999, disp :97, tl 7200.
CLOSE CONDITIONS (per task):
 (a) stop at fn51834_entry dx=0x1c01 + store-leg stop w/ ret0 in the 0x51A67
     block -> destination writer WITNESSED, OQ-019 residue narrows to per-ship.
 (b) stops at fn51834_entry with OTHER dx -> bank msg-id SET (first-ever
     STATUSWND msg census), row stays open.
 (c) fn51834_entry ZERO whole-log with btn_hdlr alive -> STATUSWND receives no
     key traffic on this rig -> 0x1c01-into-STATUSWND joins REFUTED-ROUTES;
     destination widget sought behind order-placement UI in t312.
