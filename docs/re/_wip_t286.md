# t286 WIP — MCP/PTY DEBUGGER AS A GENERAL INSTRUMENT (running notes)

## S0 TASK SHAPE (from STATE.md NEXT ACTION)
Script scripts/r1_wp_session.py so OTHER writer questions can be hunted
without hand-held sessions. Template: scripts/r1_t283_wp_session.py (its
settle laws banked there). Named hunt targets in the assignment:
u16@data 0x131b4, star byte +0x5a, PLANETALLOC getter chain.
CORRECTIONS APPLIED BEFORE BUILDING (why the assignment list is stale):
- u16@data 0x131b4 and star byte +0x5a are BOTH closed negatives already:
  0x131b4 has ZERO referencing instructions (disp32 census, _wip_t249 S10 —
  "no writer to pin"), and +0x5a is total planet SLOTS not a colonised count
  (t248 refutation, selfplay.md). Watching them would burn the session.
- The genuinely open watchpoint-class question in the same thread is the
  planet-list OBJECT: _wip_t249.md S2 "Open subitem: exact widget chain
  (needs live watchpoint, t250+)". The header PLANETS number is
  u16[obj+0x8c7]; the only writers program-wide are the list-add 0x32eb6
  (FUN_00032d1c) and resets 0x325b5/0x33015 (t249 S1). A live fire at the
  screen-open refill validates the instrument AND pins the writer chain at
  runtime — the exact thing static census could not do (indirect/vtable
  dispatch, zero E8 callers, t249 S10).

## S1 INSTRUMENT (built this session)
scripts/r1_wp_session.py — generalized from r1_t283_wp_session.py:
- --target data:OFF | lin:ADDR | heap-planets. heap-planets runs the t249
  OPEN-TIME signature scan ([o+0xab]==0 && byte[o+0xc5]==0 &&
  [o+0xbb]==0xffffffff && u16[o+0x8c9]==0x8d) over the session's own ring
  slot and watches OBJ+0x8c7. Requires exactly ONE sig-hit (refuses
  ambiguous heaps).
- --phases quiet,c,turn,planets (attribution phases; fire in a named phase
  attributes the writer to that input); --walk N walks subsequent fires with
  per-fire EIP (reported EIP = insn AFTER the store, core_normal.h:181).
- DIRECTION LAW (bind listener before spawn), pty for BREAK, settle 45 s
  before BREAK and AGAIN after the campaign load (t283 run-5), ONE armed
  BPLM (fire line prints seg 0000 = useless address), artifact rejection
  '00 -> xx' iff value nonzero at arm, EXEC-after-rejected-fire (CPU is
  stopped), MEMDUMPBIN self-verification vs payload, kill-by-recorded-PID,
  scratch work/r1/game-wp + OWN ring dir + private Xvfb :97, Oct-29
  md5-verified RESUME.GAM, base-drift abort (t285 class: B moving between
  ring scans = campaign swap, refuse to arm).
- New vs t283: pre-open click of the sidebar Planets button (window-rel
  (553,145), windows.txt rect 474,130-632,160 — the identical read-only nav
  t249 ran on production) so the heap object exists at arm time; seen-lines
  baseline taken AT ARM (t283 took it empty — a fire printed during arming
  would have been misattributed post-arms).
- Offline checks PASS: py_compile OK; resolve_target unit-checked on a
  synthetic 17 MB image (data:0x482fb -> B-0x88+0x82bb0+0x482fb EXACT;
  planted sig object -> OBJ+0x8c7 EXACT; fire-regex parses both the BPLM
  empty-tag and BPPM '(Prot)' forms).

## S2 VALIDATION RUN (heap-planets) — in flight
work/r1/t286-console.log; run dir work/r1/wp-heap-planets-<ts>/.
Expected positive shape if the instrument works: after the planets phase
click, FUN_00051834 case-1 refill fires the watchpoint with the EIP mapping
to payload file offset ~0x32eb6 (the add's `MOV word ptr [EBP+0x8c7],BX`
store, EIP reported one insn later). The artifact (count=80 at arm) is
rejected once by design.

