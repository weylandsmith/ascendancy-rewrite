# t299 WIP — DEBUGGER SELECTION/ORDER WITNESS (BPLM on the batmode legs)

Session start 2026-11-04 ~18:20 EST. Fresh session; resumed from STATE.md alone.

## Pre-flight (verified this session)
- Production :9 ring tail: last rows all t=1086 (save slots cycling 41-60),
  file mtime 18:15. NO new turn => NO new sitting => r1_t85g_sitting.py NOT
  required. (332,094 lines; unique tail sequence ends (1086,'53.sav').)
- Instrument exists: work/r1/bin/dosbox-x-dbg (t282 build), skeleton
  scripts/r1_wp_session.py (MCP listener + pty + scratch + BPLM + dump_stopped),
  relaunch-loop precedent scripts/r286b_relaunch.sh, drive skeleton
  scripts/r298_order_session.py (client-rect-bounded finders already fixed).
- REFUTED-ROUTES respected: NO savestate restore in the dbg build (t288), NO
  member-index-as-linear arms (t286b), NO fleet-row-by-rank (t298), NO fourth
  scripted release-dosbox mouse launch.

## S1. INSTRUMENT SEMANTICS RE-READ FROM SOURCE THIS SESSION
(work/r1/dbx-build/dosbox-x-master/src — all [verified] in-tree)
- debug.cpp:6665 DEBUG_HeavyIsBreakpoint(): the ONLY heavy path that evaluates
  breakpoints; called at the TOP of the instruction loop
  (core_normal.cpp:182, core_dyn_x86.cpp:466/558/565, core_dynrec.cpp:269...).
  Consequence [inferred, law-7-consistent]: the reported EIP is the instruction
  AFTER the storing instruction, so the writer = the instruction immediately
  preceding reported EIP (decodable by disassembling backwards from EIP-P0).
- debug.cpp:819 CheckBreakpoint: BKPNT_MEMORY_LINEAR uses `address =
  bp->GetOffset()` DIRECTLY as a physical Bitu => BPLM operand is guest
  PHYSICAL == guest LINEAR (paging off, cr0=10/cr3=0 per t286 law 1). No
  selector arithmetic.
- debug.cpp:2908/2934 + 4721 DEBUG_Run: `EXEC RUN` and `EXEC RUNWATCH` both
  call CBreakpoint::ActivateBreakpoints() (:790 -> every bp Activate(true));
  under C_HEAVY_DEBUG Activate() writes NO code bytes (the 0xCC patching is
  inside `#if !C_HEAVY_DEBUG` :720) — the heavy debugger never modifies guest
  memory to break. Safe for checksums and for the game.
- debug.cpp:2949 STEPIN exists over the wire and stays stopped (one
  instruction inside DEBUG_Run(1,true)) — the per-leg single-step instrument if
  a fire's attribution is ambiguous.
- ControlServer_Poll is pumped BOTH inside DEBUG_Loop (:5267, stopped) AND as a
  TIMER tick handler (:6243) => EXEC also answers while the guest runs
  [verified present in source; live behaviour while running NOT yet measured].
- P0 LAW CROSS-CHECK vs the t286b pty panel: fire EIP 0x1f231f == file 0x32ecf
  + 0x1bf450, and CS selector 0160 with EIP printed as the linear value =>
  linear = P0 + file_offset with P0 = B - 0x88. The relocated immediates t298
  measured (ds:0x43508 -> imm 0x285508) therefore say: **ds:0x43508 has guest
  physical 0x285508 at base 0x1bf4d8** (P0 0x1bf450 + obj1 0x82bb0 + 0x43508).

## S2. SESSION DESIGN (scripts/r299_leg_session.py)
Skeleton = r1_wp_session.py (MCP direction law, pty isatty gate, BREAK lottery
relaunch loop, scratch game-wp assert, private Xvfb, core=normal, -time-limit,
kill-by-recorded-PID, OWN ring dir).
PHASES, ONE breakpoint armed at a time (fire line prints a useless address for
BPLM — one bp => any fire is ours):
  A  BPLM <lin(ds:0x43508)>  = WRITER CENSUS of the order-destination global.
     Idle drain first (t297-A proved it has non-order writers), then the click
     battery; every fire banks (wall-clock, EIP, file offset, EV eip/ebp/eax/
     ecx/edx/esi/edi/esp). Answers: does the PUBLISH leg 0x1baa7 EVER run, and
     who else writes it.
  B  BPDEL * ; BPLM <lin([win+0xb7])>  = SELECTION/MODE witness: does a click
     on an in-system owner-0 kind-4 ship produce a 00 -> 02 transition at the
     SELECT leg, or zero fires (dies at the hit-test).
