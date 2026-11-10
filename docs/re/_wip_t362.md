# _wip_t362 — MIXED-FLEET DEPARTURE LAW PARITY (2026-11-09)

## S0 Intake
- NEXT ACTION = t362 VERBATIM (STATE.md queue): "reproduce the vendor
  piecemeal-departure behavior (dwell expiry per ship) from the st4 DWELL law;
  parity test vs banked witnesses; aggregate oracle still passes." Mandate from
  the t361 mutation campaign (ships.md S60): pin the POWER-CLAMP-OPERAND path
  (clamp fires only when power<steps AND power!=walk) and the MARCH-SPENDS-
  NEITHER law.
- Sitting check NEGATIVE: timeline 8,911,989,574 B, 400 KB tail-seek, 16/16
  records turn 1086 (newest 44/45/46.sav = ring rotation). r1_t85g_sitting.py
  NOT run. Production :9 never signalled; game/ read-only; tree clean at start.

## S1 Witness census (scripts/r362_departure_witness.py, exit 0, output
## work/r362_witness.out) — banked t265 drive corpus, regimes A+B healthy,
## softlock window excluded by the mtime gap; corpus law verbatim from
## r265_pass2.py (file_mtime_ns window + dedup (file,mtime_ns) + in_game +
## turn>0 + bounded tail). 163,424 lines scanned, 602 in-regime rows.

MEASURED:
1. MID-TURN (same-turn consecutive rows) kind flips: ZERO. st5 same-turn
   x-deltas {0.0: 10267}. Corroborates S24 item 3 (one step per boundary) on
   the flip class, not just the coordinate class.
2. PER-BOUNDARY FLIP YIELDS per owner (first-row-of-turn-t vs
   first-row-of-turn-t+1, same slot):
     5->4: {1: 5 boundaries, 3: 2 boundaries}  (7 events)
     4->5: {1: 2 boundaries, 3: 2 boundaries}  (4 events)
   => SAME-OWNER MULTI-FLIP IN ONE BOUNDARY EXISTS (n=3 twice for 4->5, twice
   for 5->4). The t361 skeleton runs ONE executor pick per race per boundary,
   which cannot produce 3 same-owner kind flips in one boundary. Candidate
   model correction identified (see S2) — pending the issuer-site adjudication.
3. st4 rows 3150, off-32-grid: {} (0). Re-confirms S24 item 1 on a fresh pass.

## S2 Static sites (work/r331_disasm.txt verbatim; cross-checked with
## work/functions_full.tsv spans)
- kind-5 STORE sites are exactly two (matches the ai-dossier imm census):
  0x22243 and 0x2228f. Both live in the ISSUER family, NOT in the executor:
    fn 0x221c4 (0x221c4..): loops the ship list from FUN_00022304 (same list
      builder the executor uses at 0x4130f), keeps ships whose
      [ship+0x54]>>16 == ds:0x7458e (LOCAL race), per ship: call FUN_000220a8
      (0x2222e) -> store [ecx+0x59] := lane ptr (0x2223e) -> BYTE[+0x58]:=5
      (0x22243) -> call FUN_00021f58 placement (0x22247). A PER-SHIP LOOP:
      many ships can flip in one invocation.
    fn 0x222a4 (0x222a4..0x22339): single-ship variant (asserts args non-null,
      reads ds:0x13b98), same store 0x2228f + placement call 0x22298.
  Callers: fn 0x221c4 <- 0x28f8f (inside fn 0x284bc); fn 0x222a4 <- 0x15807,
  0x16f60. Other FUN_000220a8 callers: 0x43d0c, 0x49a6f (inside FUN_00049a34
  = the kind-2 completion body!), 0x49dc7/0x49e13 (0x49d2c family), 0x4cd0d
  (gizmo dispatcher 0x4ca50).
- Executor FUN_00041260 entry verbatim: ownership-bit gate 0x412c0
  ((1<<[edi]) & [edx+0x14|0x15]), FUN_0003ea08 call 0x412cf, list build
  0x4130f (0x22304), eligibility 0x41340..0x41357 (owner, POWER>0, kind!=1),
  sums +0x88/+0x94 banked. NO kind-5 store inside.
