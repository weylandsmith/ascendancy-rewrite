# t327 WIP — DEBUGGER-SESSION TOOL v2 (scripts/r1_dbg_session.py)

## S0. Task and state
- Assigned: STATE.md NEXT ACTION t327 VERBATIM. Sitting check NEGATIVE
  (playcap newest turn 1086, tail-seek measured 2026-11-07).
- Production :9 untouched (ps: Xvfb :9 pid 1461 + dosbox-x pid 136359).
- Tool exists in pieces: scripts/r299_leg_session.py (1877 lines) holds ALL
  proven machinery — FirePat (t305 law, class at :99), launch shape (:405,
  dbg binary + pty stdio + MCP out-dial + core=normal conf), arm_all (:555),
  bank_stop (:623, regs+ret_stack+win-rec+clip), resume_and_rearm (:757,
  t302 freeze protocol), arm_census (:887, pmode gate + census-ctl control),
  disarm_run (:930), census_window (:959, 6-stop cap), census_click (:997,
  the t303 unit), whole-log pty census (:1427+). r322_relaunch.sh = the bash
  attempt-loop shape (short-circuit rc=0+census probe; rc=2 never retry).

## S1. Known-positive facts (measured, for the verification targets)
- t308 DAT_43504 leg = w43504_28ec2 (file 0x28EC2). RECORDED CENSUS DATA:
  run work/r1/t299-leg-20261105-140250 whole-log census
  {w43504_28ec2: 1, btn_hdlr: 8} rc=0, 6 star windows measured;
  run 143815 census {w43504_28ec2: 1, btn_hdlr: 3} rc=0. hits.json: every
  banked stop btn_hdlr ret0_file=0x3177d (star clicks) / 0x56cdd (NEXTTURN
  control). _wip_t308.md:94 "THE FIRE (3rd occurrence, REPRODUCED 3/3)" —
  third occurrence is INSIDE a pty log (line 341), verify below.
- t319 poster leg = pump_entry_56b5c (file 0x56B5C); expected-callsite datum
  = ret0 of an E8 caller: call site = ret0_file_off-5; the msg-4 road site is
  0x54ac5 (i.e. ret0_file_off 0x54aca). Caller table in LEGS comment
  (r299_leg_session.py:294-306): 0x53fa3 d / 0x54976 3 / 0x54ac5 4|0xc / ...
- EXPECT_BASE 0x1BF4D8, P0 = base-0x88 = 0x1BF450; linear = P0 + file off.

## S2. Design (decided)
- r1_dbg_session.py IMPORTS r299_leg_session as the plumbing library (no
  re-derivation; FirePat/launch/resume laws stay single-sourced) and adds:
  (1) LEGSPEC declarative table {name: {addr, expect_callsite, hot}};
  (2) generic phase runner (star-click / hold / pre-turn / shipclick steps
      declared per session, not task-baked);
  (3) offline mode: --offline-census RUN_DIR [--expect leg=N,...] replays the
      whole-log FirePat census against a recorded mcp-pty.log and validates
      expectations (no launch needed) — THIS is the mutation-test surface;
      (4) built-in relaunch loop (r322 shape) so a future task = ONE command;
      (5) bank-on-exit: atexit persist(hits/probes/census/verdict) + SIGKILL
      teardown by recorded PID only.
- Verification: offline census MUST reproduce recorded counts for the t308
  runs (140250, 143815) and the t319 run; mutation test = bogus pattern ->
  census 0, exit clean. THEN one live launch of the t308 legset through the
  tool (star-click phase) to prove the session runner end-to-end.

