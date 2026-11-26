# _wip_tPF7 — RESEARCH SCREEN CONTROLS (D28 items 16/17/18)

Working log; landing distils into docs/re/research.md.

## P0 TASK DEFINITION + SITTING (2026-11-26)
- D28 file scratchpad/t433-build-feedback.txt research items = lines 16-22
  (R1-R6 in DECISIONS.md D28). Controls cluster = 16 (rotation too slow),
  17 (rotation buttons must be PRESS-AND-HOLD, no latch; left one dir, right
  the other), 18 (up/down scroll buttons no-op, console msgs only).
  Items 19-22 are the selection/framing cluster (tRS-B1 law / tPF-8 /
  TPF5-A-gated framing), NOT controls.
- Sitting check ran FIRST (scripts/r1_t85g_sitting.py exit 0,
  work/r1/tPF7_pre_sitting.out): trusted rows 45,227, newest t=1335 —
  IDENTICAL to tPF-6 baseline; the 10.4 GB timeline growth is watcher
  rewrites. Stale assignment stood.

## P3 FLOAT[0x9f108] MEASURED = 1.0 EXACTLY, 4233/4233 SAVES (closes the
## magnitude half of items 16+18; scripts/tPF7_zoomscale_census.py, output
## work/r1/tPF7_zoomscale.out)
- Pointer-law read member(0x242000+0x9f108+H) per save; histogram {normal
  1.000000e+00 x4233}, ZERO zeros, ZERO denormals (3 files = non-zip
  checkpoints, excluded). _wip_tNGS S12's "measured ~0 in bank-41.sav
  (denormal)" is REFUTED (offset misread — the neighbour u32s near 0x9f108
  ARE denormal garbage, the target is not). t416 S-d "scale 1.0" CONFIRMED.
- CONSEQUENCE: the port's 1.0 assumption is vendor-exact; "rotation is too
  slow" (item 16) and "scroll does nothing" (item 18) CANNOT be the scale —
  the remaining knobs are the PUMP CADENCE and the press/release gating.
- Dispatch tail re-read 0x47648..: jb 0x47662 / jbe 0x47d3b => 0x38..0x3a
  release family -> 0x47d3b (latch bits cleared per ~ebp mask); the
  fallthrough cmp at 0x47658 desyncs capstone (0f byte) — the je-target
  0x47c88 (pump block) is reached from a msg id in (0x3a, ...] — t302 banked
  cosmos PUMP MSG = 0x3b at ~1/s. WHO POSTS 0x3b to reswin + its true cadence
  = TPF7-B (next probe).

## P2 RELEASE/RELEASE-LATCH LEG + HELP TEXT (2026-11-26)
- Dispatch handler 0x47614 on msg id dx (u32 0x47614 appears exactly once as
  data, payload 0x88a68 = the widget vtable slot — registration is by table):
  dx<2 -> 0x47679 (window-init path: CLEARS 0x764c4 `mov [0x764c4],ecx`
  ecx=0, resets sel word win+0x9db=0xffff); 2..3 -> default; 4 -> 0x47d99
  STUDY COMMIT (tRS-B1); 6..0x31 -> 0x477e4 (0x56730 cancel-pending +
  repaint); 0x32..0x35 -> 0x47b41 LATCH BLOCK; 0x38..0x3a -> 0x47d3b.
- 0x47d3b (msg 56/57/58) = THE RELEASE LEG: `mov ebx,[0x764c4]; not ebp;
  and ebx,ebp; mov [0x764c4],ebx` — clears latch bits per ~ebp mask, then
  0x56730 cancels the pending scheduled send (ebx=-1). So the vendor DOES
  have a press-schedule + bit-clear release mechanism.
- LATCH-BLOCK TAIL 0x47c48: `cmp ebp,4; jne skip` — ONLY when ebp==4 does a
  press also SCHEDULE a follow-up msg via 0x5669c(0x7a35c screen, edx=
  [win+0x41], ecx=0x38, ebx=1, push (msg==0x34/0x35 ? 1 : 0), push 0).
  0x5669c = deferred-send queue writer (stride 0x12 slots at win+0x4610,
  enqueues via 0x59bf4 into queue at win+0x48c2, cap 0x1388). ebp = 3rd
  handler arg (role: press-kind — exact semantics TPF7-A named-open).