- Turn-tail FUN_0004a74c prologue verbatim (0x4a74c..0x4a7a6): WORD[+0x9c]:=0,
  call 0x4a99c, POWER store [esi+0x88] := eax at 0x4a76c — UNGUARDED; then the
  gizmo slot-refresh loop (0x4a77c..0x4a7a4: per non-empty slot,
  WORD[slot+1] := design[+0x4e]) — the t363 seam; then kind==5 gate 0x4a7a6.
- FUN_0002547c (the per-system exec driver, second executor caller 0x2554f):
  after call 0x41260 it reads the return in AH: 0x2555a test ah,ah -> 0x25560
  arm (call 0x49f28, call 0x39c10 = the mode==1 COMMIT arm), 0x25580 cmp ah,2 /
  cmp ah,3 je 0x25560; outer loops 0x255ba/0x255d0 iterate a table. [S2b: the
  sweep-repeat structure is still being walked — see S3.]

## S4 ADJUDICATIONS RESOLVED (static, verbatim, work/r331_disasm.txt)

Q1 RESOLVED — SWEEP-REPEAT IS REAL AND VERBATIM. Driver FUN_0002547c:
  0x2550c reloads the eligible-race count; 0x2551b..0x25531 walks every race
  entry, each: executor call 0x2554f, `or edi,eax` (0x25554), return-status
  byte ah=[esp+0x10]: ah==0 -> nothing; ah==1 -> call 0x49f28(ship,1); ah==2 ->
  call 0x39c10(ship,1); ah==3 -> call 0x49f28(ship,1) (0x25560/0x25570/0x25587
  — THE mode==1 COMMIT ARMS, matches the standing commit law); other -> assert
  0x8f5. After the full pass: 0x25525 `test edi,edi; jne 0x2550c` = RE-RUN THE
  WHOLE PASS while any race reported work. => multiple picks per race per
  boundary, one per sweep, MIN POWER first = PIECEMEAL DEPARTURE. The t361
  one-pick-per-boundary encoding is superseded by this verbatim leg + the S1(2)
  witness (3 same-owner flips in one boundary, owner 1 slots 17/20/29 at
  t1104->1105; owner 2 slots 12/21/23 at t1111->1112).
  MOVES re-grant is INSIDE each executor call (0x412cf -> FUN_0003ea08) =>
  re-grant happens PER SWEEP, not per boundary.
  Termination: each walked pick spends POWER (steps >= 1); POWER==0 ships fail
  the 0x4134e gate; loop drains to no-work. Tension noted honestly: S17 T4's
  "one sub-turn per day" mapping vs full-power drain per pump call — the sim
  encodes the verbatim repeat law; day-coupling stays INFERRED.

Q2 RESOLVED — kind-5 store sites are FOUR (grep `c6 .*58 05`):
  0x22243 (fn 0x221c4 per-ship loop, LOCAL race only via ds:0x7458e — cannot
    explain the witness flips, owners 1/2 are not local),
  0x2228f (fn 0x222a4 single-ship variant),
  0x49a74 (INSIDE FUN_00049a34 = the kind-2 completion body, now banked:
    gate call 0x499f8; kind==3 -> derive star from [[+0x59]+0xa]>>16 via the
    0x13bc5 base; call FUN_000220a8(0x49a6f); BYTE[+0x58]:=5; [+0x9e]:=0;
    [+0x59]:=lane ptr; [+0xa2] := 1.0f/0.0f by lane-end compare — the
    lane-frame entry stamp),
  0x4cd16 (gizmo dispatcher 0x4ca50).
  => The kind-2 arrival path RE-ENTERS lane transit directly in the completion
  hook — the corpus 5->4/4->5 frame-switch chains are the executor+completion
  interplay, NOT the local issuer loop.

Q3 HELD — T-8 dwell stasis vs T-10 queued-order suppressor stay distinct.
  T-10 decrement moves OUT of the executor block to ONCE per boundary (the
  0x3ac1c writer is an event handler, not the executor; sweeps must not
  re-decrement). t361 expiry pins (2->1->0->fire) preserved exactly.

