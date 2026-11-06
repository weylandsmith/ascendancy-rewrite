# t312 WIP — ORDER-PLACEMENT WRITER RUN (fn 0x51b68 destination-writer pair)

Assignment: docs/STATE.md NEXT ACTION t312 (session 21, 2026-11-05). Witness
fn 0x51b68's destination-writer pair {w43504_52003 (DAT_43504, eax=[esi+0x59]),
w43508_51fc2 (DAT_43508, eax=[edx+0x59])} on a real ship->destination order
choreography (t298-B shape), or bank a second honest negative narrowing OQ-019
residue to per-ship-select.

## S0 — PRE-FLIGHT (offline, verified this session)

S0.1 New sitting check: `live-timeline.jsonl` mtime 19:16 is the WATCH DAEMON's
own polling (watch.log tail: t=1086 steady, sel=0, ships=30 across 19:12-19:16
saves 41..60) — NO human sitting since t311 commit 19:12:52. r1_t85g_sitting.py
NOT run (no new sitting to fold in). Assignment stands.

S0.2 Leg inventory (grep scripts/r299_leg_session.py, verbatim dict entries):
  "btn_hdlr":      0x336B4   (line 162)  type-0 button handler, control
  "s2_356a5":      0x356A5   (line 210)  digit sender's own call site
  "w43504_52003":  0x52003   (line 227)  ship order-target, eax=[esi+0x59]
  "w43508_51fc2":  0x51FC2   (line 230)  eax=[edx+0x59], ring 0x11
  "fn51834_entry": 0x51834   (line 280)  STATUSWND handler entry (ctl anchor)
All five EXIST -> zero script delta; only scripts/r312_relaunch.sh is new.

S0.3 Legset ORDER law: fn51834_entry FIRST (code-entry leg => census-ctl
RAM-vs-FILE MATCH is meaningful; t311 law, MATCH=True 7/7). fn51834_entry is
kept ONLY as the leg[0] ctl anchor + sender witness — arming it hoping a map
battery messages it is REFUTED (REFUTED-ROUTES t311 amendment).

S0.4 Choreography health check from the t311 run (work/r1/t311/attempt-1-console.log):
  - PRE-TURN 1086 -> 1087 (line 58) — the kind-4 owner-0 gate opens.
  - `CENSUS view star='Icarus' sprites=[(48, 151, 296)] planet=(439, 331)
    empty=(236, 200)` (line 109) — sprite detection WORKS on this save, so the
    ship->destination order is ATTEMPTABLE (the t298-B "order impossible"
    branch is not pre-established).
  - Sprite click stop (line 124-125): leg=btn_hdlr eip=0x1f2b04 file=0x336b4
    eax=0xfe72d4 ecx=0x97 edx=0x8, win[esi] name='PLIND'.
  - Planet click stop (line 159-160): leg=btn_hdlr edx=0x4, win[eax]
    name='Cancel'.
  - Oracle pairs BOTH show sel43510: 0 before AND after the sprite click and
    after the planet click (lines 110/144/145/179) — i.e. in the t311 battery
    NOTHING was selected per the DAT_43510 selection oracle. That is the
    standing per-ship-select hole; this run re-measures it as a freebie.
  - mode4226 = 0x11 before AND after the sprite click (t311 log) — the
    "mode 0->2" selection transition the t298-B choreography assumes was NOT
    observed on this battery shape.

## S1 — CAPTURE RUN

Legset: fn51834_entry,w43504_52003,w43508_51fc2,s2_356a5,btn_hdlr
Battery (existing r299 census path, no delta): baseline -> hold -> --pre-turn 1
-> digit keys 1..9 on the bare map -> fleet rowjump -> sprite click -> planet
click (separate armed windows) -> control_nextturn -> hold_post_turn ->
whole-log pty census.
Runner: scripts/r312_relaunch.sh (r311 pattern: attempts 1,2,2, stop on
rc=0-with-pty-census, never retry rc=2). Xvfb :97, port 55999, scratch game-wp,
production :9 untouched, kill-by-recorded-PID.

CLOSE LAW (from the assignment):
 (a) any stop at 0x52003 / 0x51fc2 with a named ret0 => destination writer
     WITNESSED; fn 0x51b68 is table-member-called (E8/u32-ref-less) so
     ret_stack names its caller verbatim; OQ-019 residue narrows to per-ship
     select.
 (b) all-writer zeros with btn_hdlr alive => fn 0x51b68 is ALSO unreached by
     order clicks -> bank the honest negative; residual = per-ship-select +
     a fn 0x51b68 caller hunt via sav RAM scan of the class grid containing
     0x51b68+P0 (t310 RAM-scan route: scan the grid slot index FIRST, then
     infer which table the game consults).
NOT armed deliberately: batmode legs (t306 amendment binding — dead for
system/map clicks).

## S2 — RESULTS (run t299-leg-20261105-192246, rc=0, attempt 1, no retry)

