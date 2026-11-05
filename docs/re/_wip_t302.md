# t302 WIP — debugger witness run with the RE-ARMED class legs

## Assignment (STATE.md t301 NEXT ACTION)
Run ONE debugger session battery with scripts/r299_leg_session.py as re-armed
at t301 (LEGS = router 0x30d08, cos_entry 0x26818, cos_hdlr 0x26b34, cos_s3
0x27e80, cos_s5 0x2925c, btn_entry 0x30ad8, btn_hdlr 0x336b4, batmode_dead
0x1aef8). Via bash scripts/r299_relaunch.sh (3 attempts, OUTDIR
work/r1/t299).

## Success tell / control logic (carry-over, do NOT re-trip)
- SUCCESS: any "STOP ... leg=" line in the run's session.log.
- BUILT-IN POSITIVE CONTROL: End-Turn + FLEET clicks happen while btn_entry /
  btn_hdlr / router are armed and those clicks are PROVEN to work (t300). If
  btn_* does NOT fire on them, the INSTRUMENT is dead -> attribute to harness,
  do NOT run the same battery a 3rd time.
- If cos_*/btn_* fire but map clicks do NOT: the Icarus-view battle chrome is
  BatControl (class table phys 0x247850, entries 0x15630/0x156d4/0x16420 —
  t301 S4) which is NOT in LEGS -> add batctrl legs and rerun ONCE.
- --control-click default IS 0 now (t301 pixel law: rect 557,403-587,433 is
  BLACK in the Icarus view; patched this session, py_compile OK).
- bank_stop dumps record head (magic 0x12345678, NAME@+0x20) per register
  candidate -> every stop NAMES the dispatching window.
- Fixed harness traps: MEMDUMPBIN filenames bare+relative UPPERCASE; 0000: =
  selector-0 junk; arm only AFTER campaign load (mode-bound GetAddress);
  EXEC answers while RUNNING -> pty code-view line is the only stop detector;
  FLEET reopen after a click battery FAILS (one battery per sitting, view 0
  only); post-load autosave slots may hold PREVIOUS-run bytes.

## S0. PRE-RUN STATIC PRE-CHECK (this session, payload work/ascend_payload.bin)
- Prologues for the potential batctrl legs are code-shaped, ready to add if the
  adjudication demands: img+0x15630 `53 51 89 c3 89 d1 f6 c1 04` (class-entry
  shape, same `f6 c1 04` test as cos_entry 0x26818), img+0x156d4
  `56 57 55 81 ec 8c 00` (handler shape), img+0x16420 `53 51 56 57 55 83 ec 6c`.
- CAUTION: the class table at FILE offset 0x88400 (= phys 0x247850 - P0) holds
  PRE-RELOCATION statics (0xa80, 0x1c158, 0xb24...), NOT physical pointers —
  t301's "slot 1 == 0x30d08 in every table" law was measured from RAM dumps.
  Do not re-derive table contents from the payload file.
- --control-click default patched 1 -> 0 this session (t301 pixel law);
  py_compile OK. Run launched via scripts/r299_relaunch.sh (loop pid recorded
  in work/r1/t302-relaunch.log).

## Run log

### S5. ATTEMPT t302-4 (run work/r1/t299-leg-20261105-004605) — FULL WITNESS,
### SESSION rc=0, 3 WINDOW-NAMED STOPS, POSITIVE CONTROL CONFIRMED
- Flow exactly as designed: post-run-immediate cos_hdlr fire (banked, leg
  dropped) -> liveness=True -> rearm 7 -> endturn-p1 btn_hdlr fire (banked,
  dropped) -> rearm 6 -> press-1 NOFIRE -> press-2 cos_s3 fire (banked,
  dropped) -> rearm 5 -> `press 2: advanced=True` (turn 1086->1087) -> FLEET
  -> row93 Icarus (sprites [(48,151,296)] planet (439,331) empty (236,200)) ->
  3 battery clicks NOFIRE -> FLEET reopen fails x3 (t300 law) -> SESSION END
  rc=0. Guest ALIVE throughout (autosaves every 10 s until teardown 00:53:07).