EXECUTOR PICK LOOP re-read verbatim 0x41949..0x419b8: act==0 ships get the
decider call 0x40178 (local-race arm 0x41976..0x41987); MIN-POWER scan
`cmp best,[edx+0x88]; jge skip` (skip-on-equal => FIRST ties), act!=0 gate
0x419a7; picked -> 0x41e1e commit path; no pick -> ebx=0 return. Matches the
t361 encoding; the sweep-count was the ONLY executor law t361 got wrong.

## S7 COMMIT-EXIT RETURN LAW (verbatim, closes the status question)

Commit-path common exit FUN_00041260 tail 0x41b8f..0x41bb2:
  0x41b8f mov eax,[esp+0x39e] / sar eax,0x10 / test eax,eax
  0x41b9b jle 0x419c0          ; remaining <= 0 -> RETURN 0 (no work reported)
  0x41ba1 mov ebx,-1 / mov eax,ebx / ret   ; remaining > 0 -> RETURN -1
So the executor reports WORK iff REMAINING WALK > 0 after the commit: a ship
that still has walk left re-arms the driver repeat (0x25525); an ARRIVED ship
(remaining 0) reports 0 and does not repeat. All commit arms converge on this
exit (0x41b8f reached from 0x41b64/0x41b89/0x41cf1/0x41d13/0x41d2a/0x41daf/
0x41de8). Driver arms read AH: -1 -> ah 0xff -> NO commit arm fires (only edi
accumulates) — consistent with ah 1/2/3 being specific sub-arm statuses.
MODEL EQUIVALENCE (named, provable): sim status = steps-spent != 0. By the
walk law, d>0 => walk>0 => steps>=1, and remaining==0 <=> walk==d <=> arrived.
So "steps spent" and "remaining>0" differ only when a walk spends steps AND
arrives in the same call: vendor reports 0, sim reports nonzero. Consequence
tested: one extra no-op sweep (the re-pick finds the arrived ship act-cleared
or the race silent) — STATE-EQUIVALENT, and the sim's act-consumption law
(landingAttempt/stale-act clear act) makes the re-pick a no-op exactly as the
vendor's status-0 exit prevents it. DRAIN-TO-COMPLETION is the shared law:
a non-arrived ship is re-granted MOVES per sweep (0x412cf inside the
re-invoked prologue) and keeps walking until arrival or POWER==0.

## S6 REPEAT-TERMINATION LAW (decisive, this iteration)

