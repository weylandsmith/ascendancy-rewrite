# t104 WIP — F8b OBSERVATION (order-completion POWER drain)

## Assignment (STATE.md NEXT ACTION)
The t101/t102 ATTRIBUTION of the drain leg 0x41ded..0x41e19 (ZEROS
[ship+0x94] MOVES and [ship+0x88] POWER, folds delta into stack budget)
must be OBSERVED on a live record, not just attributed. Closure = sample
sequence power>0 -> 0 on one tracked record across a turn boundary.
Negative = drain absent at arrival -> F8b mechanism reopens, +0x52 ETA
theory needs a re-read.

## Key realization (session start)
live-timeline.jsonl mtime 2026-10-26 15:44 unchanged -> no new sitting;
BUT the banked 5.69 GB stream from the user's t37..t1131 campaign already
contains tens of thousands of End-Turn autosave rows, each with ship_raw =
177-u16 verbatim window per slot (watcher r1_playcap_watch.py:93, stride
0x162). AI races reach order completion EVERY turn of that campaign. The
closure sample is therefore computable OFFLINE from banked capture — the
"capture vehicle FOR FREE" branch the assignment names. No dosbox harness
needed unless the stream yields nothing.

## Signature law (derived from cited statics)
Per ship slot (u16 word index = byte offset / 2):
  POWER   = word 68  (byte +0x88; panel-law byte-pinned t101)
  INTEGR  = word 70  (byte +0x8c)
  MOVES   = word 74  (byte +0x94)
  ETA     = word 41  (byte +0x52; reused as transit ETA per aicode S7.5)
  b5d     = word 46 & 0xff  (byte +0x5d order-state; dispatch 0x41e1e)
  b5c     = word 46 >> 8    (byte +0x5c neighbor)
  b5e/b5f = word 47 lo/hi
Across trusted consecutive rows with turn+1 (End-Turn boundary):
  DRAIN-SIGNATURE: POWER(T)>0 -> POWER(T+1)==0  (state cleared -> b5d==0,
      MOVES re-granted full per FUN_0004a658, ETA re-stamped ahead >T).
  CONTROL: POWER stays >0 (ship not completing, or recharge post-drain).
Static 59/60.sav ground truth (t102): five zero-POWER race0 rows carry
b5d==0 and [rec+0x52] > T 5/5.

## Ordering argument (why the boundary sample should SEE the drain)
aicode S2 map: master 0x24f24 runs ship-orders 0x25023 BEFORE per-race
turn-tail 0x25083/0x250a5 (recharge FUN_0004a74c @0x3e7b0 inside). If the
completion leg zeroes POWER in the order-executor pass, the recharge pass
would RESTORE it at save time — the five static zero-POWER rows then imply
the drain is POST-recharge (t102 prose). The boundary census decides:
  - rows with POWER==0 & MOVES==full & b5d==0 recurring across turns
    == post-recharge drain OBSERVED (F8b closure class satisfied);
  - POWER never 0 at boundaries -> five static rows unexplained -> honest
    negative, mechanism reopens.

## Probes
P1 schema sample (done above): keys incl ship_raw 32 slots x 177H.
P2 stream census tool scripts/r1_t104_drain_watch.py (r1_stream, trusted
   order, per-slot boundary transitions + intra-turn transitions).
## P2 RESULT (stream census, 44,928 rows, 17,170 boundary pairs, 22 s):
DRAIN power>0 -> power==0 ACROSS TURN BOUNDARY EXISTS, 4 cases:
  owner0 slot24 day780->781 P8->0 M4->0 ETA786->783 (P AND M zeroed same
    step = completion-leg signature; persisted: still 0 at next sample)
  owner2 slots 4/11/15 day1253->1254 (THE t1253 WAR SITTING):
    slot4  P4->0 I0->20 M2->2 ETA398->1264  b5d 0x1->0x0
    slot11 P8->0 I0->20 M4->4 ETA581->1260  b5d 0x1->0x0
    slot15 P8->0 I0->20 M4->4 ETA672->1264  b5d 0x1->0x0
  — b5d CLEARED 3/3, ETA RE-STAMPED AHEAD OF T 3/3 — EXACTLY the static
  five-row signature (t102: b5d==0 AND +0x52 > T 5/5 on 59/60.sav).