- VENDOR TEXT CORROBORATION (extracted/ascend00/help.txt "help resmove"
  VERBATIM): "This button will let you manipulate the Research Display.  Use
  the right mouse button if you want to move or rotate continuously." =>
  CONTINUOUS (while-held) operation is vendor law; the user's item-17 target
  matches the vendor's own help.
- PORT TARGET (user ruling D28 items 17/18 = behavior authority; law
  citations above): mouse-DOWN on a res control applies the press law;
  mouse-UP clears that pair's bits (0x47d3b shape) => hold-to-move both
  pairs, left/right opposite dirs, up/down opposite. Keep the pump.
- ITEM 16+18 MAGNITUDE: FLOAT[ds:0x9f108] multiplies BOTH the +-3deg rot
  step and the +-1 dolly step. Port assumes 1.0 (TRSV1b-A). MEASURE from
  banked saves via pointer law next.
- Port today: ui.cpp:913-920 dispatches ResHit::RotLeft/Right/MoveUp/MoveDown
  -> resCam.pressRot/pressMove (latch law researchview.h:169-178); pump
  ui.cpp:3538-3540 every Camera3d::kSpinTickMs while moving().
- ITEMS 16/17/18 ARE LIVE COMPLAINTS AGAINST THIS FAITHFUL PORT (user
  describes our exact pressPair table in item 17: left toggles on/off, right
  starts-then-flips — which IS the vendor law, re-verified below).
- RAW LAW RE-DERIVED VERBATIM 0x47b44..0x47c42 (masks: 0xf7=~bit3,
  0xfb=~bit2, 0xfd=~bit1, 0xfe=~bit0 — an easy misread trap):
  msg50 LEFT: (0,0)->(1,0) start; (1,0)->(0,0) stop; (1,1)->(1,0) flip;
    (0,1)->(1,0) revive-left.  msg51 RIGHT: (0,0)/(1,0)/(0,1)->(1,1);
    (1,1)->(0,1) DEAD.  msg52 UP: (0,0)->(1,0); (1,0)->(0,0); (1,1)->(1,0);
    (0,1)->(1,0).  msg53 DOWN: (0,0)/(bit0 clear)->(0,1); (1,0)->(1,1);
    (1,1)->(0,1).  == port pressPair CORRECT, no port bug in the table.
- PUMP 0x47c88..0x47d18 VERBATIM: rot delta = (1,0)?+3.0:(1,1)?-3.0 fmul
  FLOAT[0x9f108]; move delta = (bit0)?-1.0:(bit1)?+1.0 fmul FLOAT[0x9f108]
  added to posZ [win+0xe3]. => ITEMS 16+18 SHARE ONE MAGNITUDE CONSTANT:
  f32 ds:0x9f108 (seam TRSV1b-A "not in restored image") — MEASURABLE from
  banked saves via pointer law; port currently assumes 1.0.
- OPEN CRUX (item 17 hold-vs-latch): does the framework deliver a RELEASE
  message that clears 0x764c4? Handler 0x47614 dispatch on dx: <6 ->0x47d7f,
  ==6 ->0x477e4, 0x32..0x35 ->latch block, 0x38..0x3a ->0x47d3b (starts
  `mov ebx,[0x764c4]; not ebp` — SUSPECT, read next), pump reached via
  0x4765c je 0x47c88. windows.txt RESROTLEFT/RIGHT, RESMOVEUP/DOWN all
  SENDMESSAGE 50..53 SENDPARAM1=999 (windows.txt:1779-1832).
- ALSO: latch block tail 0x47c48 `cmp ebp,4; jne` -> 0x5669c(0x7a35c, edx=
  [win+0x41], ecx=0x38, ebx=1, push (msg==52/53?1:0)) — ebp = handler 3rd
  arg, possibly press-kind flag — roles owed.

## P4 THE FULL CONTROL LAW: PUMP = MSG 0x3a, RELEASE FAMILY 0x38/0x39
(decisive; raw disasm 0x47648..0x47662 + 0x56374/0x5669c/0x56730 this session)
- CORRECTION to P2's "0x38..0x3a -> 0x47d3b": dispatch bytes are
  `47648 cmp dx,0x38 / 4764c jb 0x47662 / 47652 jbe 0x47d3b / 47658 cmp dx,
  0x3a / 4765c je 0x47c88` => 0x38,0x39 -> 0x47d3b RELEASE; 0x3a -> 0x47c88
  PUMP; >0x3a -> default. The pump id is 0x3a for RESWIN (cosmos uses 0x3b —
  different window, do not conflate).