Deliverable (iii) — the batwin instance address law — is pinned OFFLINE first
(S3) because the ring already carries full RAM.

## S3. WIN-PIN ATTEMPT (offline, t298 run-3 save 52, B=0x1bf4d8, P0=0x1bf450)
MEASURED (scripts live at work/r1/t299_winpin.py):
- The physical value P0+0x1aef8 (= 0x1da348) occurs EXACTLY ONCE in the whole
  17 MB Memory member: ring-MEMBER 0x247978 (guest-linear 0x2478f0). t298's
  single-hit law REPRODUCES on two independent runs (t298 save 52, t297 save 44
  — same member address).
- That member is INSIDE the obj1 data image (data members span
  0x242088..0x28c15b), i.e. file offset 0x884a0 = data-seg 0x58f0 — a STATIC
  record, and the neighbourhood is a table of relocated code pointers
  (0x1da04c, 0x1f0158, 0x1da348, 0x1dcca8, 0x1f0608, 0x1dde2c) interleaved with
  small ints (0x24, 0x27, 0x1ee, 0x60) and float-shaped filler 0x3c8efa35.
- CONSEQUENCE (binding for this task): a live heap window INSTANCE that stored
  the handler would make the count >= 2. One hit means either the window is a
  STATIC singleton or dispatch reads the template, not the instance. The
  template base (and thus the handler-field offset K) is NOT derivable from
  this dump — do not guess it.
- THEREFORE deliverable (iii) (batwin instance address law) is pinned LIVE: on
  any hit at batcon 0x1b91c, EAX = win (t297 re-read calling convention), so
  the register dump gives the instance address directly. No static pin needed.

## S4. CODE BREAKPOINTS BEAT WATCHPOINTS HERE (source-measured this session)
- reg_eip holds the GUEST-LINEAR code address (t286b proof: fire EIP 0x1f231f
  == file 0x32ecf + P0 0x1bf450; the pty panel prints CS=0160 with that same
  value) => a plain `BP <seg>:<linear>` matches at the top-of-loop check
  `GetLocation() == GetAddress(cs, reg_eip)` (debug.cpp:830).
- DEBUG_HeavyIsBreakpoint (debug.cpp:6665) evaluates CheckBreakpoint EVERY
  instruction on every core, and under C_HEAVY_DEBUG Activate() writes NO 0xCC
  (the patch block is `#if !C_HEAVY_DEBUG`, :720) — so code breakpoints work
  without touching guest memory.
- Fire lands AT the leg's first instruction (the check precedes Fetchb), so
  registers show the leg's ENTRY state — exactly what the questions need
  (batcon entry: eax=win, ecx=modifier, edx=pending clip).
LEG TABLE to arm (linear = session P0 + file offset; P0 = B - 0x88):
  0x1b91c batcon entry   0x1ba39 SELECT success   0x1ba5e dl==1 order relay
  0x1baa7 PUBLISH         0x1bad3 planet order     0x1b114 mode-2 deselect
PLAN (SUPERSEDED by S5 — arming one-at-a-time is impossible while running, see
S5.2/S5.6): drive a click battery, bank (leg, EIP, GPRs, clip kind, clip object
-> ship slot) per fire.

## S5. SESSION IMPLEMENTED — scripts/r299_leg_session.py + r299_relaunch.sh
Corrections found while building (each forced by a source measurement):
1. CODE breakpoints (not watchpoints): stop lands AT the leg's first
   instruction; C_HEAVY_DEBUG adds no 0xCC; no baseline-artifact law.
2. ARM AFTER CAMPAIGN LOAD, NEVER AT THE TITLE: debug.cpp:483 GetAddress
   evaluates AT ARM TIME (seg==CS -> SegPhys(cs)+offset); the title is
   real-mode DOS. Arm gate: stopped with CS read live + P0 <= EIP <
   P0+0x8CC83, retry RUN->BREAK up to 4x.