## S3 RUN-1 NEGATIVE + WIDGET-CACHE HYPOTHESIS (run wp-heap-planets-20261103-061256)
Flow WORKED end-to-end to arming: ENTER click landed (campaign resident,
B=0x1bf4d8 — SAME base as t283's run: deterministic heap), pre-open planets
click, sig scan found EXACTLY ONE object 0xfda074 count=80 (same address as
bank-t1254's — heap determinism across sessions), BREAK#0 OK, armed
BPLM 00FDA93B, quiet 100 s ZERO fires, planets phase 7 clicks ZERO fires,
NEGATIVE rc=1. ring-final 20/20 slots: the same object, count still 80.
THREE FACTS from that (all banked, none assumed):
1. The sig object was ALREADY PRESENT at first scan (13 s after the ENTER
   click) — and RESUME.GAM.user-oct29 was saved BEFORE t249's live click, yet
   the object exists at the SAME linear address as the t249/t1254 instances.
   [inferred] save/restore replays the heap deterministically; the loaded
   campaign carried t249's last-open list snapshot (count 80 == t1086
   owner-count) into this scratch session.
2. ZERO FIRES INCLUDING READS. The header render reads [widget+0xab]+0x8c7
   (FUN_00051684, t249 S1) — a re-render would fire the watchpoint on the
   READ (granularity is per-instruction, t282). Nothing fired => after the
   pre-open click, NOTHING ever touched byte 0xfda93b again all session.
3. The count never changed across the 7 planets-phase clicks (ring-final).
HYPOTHESIS (drives run 2, testable): FUN_00051834 case 1 ALLOCATES+RESETS the
list IFF widget+0xab==0 (t249 S1 verbatim) — so a re-open with the list
object already attached does NOT reset/refill/re-read: t249's "refill on
EVERY open" overclaims; the evidence (zero sig-hits before click -> one after)
is equally consistent with FIRST-OPEN-PER-SESSION allocation. The t248 60-vs-80
anomaly then needs a widget TEARDOWN (one of the 24 [reg+0xab]=0 sites) to
force re-allocation between opens.
RUN-2 DESIGN (fixes two flaws found in my own instrument):
- FLAW A: t283-inherited artifact law only rejects '00 -> xx' when
  value_at_arm != 0 — but the baseline artifact shape IS '00 -> xx' for ANY
  nonzero value; correct: reject exactly one '00 -> xx' whenever
  value_at_arm != 0, treat 'xx -> 00' as the reset-store witness.
- FLAW B: run 1 clicked the SAME (553,145) while the panel was presumably
  already open — if the panel toggles, every click CLOSED it and the refill
  (if any) happened at the pre-open click BEFORE arming. Run 2 alternates
  RESEARCH (553,223, windows.txt NAME RESEARCH rect 474,208-632,238) and
  PLANETS buttons so every planets click comes from a different-panel state.
- Added: extra 30 s settle after the ENTER reaction before BREAK; all fire
  lines logged with phase+offset (already true); lin: target now records the
  byte value at scan (enables artifact logic for absolute targets).

## S4 RUNS 2-8 — INSTRUMENT SEMANTICS MEASURED (8 runs, all banked under work/r1/wp-*)
RUN 2 (064850): PRE-ARM sig-object count 0 — the loaded campaign carries NO
planet-list object (S3.1 carry-over hypothesis REFUTED; run-1's object was
created by run-1's own click). One creation click 1 s after the ENTER
reaction was SWALLOWED (12 s later still 0 hits) — clicks must be retried
until the signature appears, verified from the ring, never from xsend rc.
RUN 3 (065239): creation-retry loop works: click 0 no object (panel diff
4065 px), click 1 -> sig object 0xfda074 EXACT (deterministic address, 4th
independent sighting incl. production + t1254 bank). Then BREAK DIED
(channel dead right after REQ BREAK; pty ends without glibc text — t282's
fatal class, mechanism still unproven, but its rate here is WORSE than
documented: with settle, post-load BREAK died 4/6 reached-BREAK runs).
RUN 4 (065707): BREAK survived, armed 00FDA93B, quiet 120 s ZERO fires,
planets phase 7 clicks ZERO fires. value_at_scan=80 nonzero => even ONE
access (read!) would fire; nothing fired => after arming, NOTHING touched
byte 0xfda93b all session. Post-run: count still 80, sig intact, ZERO u32
pointer sites of OBJ anywhere in RAM (t249 S9 replicated in our own
session). screen_after_phases.png = PLANET DETAIL VIEW (hex grid, buildings)
=> sidebar clicks DRILL IN (list -> planet), they are not open/close
toggles; the alternating RESEARCH attempt also landed on planet rows.
RUN 5+6 (071355, 071722): 'reopen' phase (neutral starmap click 200,300 THEN
Planets button) — both died at BREAK (survival lottery, not phase logic).
RUN 7 (072240): first --heap-planets-blind run (arm the DETERMINISTIC slot
0xfda074+0x8c7 BEFORE the object exists; blind target REQUIRES
--expect-base): died at BREAK again.
RUN 8 (072827, --no-break): DECISIVE for the instrument. EXEC BPLM arms
FINE without BREAK (BPLIST shows it), the write event genuinely happened
(POST-PHASES sig-object count 1 — object created mid-phase by the reopen
clicks), and ZERO fire lines appeared. => THE FIRE PATH REQUIRES THE
BREAK-ENABLED DEBUGGER (t282's claim CONFIRMED by the negative arm).
--no-break is DEAD for hunting; kept in the script only for provenance.
COMBINED LAW: the only working flow so far = t283's (BREAK survives -> arm
-> RUN -> fire). t286's blocker is PURELY BREAK SURVIVAL (2/6 post-load
even with 45 s settle). t282's best class was BREAK at the QUIESCENT TITLE
SCREEN (3/3 with settle). RUN 9 = --break-early: BREAK+arm at the title
title screen, EXEC RUN, enter campaign (with boot-fire auto-resume watcher),
phases after. If the debugger survives the campaign LOAD with the bp armed,
the reopen click's alloc/reset/add path MUST fire it (blind slot = 0 at arm
in the loaded state, runs 7/8 measured, so no artifact ambiguity post-entry).

