# _wip t361 — PER-SHIP ENGINE SKELETON (shipsim.{h,cpp})

## S0 Pre-flight
- Sitting check FIRST: NEGATIVE — live-timeline.jsonl 8,897,010,542 B at
  2026-11-09 15:05, 400 KB tail-seek, 16/16 records turn 1086;
  r1_t85g_sitting.py NOT run; production :9 untouched; game/ read-only.
- Assignment: STATE.md NEXT = t361 VERBATIM — rewrite/src/game/shipsim.{h,cpp}:
  ship list, per-ship dwell countdown, order apply at turn boundary per
  pership-spec (2); determinism pins FIRST (seeded RNG must match the
  campaign.cpp LCG law); table-driven unit tests for dwell expiry + order
  transitions. S59 L2/L4 consumption rules honored via shipsave.h (the
  skeleton consumes Record; no parser re-derivation here).
- shipsim.{h,cpp} do not exist yet (verified by wc). No file regenerates
  docs/re/* (standing BLOCKED.md trap checked at landing).

## S1 Disputed-input adjudication: executor POWER pick (MIN vs MAX)
pership-spec §2 turn frame says the round-robin "picks MIN POWER [+0x88]
(strict <, first-in-list ties)"; ai-dossier §5 t179 P1 says the loop "tracks
the candidate with MAX [+0x88] POWER among ships whose act is set" citing
0x4199f `cmp eax,[edx+0x88]` / 0x41aaf `mov cx,[edx+0x88]`. RESOLVE by raw
disassembly of work/ascend_payload.bin (runtime addr == file offset, imagebase
0, OQ-008 CLOSED) before encoding either.

RESULT: MIN stands (pership-spec §2 + ships.md S17 T4, t183 Ghidra
decompile-verified verbatim: "picks the ONE with MINIMUM fuel [+0x88]
(strict <, first-in-list on ties) that has an order [+0x5d]!=0").
ai-dossier §5 t179 P1 "MAX [+0x88]" wording is a misreading of the same
threshold-replacement scan. Raw facts (objdump -b binary -m i386 of
work/ascend_payload.bin, runtime==file offset, imagebase 0) — read honestly:
  0x41340-0x41357  eligibility collect (owner race match via [rec+0x54]>>16,
                   power>0 `cmpl $0x0,0x88; jle skip`, kind!=1
                   `cmpb $0x1,0x58; je skip`); sums +0x88/+0x94 banked;
                   "any act set" flag 0x38c := -1 at 0x413b3. CONFIRMED raw.
  0x4138d          candidate pointer array build (esp+idx*4). CONFIRMED raw.
  0x41949-0x419b8  a threshold-replacement scan: Intel `cmp 0x88(%edx),%eax`
                   (cand - threshold) with jge=continue reads MIN-replacement
                   (replace iff cand < threshold), matching T4 — BUT the
                   0x41952 xor %ecx,%ecx on this path zeroes the threshold
                   (cx word), under which no live ship (power>0) ever
                   replaces, so THIS block is NOT the sweep entry as read;
                   the sweep pick's true init was not re-derived this
                   session (flagged, budget-bounded). The MIN/strict-</
                   first-ties STRUCTURE rests on the t183 decompile.
  0x419cf-0x419f1  ASSERT law verbatim: kind==3 -> call 0x39894; kind!=4 ->
                   mov $0x93e,%ebx; call 0x2a428. CONFIRMED raw.
  0x41a1c-0x41a45  stale act target ([+0x5e] != current object) -> 0x41a30
                   movb $0x0,[+0x5d] + re-decide 0x40178. CONFIRMED raw.
  0x40eb4          sort comparator verbatim: *(int*)a deref, [ship+0x52] -
                   [ship+0x52] — the sort operand IS the +0x52 dual-use
                   field (ETA day-stamp per t101); ai-dossier's "descending
                   design power" label vs this operand is DISPUTED; the sim
                   encodes the VERBATIM comparator (ascending on +0x52,
                   stable) and cites both labels.
  0x40ec0          ship-list builder raw: stride `add $0x162`, cap gate
                   `cmp $0x6b`, live gate ds:0x43489>>16, dead skip on
                   owner>>16 == -1 — A1/A3 re-confirmed at the code level.
Also read 0x3ac1c (QUEUE-TURN writer): `mov %ax,0xac(%edx)` where EDX is the
pending-slot object from 0x3ac14 call 0x3ac880 (coordinate->slot converter),
guarded by [edx+0x35]==0 pairs and +0xab==0x05/'05' tests — the t46-era
"ship+0xab/+0xac" field labels are on the COMMAND/pending object, confirming
spec G-a: the queued-order FIELD HOME on the ship record is NOT cited. The
skeleton therefore models the suppression BEHAVIOUR with a sim-level field
and marks the home unresolved. Never invent the offset.

## S2 Build plan
- shipsim.h: OrderKind enum {0..5} verbatim spec §2; Ship struct = the cited
  consumed fields ONLY (kind +0x58, act +0x5d, actTarget +0x5e, orderType
  +0x67, power +0x88, moves +0x94, integrity +0x8c, maxIntegrity +0x98,
  pos +0x9e); Lcg (FUN_0007824f form, state*0x41C64E6D+0x3039,
  (state>>16)&0x7fff — campaign.cpp:548 worldNext verbatim); ShipSim owning
  the list + turn counter + queue countdown + assert counter.
- Turn boundary per spec §2 turn frame: (1) per-ship turn tail: +0x9c zero,
  POWER refill trunc([+0x18]*(1+clamp((T-[+0x52])//100,0,10)/10)) [t101 leg3
  25/35 exact + 35/35 bounded], MOVES := [+0x10] re-grant [combat §1];
  (2) ship list sorted DESCENDING design power [FUN_00040ec0+0x40eb4];
  (3) queue suppressor: matching queued type with countdown != 0 suppresses
  the move and decrements [ships.md §10 item1 + §11 QUEUE-TURN LAW];
  (4) executor sweeps: ships with act==0 re-decided; act target stale ->
  act cleared + re-decide [0x41a30/0x41a45]; pick candidate among act-set;
  (5) ASSERT law: after movement kind must be 3 or 4 else assert id 0x93e
  at 0x2a428 — model as a counted violation, never crash (headless).
- Dwell law T-8: kind-4 ships do not march between turn rows (net 0.00 over
  150-turn st4 runs, ships.md S24 item 1) — encode as the no-op between
  boundaries; displacement resolves INSIDE the boundary.
- Stubs with EXPLICIT unimplemented flags for t363/t364 scope (gizmo effects,
  combat): the skeleton applies ORDERS, not effects. No silent stubs.

## S3 BUILD RESULT (MEASURED 2026-11-09)
- rewrite/src/game/shipsim.{h,cpp} + tests/test_shipsim_t361.cpp x11;
  CMake: shipsim.cpp into ascend_core, test into run_tests. run_tests 190/0
  (baseline 179 + 11). Golden LCG vectors (offline-computed from the banked
  FUN_0007824f law): seed1 16838,5758,10113,17515,31051,5627; seed7 19564,
  9806,10868,22674,32531,3365 (state after 2 draws 0x264e4f5d); seed2024
  2012,10608,2336,14785,205,18486; seed7 %200 pair (164,6), %1000-500 triple
  (64,306,368) — pinned in shipsim_lcg_law_t361 + the placement test.
- Design adjudications applied: walk guard = kind 4 verbatim (S17 T1), so
  commitMove only walks kind-4 ships; kinds 1/2 cross-system via T-4 issuer;
  kind-5 marches in the turn tail only. T-6 completion clears act (order
  consumed — else a dwelling ship re-scatters every boundary, forbidden by
  the S24 stasis witness). Dangling kind-5 lane HOLDS state (no cited law).
- MUTATION RESULTS (run_tests shipsim): max-pick 3 fail CAUGHT;
  no-dwell-decrement 7 fail CAUGHT; tie-toward-away 5 fail CAUGHT;
  power-clamp-operand 0 fail NOT CAUGHT; march-spends-MOVES 0 fail NOT
  CAUGHT — both uncaught paths are exactly t362's mixed-fleet parity
  surface; banked in ships.md S60 as the honest t362 test mandate.
- Ledger: NO row touched (skeleton per D2=(b); OQ-019 residues close on user
  ruling only). 17 closed / 2 open unchanged.