3. ACTIVATION LAW (debug_mcp.cpp:559 + debug.cpp:762): AddBreakpoint does NOT
   Activate(); only RUN/RUNWATCH call ActivateBreakpoints() — an `EXEC BP`
   issued while the guest runs is INERT. So: arm ALL legs while stopped, RUN
   once, attribute every stop by EIP.
4. MEMDUMPBIN addressing fixed: MEMREAD is real-mode-only (debug.cpp:2984) and
   `0000:` hits LinMakeProt's selector<8 rejection (debug.cpp:460) ->
   mem_no_address -> the t283/t286 "hdr OK, no file" symptom. Mid-game form:
   `MEMDUMPBIN 0160:<linear>` (paging off; SegPhys(cs)==0 inferred from EIP
   carrying the full linear). Built-in control: dump at the armed batcon linear
   must equal payload bytes at 0x1b91c (MATCH logged honestly).
5. Fire detection = pty code-view line "0160:00XXXXXX" for an armed leg; chain
   detection banks a second stop per click (batcon->select->relay walks);
   stopped-oracle: if the EXEC-while-running probe answered NEGATIVE, any EXEC
   reply mid-battery means STOPPED (probe banked in probes.json either way).
6. Ship identity comes from the CLIP (edx -> {kind,obj} -> slot via member =
   value+0x88), never from the fleet-row position (t298 refutation).
Launch: scripts/r299_relaunch.sh (3 attempts, stop on first banked leg stop),
venv python (PIL), Xvfb :97, port 55999, tl 1800, run dir
work/r1/t299-leg-<stamp>, console work/r1/t299/attempt-N-console.log.

## S6. ATTEMPT-1 MEASUREMENTS (run t299-leg-20261104-195933, crashed post-arm)
POSITIVE INSTRUMENT FACTS (all from that run's session.log):
- BREAK lottery WON at the title with settle=45; EXEC RUN resumed; campaign
  entered on the FIRST Return-to-Game click (orange 0.679 -> 0.003, ring
  loaded t=1086 ships=30) — the r293/t292 drive laws hold on the dbg build.
- ARM-TIME WINDOW IS REAL: post-load BREAK caught cs=0160 eip=0x2284f5 —
  inside the payload image at P0=0x1bf450 (file 0x690a5) — so the pmode gate
  passes on the first try at the map screen.
- ALL SIX LEGS ARMED AND LISTED: '00. BP 0160:1DA564' ... '05. BP 0160:1DAD6C'.
  BPLIST prints BP %04X:%04X (offset TRUNCATED to 16 bits in the listing only —
  the stored location is the full GetAddress value; do not re-derive the linear
  from BPLIST text).
- CODE-BP FIRE LINE CONFIRMED FORMAT (from t286 pty evidence): the code view
  prints '0160:00214141 8B35...' — the detection regex must be
  CS:%04X \s*:\s* linear:%08X.
OWN BUGS (fixed same session; NOT instrument laws):
1. poll_stop formatted the DISPLAY strings (leg_lines values) with :08X ->
   ValueError 'Unknown format code X for str' one click after arming. Fixed:
   arm_all precompiles leg_pats; poll_stop uses them.
2. MEMDUMPBIN REJECTS ABSOLUTE FILE PATHS: the argument tail runs through
   GetHexValue's expression parser, where '/' is DIVISION — an absolute path
   makes the whole command fail 'Invalid memory dump arguments' (debug.cpp
   ParseMemoryDumpArguments :2176 + GetHexValue expression loop :1910..). THE
   FIX: bare relative filenames (emulator cwd = the run dir; launch uses
   cwd=self.out). Also: MEMDUMPBIN's length argument is parsed as HEX (sent
   {n:X}).
3. ParseCommand UPPERCASES THE WHOLE LINE INCLUDING THE FILENAME
   (debug.cpp:2197 `for (auto &c : copy_str) c = toupper(c)` — verified in
   source AND measured: asked 'mem_control_001dad6c.bin', on disk
   'MEM_CONTROL_001DAD6C.BIN'). Attempt-2's Python existence check missed the
   good dump and the 0000: fallback OVERWROTE it with GDT-slot-0 junk — so the
   MATCH=False control was MY overwrite bug, not an addressing law. Fixed:
   check fname.upper(), single CS: attempt. THE 0000: JUNK FACT STANDS as a
   law: MEMDUMPBIN 0000:<X> dumps ~selector-0-mapped bytes (t283/t286's dumps,
   if any ever landed, were THIS junk — treat any old MEMDUMPBIN-based claim
   with suspicion).
