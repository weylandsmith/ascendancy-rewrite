# _wip_t363r.md — t363R RE-LAND session (2026-11-09 ~23:15 EST) — COMPLETE

## Outcome
CODE LANDED. run_tests 206/0 (197 prior + 9 new pins). Mutation campaign
6/6 CAUGHT. Ledger 17/2 UNCHANGED (honest negative — no OQ row's named
closer touched; magnetron/Phase-Bomb HOME = ring field + carriesCode, C5
chooser NOT modelled, rows stay user-gated).

## Sequence of record
1. Sitting check NEGATIVE: live-timeline 8,917,535,608 B unchanged, 400 KB
   tail 16/16 rows turn 1086; r1_t85g_sitting.py NOT run (standing law).
2. Raw re-reads (work/r331_disasm.txt) banked to _wip_t363.md S6: mutators
   FUN_00049698/0x496e4/0x49624, admission FUN_000499f8, completion
   FUN_00049a34, upkeep FUN_0004a658 (full body), recalc FUN_00049acc, C2
   loop 0x42d09..0x42d5b. NEW from the re-read: fillFirstEmpty window is CAP
   (0x4964a), not all-25 (spec G3 shorthand superseded); the recalc zeroes
   +0x18 too (0x49af5); completion stores DWORD[+0x9e]:=0 (lane-local x).
3. Code landed per contract S5 items 1-5 (shipsim.h + shipsim.cpp):
   SimLane.closed; InvSlot/SimDesign/kCidx*/DERIVED lane-step pools; Ship
   recalc-owned fields + ring + laneToB/orderPayloadLane/speciesLaneTravel;
   BoundaryReport.laned; upkeep/refresh/mutators/carrier accessors/
   starArrivalComplete; tail order status->refill->refresh->march->upkeep;
   sweep re-grant REPLACED by upkeep(); digest extended; fromRecord imports
   verbatim with NO recalc (powerMax law).
4. INCIDENT (self-inflicted, recovered): the first mutation driver ran
   `git checkout -- shipsim.cpp` as its revert AFTER M1 — but the work was
   UNCOMMITTED, so the revert nuked every cpp edit. The header, the test
   file, and the WIP survived; all six patches were re-applied verbatim
   from the session transcript and re-verified by build + suite. LESSON
   (banked to memory): mutation-driver reverts must be `git stash`/file-copy
   based, OR checkpoint-commit before the campaign. Checkpoint e9c8bae was
   made before re-running the campaign — the second run was safe.
5. Pins test_shipsim_t363.cpp x9 (contract item 6 a-h + lane-arrival):
   burn-orders-pick, unaffordable (no burn no charges), payload gate, bit0-
   ring-runs, refresh (+0x42, 0-for-unlimited, window exclusive), recalc
   carrier law (14/28/-1/Cloaker), setSlot phantom, firstCarrier C2 shape,
   kind-2 lane arrival (admitted + closed-lane denied + no-gear denied).
6. MUTATION 6/6 CAUGHT: M1 bare-regrant (needed a pin FIX first — original
   pin was visible at the TAIL burn, not sweep-visible; re-scoped powers
   28/22 so only the sweep burn flips the pick — the first M1 run MISSED,
   which is exactly what the campaign is for), M2 skip-ring-on-bit0, M3
   charges-unnested, M4 refresh-operand +0x3e, M5 recalc-window inclusive,
   M6 phantom-rejected. scripts/r363r_mutate.py is the reusable driver.
7. Banking: ships.md S62 (law prose + census corroboration); pership-spec
   G9 bit-polarity correction IN PLACE; OPEN-QUESTIONS t363R note on OQ-019
   (row STAYS OPEN, strict-close); STATE.md NEXT -> t364 VERBATIM.

## Named divergences (in-code, honest)
- clearSlot idx>=25 refuses (vendor would corrupt memory; no cited law).
- designRow out-of-range cidx -> zero cat-5 row (vendor reads garbage).
- Completion kind==3 leg NOT modelled (unreachable from sole caller 0x4a33d).
- laneToB endpoint mapping (laneToB ? b : a) is the contract's flagged
  choice for the NOT-CITED galactic-frame transform (spec G-d); raw +0xa2
  := 1.0f iff target == lane[0] (A end) is what's stored.

## Facts for t364 (do not re-derive)
- Shield charges +0x90 are engine state (Ship.shields) zeroed-always and
  re-granted per affordable cat-1 slot; the fire-loop charge law 0x4a71f
  shares the body (S3c: three sites, one law).
- Kind-5 arrivals COUNT one assert per boundary (S4 item 4) — pin exists
  (shipsim_lane_arrival_t363 asserts==1); combat completion must keep it.
- firstCarrier(code) implements C2 eligibility verbatim (InSystem + slot,
  list order, no strength test) — the invasion leg of combat REUSES it.