## S3. Tool shipped + verification results (MEASURED 2026-11-07)
scripts/r1_dbg_session.py (t327 v2). Interpreter law: run with
~/.hermes/hermes-agent/venv/bin/python (system python3 has NO PIL; the r293
import chain needs it).
OFFLINE VERIFICATION (replay recorded runs; 0 drift vs their own census lines):
- t308 run 140250: 9/9 counts reproduce EXACT (w43504_28ec2 1, btn_hdlr 8);
  expects w43504_28ec2>=1 PASS, btn_hdlr==8 PASS, ret0 btn_hdlr@0x3177d PASS
  (tag star0_226x238#0). RC=0.
- t308 run 143815: w43504_28ec2==1 PASS, btn_hdlr==3 PASS. RC=0.
- t319 run 030727: 5/5 EXACT (pump_entry_56b5c 1, p54a47 0, p54a88 1,
  s2_56c74 1, s2_56cda 106); ret0 pump_entry_56b5c@0x54aca PASS (tag
  post-rearm, edx=4 banked). RC=0.
MUTATION TESTS (bogus pattern must classify zero-fire, not crash):
1. offline bogus leg name -> counted 0, verdict PASS(==0), RC=0 [no crash]
2. offline wrong count expect (btn_hdlr==99) -> FAIL, RC=1
3. offline bogus callsite (@0xdeadbe) -> FAIL, RC=1
4. unparsable expectation -> HARNESS ERROR, RC=2
5. live-mode bogus leg -> preflight HARNESS ERROR RC=2 (no launch)
6. busy MCP port -> preflight RC=2 (no launch)
7. unit: fabricated last-4 collision (0x336b4 vs 0x136b4) -> preflight RC=2
   (t305 audit law enforced mechanically for the first time)
LIVE RUN: launched detached (work/r1/t327/live-verify.out), t308 legset
(w43504_28ec2,btn_hdlr) phases baseline,star6,hold expects >=1/>=1 +
ret0@0x3177d, attempts 2. Result appended below when done.

## S4. Doc-drift check (task-mandated)
- xsend arg1 = WINDOW TITLE law: corroborated docs/re/selfplay.md:751
  (tclick-by-ID history: the blocker title matches 'DOSBox-X', xsend refuses
  'warning' titles) + _wip_t293.md:67 usage; NOT stated in
  dosbox-debugger.md -> stated in the new §TOOL v2 instead.
- MEMREAD real-mode-only (debug.cpp:2983) — cited in the tool header; the
  doc's read-surface law (ring = measurement surface) is the t286/t283
  material already in dosbox-debugger.md.

## S5. LIVE END-TO-END RESULT (MEASURED 2026-11-07, attempt 1, rc=0 PASS)
Run dir work/r1/dbg-t327v-20261107-050546 (verdict.json pass=true):
- launch -> PONG -> BREAK lottery won -> title -> campaign ENTER -> drain ->
  ring base B=0x1bf4d8 match -> phases baseline(15s, 0 stops, BPLIST proved
  arms 0160:1F2B04 btn_hdlr + 0160:1E8312 w43504_28ec2, disarm clean) ->
  star6 phase: 23 green candidates (t308b law count reproduced exactly),
  click #0 (182,284) diff=94712 ENTERED, WITNESS DELTA 0x256825(Icarus) ->
  0x255bc5(Vega) — byte-identical datum to t308 run 143815; pip loop stopped
  early as designed -> hold window -> whole-log census {w43504_28ec2: 1,
  btn_hdlr: 2}.
- VERDICT: w43504_28ec2>=1 PASS(1); btn_hdlr>=1 PASS(2);
  btn_hdlr@0x3177d PASS (tag star0_182x284#0). rc=0, loop stopped attempt 1
  per r322 short-circuit law.
- Teardown: SIGKILL dosbox 157944 + xvfb 157940 (recorded PIDs); bank-on-exit
  artifacts census.json/hits.json/probes.json/verdict.json all present.
- Offline replay of the FRESH run: 0 drift vs its own census line, rc=0 —
  the tool's live and offline census paths agree.
- Production :9 untouched: post-run ps = Xvfb :9 pid 1461 + timeout 136357 +
  dosbox-x 136359 (unchanged).
WALL CLOCK: attempt 1 = 05:05:46 -> 05:10:21 (~4.6 min) — single command,
zero hand-holding. That is the t327 payoff metric vs the t306-t323 chain.

## S6. Ledger
t327 is a tooling task: NO ledger row closed (strict-close unaffected).
OQ-005 / OQ-016 / OQ-019 statuses untouched; ledger_audit must stay OK.
The tool's practical effect on the ledger: t328+ witness work now runs as
one command with mechanical law-enforcement + expectation verdicts.