Session: spawned 19:22:48 pid=88894 Xvfb :97 port 55999 scratch game-wp, tl
7200; BREAK lottery won attempt 1 (19:23:33); all 5 legs armed + re-armed
(BPLIST 5 entries, rearm ok=True); SESSION END rc=0 19:32:44,
census-measured=['digit_keys','sprite','planet','control_nextturn'] hits=4.

S2.1 WHOLE-LOG PTY CENSUS (the verdict):
  {fn51834_entry:0, w43504_52003:0, w43508_51fc2:0, s2_356a5:0, btn_hdlr:4}
  census-ctl MATCH=True x7 (fn51834_entry leg[0] law held — instrument sane).
  => BRANCH (b) OF THE ASSIGNMENT: fn 0x51b68's destination-writer pair is
  unreached by the WHOLE ship->destination order battery. SECOND honest
  negative; OQ-019 row STAYS OPEN (strict-close), residue narrows to
  per-ship-select + the fn 0x51b68 caller hunt.

S2.2 STOP INVENTORY (all btn_hdlr, control alive — the battery DID click):
  - digit_keys#0  ret0 file 0x3177d, eax=0xfd6240 ecx=0x2 edx=0x3,
    win[esi]='NEXTTURNCONT'  (t311 datum REPRODUCED: bare-map key focus is a
    button-family class, not STATUSWND).
  - sprite_48x151#0 ret0 file 0x3cb8d, eax=0xfe72d4 ecx=0x97 edx=0x8,
    win[esi]='PLIND'  (t305/t306/t311 msg-0x8 repaint/dispatch datum
    reproduced 4th time).
  - planet_439x331#0 ret0 file 0x56c77, eax=0xfe7748 ecx=0x14b edx=0x4,
    win[eax]='Cancel' (t311 datum reproduced).
  - control_nextturn#0 ret0 file 0x3d391, eax=0xfe7170 ecx=0x43 edx=0x8,
    win[eax]='PLSQUARE' (t305 datum reproduced).
  baseline and hold_post_turn windows: 0 stops.

S2.3 ORACLE PAIRS (the decisive new datum): sel43510 = 0 in EVERY snapshot
  (preturn_before/after 1086->1087, digit_after, sprite_before/after,
  planet_before/after, nextturn_before/after); mode4226 = 0x1 before the
  sprite click, 0x11 after (view id, map->system, t309 law — NOT a selection
  mode); DAT_43504 'Icarus' constant, DAT_43508 churns 0x26fe77<->0x26f00d
  across saves with ZERO writers firing (t298-C re-observed 3rd time).
  => THE SPRITE CLICK AT (48,151) DOES NOT SELECT: the t298-B choreography's
  first step (select ship, mode 0->2) NEVER HAPPENS. The planet click that
  was supposed to be an order-destination click is a bare-map click into a
  'Cancel' popup window. This is now measured across FOUR runs (t305, t306,
  t311, t312) with the same shape.

S2.4 SENDER-SCOPE FREEBIE (assignment): s2_356a5 (the digit sender's own
  call site) fired ZERO whole-log EVEN THOUGH digit keys demonstrably reached
  a window (btn_hdlr 'NEXTTURNCONT' stop). The digit-key keysym path taken at
  the bare map is therefore NOT the 0x356a5 slot-2 sender of msg 0x1c01 —
  the t311 sender-scope question closes as a negative: NEITHER 0x1c01 sender
  (relay 0x16168 s2_1616f t311 zero, digit 0x35696->0x356a5 t312 zero) ever
  fires in any session shape tried.

S2.5 INTERPRETATION / WHY THE ZERO IS INFORMATIVE: fn 0x51b68 (label
  builder, owns 3 of the 12 DAT-selection stores) is table-member-called
  (E8/u32-ref-less). With both its DAT-writer legs armed across ~10 min of
  gameplay incl. turn advance + map/system clicks + keys, zero fires means
  the game never invoked fn 0x51b68's writer paths in this composition.
  Since the ONLY choreography that could plausibly drive them is a SELECTED
  ship issuing a destination order, and selection itself never happens
  (S2.3), the two open residues are the SAME hole: nothing in the current
  battery can select a ship. The writer hunt must therefore either (a) find
  what actually selects (the fn 0x51b68 caller, via the t310 class-grid RAM
  scan route on grid containing 0x51b68+P0: scan slot index FIRST, then
  infer which table the game consults), or (b) drive selection through the
  FLEET window keyboard/UI path rather than the sprite pixel.

## S3 — CLOSE DECISION

No ledger row closes (strict-close). Honest negative banked: fn 0x51b68
writer pair {0x52003, 0x51fc2} unreached whole-log on the t298-B order
battery with control alive (run t299-leg-20261105-192246); s2_356a5 zero
=> both msg-0x1c01 senders dead in every shape tried; sprite-pixel click
does not select (sel43510 0 x4 runs). REFUTED-ROUTES amendment: the
sprite-pixel-selection choreography is spent as a writer trigger.
Next (t313): class-grid RAM scan for 0x51b68+P0 caller identity (t310 route,
offline on this run's own save/ dir — no new capture needed for step 1).