- PUMP HANDLER 0x47c88 VERBATIM: rot pair bits2/3 [0x764c4]: (bit2 set) ->
  delta +3.0, (bit3 also) -> -3.0; fmul f32[0x9f108] (=1.0 MEASURED P3);
  call 0x53504(esi+0x11f, ecx=-1) yaw mix. Move pair bits0/1: bit0 -> -1.0,
  bit1 -> +1.0, fmul same, fadd into posZ [win+0xe3]. Sets [0x764c0]=-1
  (repaint) if either pair active; 0x47d18 repaints via vtable [esi+0xa7]+0xc
  when flag set.
- PUMP IS SELF-SCHEDULED AT WINDOW INIT: 0x47679 tail calls 0x56374(0x7a35c,
  edx=[win+0x41], ecx=0, ebx=0x3a, push 0, push arg[esp+0x14]) — 0x56374 =
  REPEATING-message registration: stride-0x16 slot at win+0x44ae, stores
  msgid + interval + DAT_0xa2044+interval fire-time, count [win+0x460e]++.
  => reswin pumps ITSELF msg 0x3a on a timer while open. Interval argument
  role + the framework fire-loop = TPF7-B (cadence MEASUREMENT owed —
  t302's ~1/s was cosmos msg 0x3b, NOT this timer; strict-close forbids
  reusing it as a cited value).
- RELEASE FAMILY: 0x47d3b (msg 0x38/0x39) `ebx=[0x764c4]; not ebp; and
  ebx,ebp; mov [0x764c4],ebx` clears latch bits per ~ebp, then 0x56730
  cancels the pending queued send (ebx=-1 wildcard msgid). The press tail
  0x47c48 (ebp==4 only) queues msg 0x38 via 0x5669c (one-shot queue stride
  0x12 at win+0x4610 -> 0x59bf4 queue win+0x48c2 cap 0x1388). 0x477e4 (msg
  6..0x31 = any other event) ALSO cancels the pending release (0x56730,
  ebx=8). READ AS A SYSTEM: press latches + arms a release; release (or
  unrelated event) clears the pair bits => CONTINUOUS-while-held is the
  vendor law, matching help resmove (P2) and the user's item 17 verbatim.
  ebp bit-role detail (which pair 0x38 vs 0x39 masks) = TPF7-A named-open;
  SHIP-SAFE reading: mouse-UP on a control clears THAT control's pair.
- PORT DEFECT ATTRIBUTED: (17) no release leg -> latches stick; (16) pump at
  guessed 1000 ms + sticky latches; (18) move deltas +-1 unit/tick at 1 Hz
  read as "does nothing" — release leg + measured/decided cadence fix all
  three shapes. HOLD SEMANTICS SHIP NOW (law cited); cadence stays
  kSpinTickMs documented default until TPF7-B measures the vendor timer.

## P5 FRAMEWORK FIRE-LOOP DECODED — PUMP CADENCE IS THE SAME TIMER t302
MEASURED LIVE AT ~1/s (static; 0x56374/0x56608 + callers)
- Watcom regargs: 0x56374(eax=screen, edx=target, ecx=param, ebx=MSGID,
  [esp+0x14]=interval, [esp+0x18]=flag2). Slot stride 0x16 at win+0x44ae:
  +0 target, +2 msgid, +6 param, +0xe INTERVAL, +0x12 next-fire
  (= DAT_000a2044 + interval at registration).
- FIRE LOOP 0x56608: per slot, `cmp DAT_000a2044,[slot+0x12]; jb skip` ->
  dispatch 0x56ca4 -> `add [slot+0x12], interval` (repeat). RESWIN INIT
  PASSES INTERVAL=0 (0x47713 caller pushes 0,0) => next-fire never advances
  => the pump fires EVERY fire-loop pass once DAT >= registration time. The
  fire-loop period IS the cadence — and t302 LIVE-WITNESSED this exact
  mechanism (cosmos slot msg 0x3b, caller 0x26c80, identical interval-0
  registration) at ~1/s. => reswin pump ~1/s is MECHANISM-VERIFIED +
  same-timer live-witnessed; kSpinTickMs=1000 stays the cited default (feel
  ruling, if any, = TPF7-C named-open).