4. Escape-ladder gap: after closing the system view, fleet_open rails==0 is
   satisfied while still IN the system view, so the ladder exits early and the
   next FLEET click does nothing (attempts 1-3 views 1-3 all 'diff 0/132').
   Not fixed (only view 0 matters for this task's question).

## S7. FIXED-SCRIPT RESULTS (3 attempts, runs -201408/-201757/-202146, all rc=1)
IDENTICAL CLEAN NEGATIVES x3 (instrument healthy every run):
- pmode arm window won at attempt 0 each time (cs=0160, eip=0x21411f/0x214141 =
  file 0x54CD0-ish in-image); 6 legs armed; EXEC-while-running probe ANSWERED
  (e.g. eip=0x214115, rtt 0.05 s) => EXEC answers while the guest runs; the
  stopped-oracle is INVALID on this build (fires must be detected via the pty).
- End Turn x1 advanced t1086->1087; FLEET opened (diff 122756 rails 188); row
  93 -> system view star='Icarus'; finder found the tan sprite at (48,151,296px)
  — the SAME validated t297/t298 coordinates; planet (439,331); empty (236,200).
- Clicks sprite/planet/empty: ZERO pty fire lines, ZERO stops, ring kept
  autosaving (game demonstrably RUNNING, never frozen at a bp).
INTERPRETATION LIMIT (why run 4 is required): batcon 0x1b91c sits BEHIND the
msg-4 router branch 0x1b070 ('IF [ebp+0.af] != 0 -> call 0x1b91c ecx=1', t297
verbatim). Zero fires at the 6 downstream legs is consistent with BOTH (a) the
hit-test returning null for every click (the t298 hypothesis) AND (b) msg 4
never reaching BatModeWnd at all. Arm 0x1b070 (router) + 0x1aef8 (handler
entry) to separate them — this is deliverable (i) in one launch:
  handler fires + router fires + batcon zero  => hit-test-null law CONFIRMED
      live (and the router stop banks [win+0xaf] directly: the pending clip!).
  handler zero                                => synthetic clicks deliver NO
      msg to BatModeWnd -> the whole scripted-mouse class gets a MECHANISM for
      REFUTED-ROUTES (t298's 'not refuted' becomes a cited negative).
RUN 4 = --views 1 --legs handler,router,batcon,select,deselect (Icarus view is
reached every run; the ship in view need not be slot 8 for the router answer).


## S7 RUN 4 (loop3 attempt-1 = work/r1/t299-leg-20261104-205111) —
HANDLER+ROUTER-ARMED NEGATIVE, AND IT IS ATTRIBUTABLE
- 8 legs armed incl. handler 0x1aef8 and router 0x1b070 (BPLIST verbatim:
  0160:001DA348, A4C0, AD6C, AE89, AEAE, AEF7, AF23, A564).
- MEMDUMPBIN control MATCH=True (dump law fixed: uppercase fname, relative
  path, seg=CS). Instrument integrity proven live.
- Choreography good: press-1 advanced, EVENTWIN Escape law held, post-turn
  t=1087 owner0 n=30 cand=[8], FLEET opened (diff 122756), row-93 ->
  Icarus view, sprite (48,151) found by the validated finder.
- Battery: sprite/planet/empty clicks -> NOFIRE x3 (25s budgets). pty
  'Memory breakpoint' count = 0 (the 9 hex-address lines are my own BP
  commands echoed, not fires). SESSION END rc=1 hits=0.
- DECISIVE CONTRAST (same session, same click channel): the FLEET button
  click PRODUCED an effect (ring diff 122756), the row-93 click PRODUCED
  the view change, the earlier turn-advance click worked. So synthetic
  clicks DO reach the game. Yet the BatModeWnd msg-handler ENTRY (0x1aef8,
  windows.txt attribution) never executed during ship/planet/empty clicks
  in the system view.
- CONCLUSION (cited, measured): ship selection in the system view does NOT
  dispatch through 0x1aef8's msg layer. The t297 static claim '0x1ba8c
  leg = MOUSE-REACHABLE order publication' is REFUTED as stated: those
  legs are behind a router that these clicks never wake. t298's zero-fire
  is now EXPLAINED, not mysterious.
- Two live hypotheses remain for WHO handles system-view ship clicks:
  (H1) a different window (BatModeWnd may be battle-only or windows.txt
  attribution is wrong); (H2) the main loop hit-tests mouse state directly
  (INT 33h polled struct) without entering any msg-dispatch handler.
  Both are answerable by ONE differential probe: arm 0x1aef8 + click the
  FLEET button (known-good click). Fires => H2-style local law for the
  system view (router really is click-gated elsewhere). Zero => 0x1aef8 is
  not on the live msg path at all -> windows.txt attribution dead, whole
  batmode leg map needs re-verification from windows.txt.
- Also banked: EXEC answers while guest runs (probe said answered=True
  rtt=0.05s) -> the 'stopped-oracle' (EXEC-eip-means-stopped) is INVALID;
  pty fire-line scanning is the ONLY stop detector. (Earlier t286 note
  said otherwise; this measurement wins.)
- Views 1-3 FLEET reopen failed (diff 132 then 0) — game UI state after
  the battery does not return to a FLEET-openable state; do not rely on
  multi-view batteries in one sitting without a close-choreography.

## S8 RUN 4 FULL RESULT (3/3 attempts, loop3) + STATIC CROSS-CHECKS
Attempts 205111/205500/205849: identical 8-leg arm (handler+router included,
  BPLIST verbatim same addrs), control dump MATCH=True, attempt-1 full good
  choreography (End Turn 1086->1087, FLEET diff 122756, row-93 -> Icarus,
  sprite 48x151 clicked, planet 439x331, empty 236x200) — ZERO fires, pty
  'Memory breakpoint' count 0 (the 9 hex-addr pty lines are MY BP commands
  echoed). Attempts 2-3: FLEET reopen failed post-battery (diff 132/0) —
  one-shot battery law: only the FIRST view per sitting is trustworthy.
SAME-SESSION CONTRAST = attribution: FLEET button click PRODUCED an effect
  (ring diff 122756), row-93 click PRODUCED the view jump, End-Turn click
  PRODUCED t+1. Synthetic clicks demonstrably reach the game. Yet handler
  0x1aef8 (BatModeWnd msg entry) + router 0x1b070 + 6 downstream legs never
  executed on ship/planet/empty clicks in the system view.
STATIC CROSS-CHECKS (offline, payload 576643 B, P0=0x1bf450):
  - E8-call census: handler 0x1aef8 ZERO callsites; router 0x1b070 ZERO;
    batcon 0x1b91c TWO (0x1da51c, 0x1da62e — enclosing fn NOT yet found).
  - u32 scans: value P0+0x1aef8 AND raw 0x1aef8 occur ZERO times in the
    payload image (only the RAM member+0x88 hit t298 found — heap, likely
    a live window instance slot).
  - windows.txt VERBATIM: BatModeWnd rect X0=7 Y0=7 X1=465 Y1=472 — ALL
    three click points are INSIDE the window rect; every named child button
    sits x>=479 (sidebar chrome), so clicks could not have been stolen by a
    child. TOGGRID at (557,403)-(587,433) SENDMESSAGE 74 = live, reachable
    control candidate.
  - INT census: CD 33 x5, CD 31 x42 (DPMI) — mouse likely polled/thunked;
    NOT yet probed live (DOSBox intercepts INT 33h; guest BP may not catch).
READING: either (A) system-map clicks bypass the msg-dispatch layer entirely
  (polled hit-test), or (B) 0x1aef8 is not the live msg handler for this
  window (dead variant / wrong attribution). SEPARATING PROBE (t301): arm
  0x1aef8, click TOGGRID (inside BatModeWnd, known-good click path, visible
  toggle effect): FIRE => (A) map clicks bypass dispatch (msg layer alive,
  ship selection is NOT msg-dispatched -> REFUTED entry + watchpoint route
  for the mouse-state block); ZERO => (B) handler attribution dead, the
  windows.txt->handler bridge (t298 member+0x88) is the live-instance law
  and the whole static leg map needs re-derivation.
  NO hardware-breakpoint command exists in this dbg build (grep HBREAK:
  zero hits) — code BPs + BPLM watchpoints only.