## S5 RUN 9 + BREAK-SURVIVAL CENSUS (this session, 9 reached-BREAK-or-armed runs)
RUN 9 (074516, --break-early first flight): BREAK at the QUIESCENT TITLE
SCREEN (45 s after boot, zero intervening ops) — DIED (channel dead right
after REQ 2 BREAK, pty ends clean, no glibc text). t282's "title screen 3/3
with settle" DOES NOT HOLD on this box today; the settle law is not
predictive. pty.log tell identical to runs 3/5/6/7.
BREAK-SURVIVAL CENSUS (t286 session only): post-load class SURVIVED runs
1,4; DIED 3,5,6,7. Title-screen class DIED run 9. ~2/6 where BREAK was
attempted with settle. Instrument consequence: the session script is only
the INNER loop; the OUTER loop must relaunch whole sessions until BREAK
survives (run 10 = background for-loop, 3 attempts, stops on 'armed:').

## S6 RUN 10 (074807) — EARLY-ARM FULL FLOW WORKED, ZERO FIRES; ring caught the RESET
BREAK survived attempt 1 (title class lottery confirmed: run 9 died, run 10
lived, same script). EARLY byte-at-arm MEMDUMPBIN FAILED (hdr OK, no file —
title-state dump quirk, val unknown -> no artifact rejection). Arming, EARLY
RUN, campaign ENTER with the bp live, base verified 0x1bf4d8, quiet+reopen
phases: ZERO fire lines (pty holds ONLY the arm + BPLIST echoes — checked).
RING-FINAL GOLD: slots 57-58 hold the list slot in state count=0
stamp+0x8c9=0xe, slots 59-60 count=80 stamp=0x8d — the RESET-then-REFILL
transition of t249's law captured between autosaves, WHILE the watchpoint was
armed at that very byte and never fired. Two readings left:
(A) save-state RESTORE drops heavy breakpoints (PING answers regardless —
    run 8 proved PING needs no debugger; so PONG post-entry proves nothing);