- DAT_000a2044 tick fn 0x53d84 (`inc [0xa2044]; ret`) sits in a callback
  table payload 0x8b358 {0x6cec0, 0x53d84, 0x650ec} — timer-driven.
- MOVE PAIR DEAD STATE RE-CONFIRMED 0x47cd0: bit0 CLEAR -> je 0x47d18 (no
  dolly); (1,0)->-1.0, (1,1)->+1.0; state (0,1) pumps NOTHING. Port tick()
  matches.
- RELEASE FAMILY REFINED: 0x477e4 (msg 6..0x31) cancels pending msg id 8
  ONLY (0x56730 filter ebx=8) — NOT the release; 0x47d3b (msg 0x38/0x39)
  clears latch bits per ~ebp AND cancels wildcard (-1). Motion = latch while
  held; release msg clears. SHIP-SAFE reading: mouse-UP clears THAT
  control's pair bits (rot=0xc, move=0x3) per 0x47d3b shape; exact per-msg
  masks = TPF7-A.

## P6 THE "~1/s" READING IS A MISREAD — FIRE-LOOP PERIOD = 1000/29.25 ms
(DERIVED from two cited numbers; this is the item-16 root cause, ~29x slow)
- t302 S2/S6 (docs/re/_wip_t302.md ln135-155): first msg 0x3b stop landed
  "within ~1 s of the armed RUN, BEFORE any click" — an UPPER BOUND on the
  first-fire latency, explicitly flagged "consistent with a periodic/timer
  message; NOT yet a law". It NEVER measured the period. cam3d.h:92-95
  turned it into "vendor-measured (t302)" — an unearned citation.
- LIVE MEASURED PUMP RATE (tNG-S S30-X5, debugger, cursor-out): cosmos basis
  azimuth 690 deg / 11.8 s = 58.5 deg/s (+-1, three windows, run
  dbg-tngh-20261123-130254). Cosmos pump delta = 2.0 deg VERBATIM
  (cam3d.h:88 kRotStepDeg, t416 F2). => FIRE-LOOP PASSES
  58.5/2.0 = 29.25 +-0.5 PER SECOND (interval=0 slots fire every pass, P5).
- CONSEQUENCE: reswin pump = 3 deg x 29.25/s ~ 88 deg/s and dolly 29.25
  units/s; the port at 1000 ms delivers 3 deg/s — 29.25x SLOW, EXACTLY the
  user's item-16 shape ("rotation is too slow"), same 30x family as tNG-R
  S28 on the cosmos dial. DITTO item 18: 1 dolly unit/s is sub-perceptible.
- SHIP: kResPumpMs = 34 (1000/29.25 rounded); seam TPF7-D named-open = the
  fire-loop period measured directly (expected 34.2 +-0.6 ms). SIBLING
  DEFECT BANKED: cosmos/systemCam pumps in the SAME ui.cpp block ride the
  same kSpinTickMs=1000 and are 29x slow by this derivation — NOT touched
  this task (tPF-7 scope = research screen); queued as tPF-7b.

## P7 SHIPPED (2026-11-26)
- researchview.h: ResCam::releaseRot/releaseMove (0x47d3b shape), kPumpMs=34
  (P6 derivation cited in-source). ui.cpp: resHold tracker set by the four
  control presses; SDL_MOUSEBUTTONUP applies the pair release + logs
  "ui research latch"; screen-exit zeroes latches + tracker (window-init
  0x47679 law); research pump gated on ResCam::kPumpMs (cosmos/systemCam
  pumps UNTOUCHED — tPF-7b).
- tools/xsend: clickdn/clickup modes (press-only / release-only BUTTON1) —
  hold-semantics witnesses. Rebuilt OK.
- PINS tests/test_rescontrols_tpf7.cpp x4 (release from every state +
  pair-isolation; hold-cycle monotonic + flip-while-held + DEAD state +
  freeze-after-release; cadence derivation self-consistency; ui.cpp wiring
  source-text). CMakeLists entry ADDED. Suite 572 -> 576/0/0.
- FOUR EXISTING RESEARCH WITNESSES MIGRATED to clickdn/clickup + POLLLED
  hold (tRSB1, tRSV1d, tRSV2p, tRSV2w): the old "press, sleep 6, press
  again" idiom relied on the sticky latch + 1s pump; at 34ms it would dolly
  ~175 units. The poll adaptive-terminates on the app's own centre re-log
  count (>= 8 changes), so the scripts survive any future cadence change.