CONTRAST mid-turn drains (133 owner0 same-day P->0, b5d unchanged, ETA
unchanged) = firing/upkeep burns, NOT the completion family.
REFILL power==0 -> >0 concentrates on BOUNDARIES (owner0 120, o1 6, o2 4)
== the per-turn recharge pass 0x3e7b0 -> FUN_0004a74c restoring at End-Turn;
the 4 boundary DRAINS are zeroing that lands AFTER recharge within the same
turn tick (command-exec tail 0x2554f runs after per-race 0x25083/0x250a5
per the t90 master map) — the ordering that t102 could only infer.
owner65535 = free-record sentinel (316 b-zero rows), excluded from meaning.

## P3 RESULT (continuity probe scripts/r1_t104b_continuity.py, 76 lines):
t1253->1254 boundary is THE WAR TURN (t85g sitting: battle frames visible
mid-t1253 — slot11 INTEGRITY 20->12->4->free(owner 65535,st0)->20 restored;
slot4 INTEGRITY 20->16->12->7, POWER decrements 14->4 mid-turn (combat+
travel burns), slots 4/11/15 DEATH events to free mid-t1253 then slots
REFILLED by full-INTEGRITY records same turn, then t1254 shows slot4
P0 dsgCHANGED(2->4), slot11/15 P0 dsg SAME, xyz FROZEN at last value,
ETA re-stamped 1260/1264 (== T+11? law candidate: 0x40e96 idiv quotient).
=> the t1254 zero rows ARE post-death RECYCLED records (owner-2 rebuild or
free-record reuse), NOT continuity-continuous tracked ships. The boundary
"drain" in P2 at t1253->1254 FAILS the tracked-record continuity test.
slot24 t780->781: owner 2 -> owner 0 (recycle across owners), P8->0 M4->0.
LESSON: autosaves land at End-Turn + player actions; AI-turn internal
(order-completion) moments are NOT sampled; slots churn via death/reuse —
a P2-style transition census MUST require same-owner same-design
continuity or it counts recycles as drains.

## HYPOTHESES for the static five P0/b5d=0/ETA-ahead rows (t102 signature):
  H1 order-completion drain surviving after the recharge pass
  H2 ship BUILT after its race's recharge pass (t102's own alternative),
     P=0 stale until NEXT turn's recharge; +0x52 reused as ETA stamp
  H3 death-recycle artefact (P0 window residue)
## P4 RESULT (continuity-GATED census scripts/r1_t104c_fulllaw.py RC=0):
Gate = same owner, same design (+0x10), state present both sides, so a
death/recycle can never masquerade as a drain (t104b lesson applied).
FULL SIGNATURE OBSERVED — 4 distinct events (6 pairs, dedup):
  slot3 d369 own0 P4->0 M4->4 ETA345->345 b5d0x3->0; still 0 through d372
  slot14 d678 own0 P3->0 M4->4 ETA599->599 b5d0x3->0; t679 P4 (NEXT-BOUNDARY
     REFILL == recharge pass FUN_0004a74c), then P2 b5d0x1 = new order
  slot10 d945 own0 P3->0 M4->4 ETA525->525 b5d0x3->0; t946 P5 refill
  slot28 d1017 own0 P8->0 M6->6 ETA825->825 b5d0x3->0; zero across >=5
     samples incl (pending persist tail)