- THE THREE STOPS (hits.json verbatim):
  1. `post-run-immediate` leg=cos_hdlr (file 0x26b34, COSMOS table slot 2)
     eax=0xfd2310 wrec magic OK name='COSMOSWnd', edx=0x3b.
  2. `endturn-p1` leg=btn_hdlr (file 0x336b4, type-0 button table slot 2)
     eax=0xfd6190 name='NEXTTURN', **edx=0x7 — the windows.txt
     `SENDMESSAGE 7` for NEXTTURN VERBATIM as the dispatch msg**. POSITIVE
     CONTROL: working clicks DO execute the class msg layer; t299/t300's
     zero-fires were the wrong legs + dead detector, not a bypass law.
  3. `endturn-p2` leg=cos_s3 (file 0x27e80, COSMOS table slot 3)
     eax=0xfd2310 esi=0xfd2310 name='COSMOSWnd', edx=0x0 — the click that
     ADVANCED THE TURN (press 2 advanced=True) reached COSMOS slot 3.
- BATTERY NEGATIVE (now with a LIVE guest + armed un-witnessed legs
  {cos_entry, cos_s5, btn_entry, router, batmode_dead} through all 3 clicks,
  and pty fire-scan per leg = 0): sprite (48,151), planet (439,331), empty
  (236,200) in the Icarus system view execute NONE of the armed class-table
  slots. [inferred] map-click handling does NOT go through COSMOS table slots
  0/3/5, the type-0 button class, or router slot 1 — it likely enters via
  cos_hdlr slot-2's internal branch (the ONLY COSMOS leg that ever fires,
  on msg 0x3b) and never re-consults the table. NEXT PROBE (t303): msg-census
  mode — BP at cos_hdlr entry ONLY, and at the 5 `call [ecx+4]` sites
  (img 0x26eda/0x30d02/0x7a7eb/0x7aa3e/0x7b020, t301 S6.1), banking edx per
  hit for sprite/planet/empty clicks -> names the map-click msg -> its handler.
- pty fire census for this run: cos_hdlr 1, cos_s3 1, btn_hdlr 1, router 0,
  cos_entry 0, btn_entry 0, cos_s5 0 (batmode_dead un-armed after drop...
  armed but never hit — BatModeWnd record state stays inactive in view).
- LAW (instrument): drop-witnessed-legs + BPDEL-fired-index-before-RUN +
  liveness-by-autosave + BREAK-window re-arm = the ONLY viable code-BP
  multi-stop protocol on this build. codified in scripts/r299_leg_session.py.

### S4. ATTEMPT t302-3 (run work/r1/t299-leg-20261105-002628) — RESUME FIX
### WORKS (liveness=True), but the RE-ARMED HOT LEG re-freezes the guest
- BPDEL fired-index -> RUN -> `resume liveness=True` (autosave growth in 12 s)
  -> BREAK ok -> re-armed 8/8 ok=True -> RUN. THE FIX IS VALID: the guest ran
  again and saved.
- ~2 s later the pty shows the cos_hdlr code-view + `I-> _` prompt AGAIN:
  msg 0x3b (same eax=0xfd2310 win, edx=0x3b) re-struck the re-armed hot leg
  and bank_stop's chain path re-froze it (press 1/2: advanced=False). The
  0x3b pump is PERIODIC — any armed hot leg (router slot1, cos_hdlr slot2)
  guarantees a re-stop within seconds regardless of clicks.