(B) the fire path dies post-restore while BPLM survives.
RUN 11 = POSITIVE CONTROL, decisive: --break-early arming the BIOS tick
lin:0x46C (t282's proven 18.2 Hz target) and letting the campaign load +
quiet phase run. Tick fires (artifact '00->xx' + walk stream) => restore KEEPS
bps and the fire path LIVES => the slot byte was simply never written at
0xfda93b after title-arm (address model wrong for the loaded state). Tick
silent => watchpoints are DEAD past a save-state restore => t286 closes as
"the instrument cannot cross a restore" and all future watchpoint hunts must
arm POST-load (t283 class) — the STATE.md t286 queue text needs that law.

## S7 RUN 11 POSITIVE CONTROL — INSTRUMENT VALIDATED rc=0 (wp-lin-0x46C-20261103-080919)
Same script, --break-early, target lin:0x46C (BIOS tick, t282's proven
18.2 Hz address). BREAK survived; armed; EARLY RUN; boot fires DRAINED with
EIPs (20eec6, feaa); campaign ENTER with bp live; BASE VERIFIED 0x1bf4d8;
quiet phase fired +2.0 s ('26 -> 27'), full stopped-state banked (BPLIST/CPU/
EV x15). DONE rc=0. THIS IS THE t286 DELIVERABLE: a fully scripted,
no-hand-holding watchpoint hunt that captures fire + register state.
LAWS ESTABLISHED (cited):
1. WATCHPOINTS SURVIVE SAVE-STATE RESTORE and the campaign load: the
   title-armed bp fired in the post-load quiet phase. t283's mandatory
   post-load re-arm is NOT a law of the instrument — it was a workaround for
   the BREAK-survival lottery, not for bp loss.
2. Paging OFF at fire time (cr0=00000010, cr3=0) — linear==physical stands
   (pointer-law compatible); run-10's zero-fires are NOT aliasing.
3. Fire lines arrive on the pty stream with a '(Running)' prefix when the
   CPU was RUNning under an early-armed bp ("(Running)LOG: DEBUG: Memory
   breakpoint : 0000:046C - 26 -> 27"); FIRE_RE matches unchanged.
4. BREAK survival is a pure per-attempt lottery at EITHER screen (title:
   died run 9, lived runs 10/11; post-load: lived 1,4 died 3,5,6,7).
   SOP: wrap the session in a relaunch loop (run-10 pattern: retry until
   'armed:' appears in the log) and accept ~40-60% per-attempt cost.
   t282's 'title 3/3 with settle' does NOT reproduce; settle is not
   predictive.
5. MEMDUMPBIN at title-arm time returns hdr OK but writes NO file (runs
   10/11) — byte-at-arm unknown in --break-early mode; artifact rejection
   is off there. The entry loop drains boot-stage fires instead.
HONEST NEGATIVE (the hunt question, UNRESOLVED): run 10 armed blind at
0xfda93b and the RING captured the list slot transition between its own
autosaves (57-58: count 0, +0x8c9 stamp 0xe; 59-60: count 80, stamp 0x8d —
t249's reset+refill law witnessed live for the FIRST time, between the
reopen clicks at 07:51:07/07:51:13) — yet ZERO fire lines all session while
the control proves bp+fire-path live in the identical flow. So the byte
values in RAM changed without the heavy-check firing at 0xfda93b. Candidates
[unverified]: the write goes through a path the per-instruction check misses
at that address class; or the autosave captured a state the bp was removed
from; or dosbox save/restore of the ring rewrites guest RAM in bulk without
checks and the transition I read is a RESTORE artifact of an older slot
(but 57-58 show count 0 which only exists mid-refill...). The planet-list
writer EIP remains UNWITNESSED. Next session's t288-class debugger work
should re-run run-10 ONCE more with --walk and per-fire EIP + a SECOND
control armed... only one bp allowed — so interleave: run 10 flow with the
tick control FIRST (fires drain), then... INCOMPATIBLE with one-bp law;
simplest next probe = rerun blind-planet-list hunt 2-3 attempts (lottery)
and grep pty for ANY 'Memory breakpoint' beyond arm/BPLIST echoes.