Executor FUN_00041260 return values (edi = race-entry ptr; ebx = status):
  0x419c0 xor ebx,ebx -> return 0  (ownership-bit gate fail AND no-pick path)
  0x41a4a/0x41ba1/0x41d67 mov ebx,-1 -> return -1
  assert paths return ids (0x93e etc. — driver's "other" arm).
Driver FUN_0002547c reads status in AH ([esp+0x10] byte): ah==1 -> call
0x49f28(ship,1); ah==2 -> call 0x39c10(ship,1); ah==3 -> call 0x49f28(ship,1)
(0x25560/0x25570/0x25587). edi accumulates `or edi,eax` (0x25554) across the
race pass; 0x25525 test edi,edi jne 0x2550c repeats the pass.
=> WORK IS COMMIT-DEPENDENT, NOT PICK-DEPENDENT: a pick whose commit arm
reports status 0 does NOT set edi -> no repeat. The t361 assert-law pin
(kind-2 pick, orderType 0, acted==1, asserts==1 — one pick then stop) is
CONSISTENT with the repeat law precisely because the no-walk commit reports 0.
A walk that spends steps (kind-4 commit path) reports nonzero -> repeat.
Witness corroboration: S1 B2 (3 same-owner flips in ONE boundary, both owners,
twice each direction) — the repeat fired in the vendor.

MODEL: commitMove returns int status (0 = no walk committed; nonzero = steps
spent / state committed). advanceBoundary repeats the per-race pass while ANY
race's sweep committed work. Stale-act clear + T-10 decrement stay ONCE per
boundary (sweep==0) — honest simplification named: the vendor re-runs the
stale-act leg every executor invocation (incl. its 0x40178 re-decide), but
focus cannot change mid-boundary in the sim, so the observable effect is
identical while no AI is invented.

## S5 t362 CODE PLAN (executed):
1. advanceBoundary executor phase -> repeat-until-no-work (per sweep: per race
   ascending: regrant, stale-act, one MIN pick, commit, assert law). "Work"
   proxy = power decreased OR kind changed OR act changed [INFERRED substitute
   for the unread executor return code at 0x41e1e — named, honest].
2. T-10 decrement hoisted to once per boundary (pre-sweep-read/post-decrement
   order kept: suppresses on the value read, decrements even with no pick).
3. BoundaryReport.sweeps field (pin surface).
4. laneMarch made a PUBLIC test seam (the march-spends-NEITHER mutant is
   invisible at boundary observation — the per-sweep re-grant overwrites moves,
   exactly as in the vendor 0x412cf — so the law is pinned at the seam).
5. Clamp mutant pin: NON-INTEGER walk clamp case d=416 (2.6 sugar), power=2,
   moves=10 -> steps=3>power -> walk=2.6*2/3=1.7333 (NOT power=2 — the mutant
   signature), pos 277.333, power 0, moves round(8.2667)=8, not arrived.
6. Mixed-fleet departure parity test (ascending-fuel one-per-sweep order,
   multi-flip same boundary per the S1(2) witness shape) + dwell-expiry
   interleaving test.

Q1: does ONE turn boundary run FUN_00041260 once per race, or N times
    (repeat-until-no-work)? S17 T4 says REPEATS sweeps while any ship reports
    work; t361 encoded one call. S1(2) witness (3 same-owner flips/boundary)
    supports N>1. Walk the 0x2547c/0x16eb0 call frames for the loop.
Q2: are the observed 4->5 flips driven by fn 0x221c4 (local-race per-ship loop
    — but the drive corpus has no human input, and S24 shows zero placement
    jitter, while fn 0x221c4 always calls placement 0x21f58 which jitters %200)
    or by the executor's case-1 gradient hop (S17 T5)? If placement always
    jitters and corpus st4 rows are 100% on-grid, fn 0x221c4's placement leg
    must exit before the jitter (FUN_00021f58 has early returns) — verify the
    early-return guard in 0x21f58.
Q3: the t361 dwell word (T-10) is a SIM-level countdown; the queue row says
    "dwell expiry per ship" drives piecemeal departure. Keep the two laws
    distinct: T-8 dwell (kind-4 stasis between boundaries) vs T-10 queued-order
    suppressor. Do NOT merge them.

## S8 MUTATION CAMPAIGN (t362 pins, each mutant applied alone, rebuilt, run)
1. clamp scale power/walk instead of power/steps -> CAUGHT
   (shipsim_power_clamp_operand_t362 pos 277.333 fails). NOTE: swapping the
   clamp CONDITION (power<walk) is VACUOUS — integer power makes the
   conditions identical; only the scale factor separates the readings. The
   t361 campaign's "clamp operand" mutant class needs this correction.
2. march decrements MOVES -> CAUGHT (march_spends_neither_t362 seam pin).
3. driver never repeats (t361 behavior) -> CAUGHT x20 tests
   (piecemeal_departure acted==3, noop_sweep sweeps==2, +18 collateral).
4. T-10 decrement per sweep -> CAUGHT (dwell_law_and_expiry_t361 +
   dwell_suppress_across_sweeps_t362).
ALL FOUR CAUGHT; run_tests back 197/0 after restore (git diff shipsim.cpp
shows only the intended t362 edits).

## S9 TEST-DEBUG MEASUREMENTS (real execution facts, worth keeping)
- Silent sweeps RE-GRANT MOVES (0x412cf unconditional per executor call), so
  the remaining-walk word is commit-exit STATUS, not durable state: after a
  clamp walk leaving remaining 9, observed moves == 10 (re-grant), power 0.
- Landing scatter (T-6, 3 draws %1000-500/axis) fires on every orderType-1
  arrival under the no-slot default — landed positions are NOT targets; pins
  must assert arrivedFlag/act==0, not coordinates.
- shipsave_ring flakiness: ring saves touched 19:04-19:05 mid-run (capture or
  game running); shipsave_reader_and_base_vote_t360 flaked once, clean on
  re-run. NOT a t362 regression — environmental. (Sitting check earlier said
  turn 1086 stable; the ring FILES rotate even when the turn does not.)