LAW OBSERVED: completion DRAIN = P->0 WITH order-state +0x5d CLEARED 3->0
in the same sample pair. The t104 P2 census without the gate counted 133
mid-day P->0 — b5d-unchanged burns are the PART class (b5d 0x0:57, 0x1:55,
0x7:2 = firing/travel burns per 0x4a2d4..0x4a314), the b5d-cleared family
is the completion leg. b5d==0->0 drains (57) are a zero-state ship burning
power = upkeep/fire, NOT completion (dispatch 0x41e1e requires state!=0).
WHAT THIS CLOSES: the drain executing (POWER goes to 0 on a live tracked
record as orders complete) is now CAPTURE-OBSERVED on the user's campaign
stream, and the refill-at-next-boundary behaviour confirms the recharge
pass restores it exactly one End-Turn later (slot14: zero d678 -> P4 t679).
WHAT THIS DOES NOT CLOSE (honest negative, strict-close): the ETA leg.
OBSERVED completion events keep ETA UNCHANGED (345->345 etc., all ETA < T =
birth-day semantics); the static five zero-POWER rows in 59/60.sav carry
[rec+0x52] > T — a DIFFERENT sub-signature. t1253->1254 war-turn boundary
rows (ETA 398->1264 etc.) FAILED continuity (owner/design change after
death = free-record reuse, t104b), so they do not count as evidence either.
=> the five static rows remain [unverified mechanism]; ETA re-stamp
provenance (0x40e96) still cited-static-only. Ledger row STAYS OPEN.
Also observed: PERSISTENCE spans 3+ days (slot3 zero 369..372+) proves the
zero OUTLIVES the immediately-following recharge for some records — but
autosaves are End-Turn/action-gated, so "post-recharge drain" vs "built
after its race's recharge pass (H2)" remain INSEPARABLE on this stream:
the autosave ring cannot sample mid-turn tick internals.

## P5 ADJUDICATION (59+60.sav static rows vs the stream, decisive):
The t102 "five zero-POWER rows" on 59.sav AND 60.sav (both T=1254, anchor
B=0x1bf4d8, deterministic Factory needle) are slots 2/4/11/12/15, all
own2 (Ungooma) st1 b5d0 cap12, ETA 1257..1264 AHEAD of T=1254.
t104b ALREADY PROBED slots 4/11/15: they DIED mid-t1253 (owner -> 65535,
state -> 0, INTEGRITY bled 20->12->4->0 through battle frames) and
REAPPEARED at t1254 with design/owner-reset records (slot4 dsg 2->4,
xyz frozen, ETA re-stamped 1260/1264). => THE FIVE ROWS ARE POST-DEATH
FREE-RECORD REUSE OCCUPYING EXACTLY THE WAR-TURN DEATH SLOTS (3/5 probed
directly; slots 2/12 same family own2 st1 ETA-ahead, not death-probed —
t85c independently placed four Minion deaths elsewhere 0/5/8/12, so the
Ungooma fleet also lost ships). The t102 hypothesis "mid-transit rows
whose completion leg drained POWER to 0 post-recharge" is REFUTED as the
mechanism of THOSE ROWS: P=0 is a freshly-reused record awaiting its
race's next recharge (refill-at-boundary census: owner2 boundary refills
4, consistent); ETA-ahead is the 0x40e96 order stamp on the new orders.
MYSTERY CLOSED BY SUBSTITUTION, not by drain observation.
UPDATE (verify-tool run): the death census over trusted t1253 rows shows
ALL FIVE slots 2/4/11/12/15 state->0 mid-turn (plus 19/21/23) — 5/5
death-probed, not 3/5. t85c's target list r1_t85g2_slots.py had exactly
these slots ("Ungooma slots that died").

## WHAT THE CAPTURE DID OBSERVE (the t102 named closure path):
Completion drain EXECUTING on continuous tracked records: 4 events
(6 pairs), every one: P>0 -> P==0 WITH order-state byte +0x5d cleared
0x3->0 in the same sample pair; MOVES net-unchanged (zero leg then
FUN_0004a658 re-grant between autosaves, consistent); POWER restored at
the NEXT day boundary (slot14 P0@d678 -> P4@t679; slot10 P5@t946;
slot28 P8@t1018) == the FUN_0004a74c recharge pass exactly one End-Turn
later. PART class (b5d unchanged) = 115 same-day burns = travel/upkeep
consumption 0x4a2d4..0x4a314, NOT completion (dispatch 0x41e1e needs
state != 0). RESIDUAL kept honest: autosave granularity cannot time-stamp
drain-vs-recharge WITHIN a turn tick; and the observed events carry
b5d BEFORE == 0x3 (state domain semantics only partially mapped t96).
Verify tool scripts/r1_t104_drain_verify.py four legs.