- FIXES APPLIED (gen-3 instrument, py_compile OK):
  1. `witnessed` set: a leg banked once is NEVER re-armed (drop policy);
     rearm arms only un-witnessed legs; when all are witnessed the session
     goes leg-free and the battery runs with the guest clean.
  2. post-rearm: poll_stop (budget 8 s, recursion-capped at 3) instead of
     pty_new — a hot-leg stop right after rearm RUN is BANKED not swallowed.
  3. bank_stop names the WINDOW: dumps head of every candidate reg, keeps the
     magic-0x12345678 one (at cos_hdlr: eax=window record, esi=class table —
     the old code dumped esi's blob first and never named the window).
  4. relaunch tl 1800 -> 3600 (battery + rearm churn needs room).
- EXPECTED gen-3 flow: post-run-immediate fire (cos_hdlr or router) -> banked,
  leg dropped -> liveness -> rearm 7 -> maybe 1 more hot fire banked+dropped ->
  End-Turn advances -> FLEET -> battery; btn_entry/btn_hdlr fire on the
  End-Turn/FLEET clicks = POSITIVE CONTROL; sprite/planet/empty stops name
  their window -> OQ-019 selection witness.

### S3. RESUME DEFECT — MECHANISM PINNED IN SOURCE (work/r1/dbx-build/
### dosbox-x-master, read this iteration; explains t302-1/-2/-3 identically)
1. `RUN` (debug.cpp ParseCommand RUN ~95652): sets debugging=false, runs
   `inhibit_int_breakpoint=true; DEBUG_Run(1,false)`, then
   `DOSBOX_SetNormalLoop()` — ACK "OK" is sent on ACCEPTANCE (debug_mcp.cpp
   ProcessControlCommand: resume cmds reply BEFORE DEBUG_ExecuteCommand).
2. `DEBUG_Run` (debug.cpp ~165288): `skipFirstInstruction = true; CPU_Cycles =
   amount; (*cpudecoder)();` — one instruction budget.
3. THE DEFECT: heavy-debug check runs at the TOP of the core loop, BEFORE the
   instruction (core_normal.cpp:182 `if (DEBUG_HeavyIsBreakpoint()) {
   FillFlags(); return (Bits)debugCallback; }`).
   `DEBUG_HeavyIsBreakpoint` (debug.cpp ~224334) order: cpuLog -> logHeavy ->
   zeroProtect -> `if (skipFirstInstruction) {skip=false; return false;}` ->
   `CheckBreakpoint(SegValue(cs),reg_eip)` (debug.cpp ~: CheckBreakpoint:
   BKPNT_PHYSICAL && active && location==GetAddress -> lastTriggered, return
   true). Code BPs are NON-`once` (BP command -> AddBreakpoint(seg,ofs,false))
   and under C_HEAVY_DEBUG there is NO 0xCC patching (Activate() is a no-op
   for PHYSICAL, `#if !C_HEAVY_DEBUG`) — so the address stays hot.
4. EMPIRICAL: after every bank_stop's RUN the pty shows `(Running)` ACK then
   the debugger prompt `I-> _` again — the guest RE-STOPPED at the same EIP
   without executing the instruction; autosave cadence dead (50.sav 23:30:41,
   none until teardown 8 min later). Both t302 instrument runs and both
   pre-fix runs show identical death. [inferred] the exact skip-consume site
   (dynamic-core interaction) — the re-stop itself is MEASURED.
5. FIX (classic): delete the FIRED bp by index before RUN, re-arm after the
   guest is verifiably alive (autosave-file growth + BREAK window). BPDEL takes
   a hex index: `EXEC BPDEL <idx>` (debug.cpp BPDEL: GetHexValue then
   DeleteByIndex; '*' = all). BPLIST order != arm order — parse the index from
   the address line. Implemented in bank_stop + rearm_after_resume (t302).
6. SECOND OBSERVATION (3 samples: runs 225819, 230846, 232859):
   msg edx=0x3b (59) hits COSMOS slot-2 handler within ~1 s of RUN, before any
   click — consistent with a periodic/timer message; NOT yet a law. Expect
   stop churn at router/cos_* legs once re-arming works; battery tags
   disambiguate.

### S2. ATTEMPT t302-2 FIXED INSTRUMENT (run work/r1/t299-leg-20261104-232859)
### FIRST REAL CLASS-DISPATCH STOP BANKED + NEW BLOCKER: guest never resumes
### after a CODE-BP stop (watchpoint stops DO resume — t290 flow).
- Fixed instrument worked end-to-end on detection: "FIRE-CANDIDATE
  post-run-immediate after 0.0s" -> "STOP leg=cos_hdlr eip=0x1e5f84
  file=0x26b34 eax=0xfd2310 ecx=0x0 edx=0x3b esi=0x247a4c ebp=0x2bc35c
  esp=0x2e9108". esi holds the COSMOS CLASS TABLE phys 0x247a4c (t301 law);
  the +0x90 dump is the class METHOD table (slots 0x1f0158/0x1eb330/0x1eb3f8/
  0x1f0608/0x1f0b40/0x1ea81c...), NOT a window record — bank_stop's wrec
  magic-check correctly found no magic there (win_from_esi recorded raw).
  MEANING: the generic msg dispatcher called COSMOS table slot 2 (0x26b34)
  with eax=window 0xfd2310, message edx=0x3b (59) — within ~1 s of the armed
  RUN, BEFORE any click. The dispatch law is LIVE-CONFIRMED.
- BUT after bank_stop's "EXEC RUN" (REQ 34, hdr OK): guest NEVER resumed.
  Autosave ring died at 50.sav 23:30:41 (BP hit ~23:30:48 blocked the 51st;
  resume 23:30:50; NO 51.sav through teardown 23:38:41 — 8 min, cadence 10 s).
  pty shows only "(Running)" ACK then silence. Clicks did nothing -> the
  End-Turn press loop failed x3 (rc=1) and the battery never ran. The
  relaunch loop misread its own success tell ("BANKED A LEG STOP" -> stop)
  so no further attempts — the tell fired on a PARTIAL win.
- t299-t301 RE-ADJUDICATION: their pty logs scanned with the NEW pattern:
  ALL ZERO fires (12 runs, batmode-era + t301 leg sets). So their zero-fires
  were REAL zero-fires (pattern bug only hides stops that actually happen),
  consistent with t301's wrong-legs explanation. The t302-1 run (225819) and
  killed t302-3 (230846) each show the fire in pty that their dead pattern
  missed — the game was frozen at the BP the whole time, explaining
  "advanced=False" x3 without any game-side mystery.
- CONTROL STATUS: btn_entry/btn_hdlr-on-End-Turn positive control STILL UNRUN
  (guest dead before clicks). Do NOT conclude the instrument is dead — the
  fire proves arming+detection both work now; resume is the open defect.
- RUNS CONSUMED this iteration: t302-1 (bug repro), t302-2 (banked stop +
  blocker), t302-3 (killed, pre-fix), plus 2 lottery/channel losses (232811,
  230758). Old runs archived: work/r1/t299-pre-t302fix/.

### S1. ATTEMPT t302-1 (run work/r1/t299-leg-20261104-225819) — INSTRUMENT
### DEAD-DETECTION BUG FOUND: FIRE-PATTERN MISMATCH (the t299-t301 zero-fires
### were partly THIS bug, not the game)
- Arming perfect: BPLIST 8/8, MEMDUMPBIN control MATCH=True, base
  B=0x1bf4d8 as expected, ring loaded t=1086 ships=30.
- mcp-pty.log line ~208 (right after "EXEC RUN"): the DrawCode stop render
  `1E5F84 56 push esi1E5F85 57 push edi...` — **cos_hdlr (file 0x26b34, COSMOS
  table slot 2) FIRED within seconds of the armed RUN** (before End-Turn),
  with a mem-watch line `ss:[002E9140]=3C7` and run-on data containing
  `_0FD231047A4C00000003B1E5F84`.
- The fire-detection regex was `0160\s*:\s*001E5F84` (full CS:LINE form). This
  build's pty NEVER emits that form for stops — DrawCode prints bare 6-hex EIP
  (no CS, unpadded), opcode glued to mnemonic, run-on lines. => poll_stop could
  NEVER match; the stop was never banked; the guest sat FROZEN at the BP.
- Downstream misattribution: End-Turn clicks (511,67) at a frozen CPU do
  nothing -> "press 1/2/2: advanced=False" x3 -> "NEGATIVE: could not advance
  one turn" rc=1. VISION on 12_ewc0.png: clean strategic map, turn 01086, NO
  popup — the screen was fine; the CPU was stopped.
- CONSEQUENCE (binding): t299/t300/t301's zero-fire batteries ran with the same
  dead pattern; their NOFIRE lines cannot distinguish "code didn't run" from
  "stop undetected + frozen guest". The t301 arming-failure narrative stands
  (legs were wrong), but the run-level zero-fires are now WEAK evidence.
- FIXES APPLIED (scripts/r299_leg_session.py, py_compile OK):
  1. leg_pats -> `(?<![0-9A-Fa-f])<6hex> [0-9A-F]` (matches the DrawCode form;
     regression-checked: fire line matches; "Set breakpoint at 0160:1E5F84",
     BPLIST lines, REQ echoes, and the observed mem-watch run-on all NO-hit —
     lookbehind kills hex-preceded runs, arm lines end at the address).
  2. The `s.pty_new()` right after the armed RUN SWALLOWED the first fire line
     -> replaced with `s.poll_stop("post-run-immediate", budget=6.0)` so an
     early fire is banked with regs + window-record NAME.
  3. --control-click default 1 -> 0 (t301 pixel law) — done pre-launch.
- Attempt t302-2 (230758) + t302-3 (230846) ran BEFORE fixes 1/2 landed
  (script loaded at start) — both invalid as tests of the fixed instrument;
  t302-3 killed mid-run. All scratch procs verified dead (structured match;
  substring pgrep self-killed the searching shell TWICE this session — the
  BLOCKED.md law is stricter than written: even `grep "[r]299"` self-matches
  when the pattern is IN the shell cmdline; use basename(argv0) matching).

