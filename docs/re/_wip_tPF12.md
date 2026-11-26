# _wip_tPF12.md — FIRE-LOOP PERIOD DIRECT DERIVATION (TPF7-D)

## P0 TASK DEFINITION + ASSIGNMENT AUDIT (2026-11-26)
- STATE.md NEXT ACTION named **tPF-12 cosmos/systemCam pump period** with the
  rationale "cosmos/systemCam pumps STILL on kSpinTickMs=1000 (29x slow)".
  THAT PREMISE IS FALSE — it is the research.md S10 SEAMS line as written
  BEFORE tPF-7b landed. AUDIT (this session, read from disk):
    * commit e43fc2e "tPF-7b: COSMOS/SYSTEMCAM PUMP CADENCE = FIRE-LOOP
      PERIOD 34 ms SHIPPED" is an ANCESTOR of HEAD (HEAD f44a42e).
    * rewrite/src/ui/cam3d.h:106 `static constexpr int kFireLoopMs = 34;`
    * rewrite/src/ui/ui.cpp:3665 cosmos leg
      `cam.moving() && nowMs - lastPumpMs >= (Uint32)Camera3d::kFireLoopMs`
    * rewrite/src/ui/ui.cpp:3676 systemCam leg, same constant.
    * rewrite/tests/test_campump_tpf7b.cpp is in rewrite/CMakeLists.txt:161;
      lines 63-64 CHECK `kSpinTickMs` absent from ui.cpp AND cam3d.h.
    * `grep -rn kSpinTickMs rewrite/` -> ONLY 6 hits, all prose/pin
      assertions about the RETIRED name (researchview.h:211 comment,
      test_rescontrols_tpf7.cpp x3 comments, test_campump_tpf7b.cpp x2
      absence-CHECKs). No consumer remains.
  => tPF-12 as assigned is ALREADY DONE. Re-doing it would burn the
     iteration. The STATE block was stale, not the ledger.
- SITTING CHECK FIRST (per prompt rule 5): work/r1/playcap/live-timeline.jsonl
  mtime 2026-11-26 00:30:25, HEAD commit time 2026-11-26 13:44:01 => the
  sitting PREDATES the last landed iteration; no new play data, so the stale
  assignment stands and I re-point it (below).

## P1 THE REAL SEAM IN THIS FAMILY = TPF7-D (chosen task)
- What is actually still [inferred] after tPF-7/tPF-7b is the VALUE 34 ITSELF.
  Both pumps cite the SAME derivation chain (docs/re/_wip_tPF7.md P6 +
  _wip_tPF7b.md P2): live cosmos spin 58.5 +-1 deg/s (tNG-S S30-X5) DIVIDED BY
  the verbatim 2.0 deg cosmos pump delta (tNG-S S27-X2) = 29.25 fires/s
  => 1000/29.25 = 34.2 ms => kFireLoopMs=34.
- That chain is a PRODUCT OF TWO MEASUREMENTS TAKEN IN DIFFERENT PLACES: the
  numerator is a live-RAM rotation census (cosmos screen), the denominator is
  a static disasm constant. It is sound but it is INDIRECT.
- TPF7-D as named in _wip_tPF7.md seams: "direct fire-loop period
  measurement (expected 34.2 +-0.6 ms)".

## P2 STATIC WALK OF THE TICK/FIRE MACHINERY (this session, fresh disasm)
Tool: ~/tools/revenv/bin/python scripts/t442_disasm.py work/ascend_restored.bin
(project .venv has NO capstone — banked trap: use tools/revenv).
- TICK FN 0x53d84 VERBATIM: `inc dword ptr [0xa2044]; ret` — confirms P5's
  claim byte-exact. THE ONLY pointer to 0x53d84 in the entire restored image
  is at file-off 0x8b35c (u32 scan, whole-file): the callback table
  {0x8b358: 0x6cec0, 0x8b35c: 0x53d84, 0x8b360: 0x650ec}. No direct caller.
- INSTALLER 0x74b36 (single caller 0x74383, inside an init fn that runs
  `pushfd; cli; ... mov es, [0x8942]` — extender-side):
    push 0x9358; push 0x8b358; call 0x66241
    push 0x5ff86; push 0x5f5b4; call 0x66241
  0x66241 = extender service: builds a param block {0x600, hi/lo(arg1),
  hi/lo(span)} and calls eax=0x31 via thunk 0x78cfd->0x7c3a4. 0x600-with-
  param-block is NOT DPMI 0x0600 (that form is CX-in/BX-out); the thunk sits
  in the game's own extender slab (0x7c37c/0x7c3a4) — this is a CUSTOM
  callback/lock registration, rate literal NOT present at the install site.
  DEAD END for a static period cite (probe budget respected, stopped).
- FIRE LOOP 0x56608 FULL VERBATIM (work/tPF12_fireloop.asm):
    0x5661a slot-count word [win+0x460e]; per-slot stride 0x16 at win+0x44ae;
    0x56666 mov ebx,[0xa2044]; 0x5666c cmp ebx,[slot+0x12]; 0x5666f jb skip;
    0x56689 dispatch 0x56ca4; 0x56638/0x5663b add [slot+0x12], interval.
  Slot next-fire at registration = DAT + interval (0x56374 law, P5), so an
  INTERVAL-0 slot's next-fire NEVER advances => it passes the cmp EVERY pass.
  THE FIRE LOOP HAS NO WAIT OF ITS OWN — the only pacing is its CALLER: the
  main-loop fn (body ~0x547d8..0x54ba3; fire-loop call 0x5481e guarded by
  `cmp word [esi+0x460e],0 / je` = "run the fire loop iff any slot exists").
- CONSEQUENCE (law-grade, static): the vendor pump period == the MAIN-LOOP
  PASS PERIOD, period. There is no timer constant between the pump and the
  loop. DAT_000a2044 gates only the FIRST fire (next-fire = tick at
  registration time; fires once the tick advances) and paces NONZERO-interval
  slots — NOT the interval-0 pumps.
  => A "fire-loop period measurement" IS a main-loop pass-rate measurement.
  => The tick-counter rate (18.2 Hz? something else?) is a SEPARATE quantity
     that cannot confirm/refute 34 ms for the interval-0 pumps. Do not chase
     it for this row (would be a wrong-consumer cite, D30 derivation law).

## P2b FPS-METER FINDING (0x55020, from the flood range — TRAP banked below)
- TRAP: `scripts/t442_disasm.py 0x54820 $(( $f + 0x40 ))`-style hex arithmetic in
  bash: `$(($f+0x40))` with f='0x54820' evaluates DECIMALLY-mixed and produced a
  10 MB disasm dump into the tool output. Always pass explicit hex END bounds.
- FN 0x55020 VERBATIM (0x55020..0x5507e+): per-invocation counter
  [0x7a34c]++; at 10 (`cmp ebx,0xa`): sample eax=DAT_000a2044 -> store
  [0x7a350] and [0x7a354]; ebx = now - prev-sample (delta ticks per 10 calls);
  zero-guard ebx=1; then `mov eax,0x3e8; xor edx,edx; div ebx` =>
  QUOTIENT = 1000 / (ticks per 10 invocations).
  * If DAT_000a2044 ticks at 100 Hz: quotient = 1000/(delta) = invocations/s
    EXACTLY (10 * 100/delta). FN 0x55020 IS A CALLS-PER-SECOND METER whose
    quotient is exactly the rate of ITS OWN CALLER under the 100-Hz reading.
  * If tick = ms (1000 Hz): quotient = calls/s / 10 (needs x10 downstream).
  * If tick = 18.2 Hz (DOS timer): quotient = 55.0 at 1 call/s — implausible
    for an in-game meter constant 0x3e8 to be used that way.
  [inferred] pending: (a) who calls 0x55020, (b) who consumes the quotient.
- OTHER DAT_000a2044 CONSUMERS SEEN (22 byte-hits, full list): 0x54c44
  (tick+mousex div 5 — mod-5 spread), 0x54cf1 (`esi=tick-[0xa2020]; cmp esi,3;
  jb` = 3-tick DEBOUNCE gate), 0x5504d (this meter), 0x563f3/0x56582 (slot
  registration next-fire = DAT+interval, P5 law), 0x56666 (fire-loop cmp),
  0x545af (`mov [0xa2044], edx` ZERO RESET at init fn 0x545a0 — allocates
  [win+0x4732] via 0x67698(0x3f1d4); monotonic WITHIN a run).
- 3-TICK DEBOUNCE + fire-loop cmp share the tick: if tick were ~29 Hz the
  debounce would be ~100 ms; if 100 Hz, 30 ms. No contradiction either way —
  not decisive, unit still owed.

## P3 MEASUREMENT DESIGN (what would upgrade 34 from [inferred])
- Existing evidence for 29.25 passes/s:
    S30-X5 58.5+-1 deg/s (live yaw basis integration) / 2.0 deg verbatim
      => 29.25 +-0.5 passes/s  [indirect product]
    S28-X3 DIRECT fire-count 28-33 fires/s => 30.3-35.7 ms  [direct, +-10%]
  The direct channel already EXISTS and contains 34; the indirect channel is
  tighter. A new capture could only tighten the DIRECT band (sample the
  cosmos yaw f32 at >>29 Hz and count steps). Check tooling feasibility
  (r_tNGH_hover_session.py pattern) before committing to a run.
- ALTERNATIVE ZERO-CAPTURE CITE: the fire loop runs once per main-loop pass;
  the autosave law (t260: ~10 s cadence) is ALSO slot-driven — if a banked
  nonzero-interval slot with a known wall-cadence consumer exists, its
  interval/tick ratio pins the tick rate, and combined with S28-X3 brackets
  nothing new about 34. (Not pursued as the primary route.)

## P4 TICK-RATE CENSUS — MEASURED 94.7 Hz (zero new capture)
- scripts/tPF12_tick_census.py: pointer law (member = 0x242000 + D + H, BDA
  signature, same machinery as tPF7_zoomscale_census) reads u32 DAT_000a2044
  from banked saves; consecutive ring saves cross-timed against file mtimes.
- bank-play-20261111 (autosave=10 41-60 law confirmed in session.conf of the
  sibling dbg run): 100 saves, CONSECUTIVE tick deltas 947,947,949,948,946,
  945,948,945,946,946 across mtime steps 10.016 s => 94.6 +-0.3 ticks/s
  [verified measurement, guest wall-clock].
- dbg-t327v-20261107-050546: deltas 960,963,963,961 over ~10.0 s => 96.2/s
  (same ballpark; guest-caps variance).
- The tick is NOT 18.2 Hz (DOS tick would be 18.2) and NOT 1000 Hz. It is a
  ~95 Hz extender callback — consistent with the 0x66241/0x600 registration
  walk (P2) where no literal rate sits at the install site (the rate lives
  in the extender's timer config, not the game image).

## P5 THE FPS-DUDE METER (0x55020) — what it does and does NOT settle
- String "FPS DUDE" MEASURED verbatim at ds:0x895ec (restored-image read);
  fn 0x55020 sprintfs 1000/(delta-ticks-per-10-calls) into it via 0x76c79
  (sprintf family, cited aicode.md:668) at fmt 0x2cdb. Called once per
  main-loop pass from 3 sites: 0x217bd, 0x55603 (both right after the
  0x54650-frame event pump), 0x55f89.
- ARITHMETIC: at tick=94.7 Hz the quotient = 94.7*(10/delta) ~ 9.47*fps when
  the loop runs at fps passes/s. A 100 Hz tick makes it EXACTLY fps. Either
  way the meter displays ~fps/10..~fps — i.e. THE VENDORS OWN OVERLAY MEASURED
  THE MAIN-LOOP PASS RATE, proving the loop rate was a machine-dependent
  quantity the developers actively watched, NOT a fixed framework constant.
- Meter state [0x7a34c]=0 and samples [0x7a350]/[0x7a354]=0 in 100/100 ring
  saves: the counter RESETS to 0 right after each sample (0x55068 verbatim),
  so a snapshot catching 0 is EXPECTED, not producer-absence (D29 checked).
- CONSEQUENCE FOR THE PUMP LAW (the honest core): the fire-loop 0x56608 has
  NO wait (P2), so the vendor pump period = the main-loop free-run period.
  On 1995 hardware that rate WAS "as fast as the machine runs" (~29 Hz
  measured on our caps machine); there is NO vendor constant to lift that is
  tighter than the wall-clock spin measurement already banked. kFireLoopMs=34
  is therefore NOT a lifted constant — it is the port's chosen rate matching
  the OBSERVED vendor spin feel (S28-X3 direct band 28-33 fires/s contains it;
  user stopwatch 5.3 s family). Keep 34; the derivation comment is already
  honest ("derived", cites both channels).
- TICK UNIT SIDE-CITE (new, useful): 3-tick debounce gate at 0x54cf1
  (`esi=tick-[0xa2020]; cmp esi,3; jb`) = ~31.7 ms at the measured 94.7 Hz —
  same order as one fire-loop pass; plausible input-debounce design.

## P6 DISPOSITION (strict-close)
- tPF-12 as ASSIGNED: already shipped tPF-7b (e43fc2e) — audit P0.
- TPF7-D "direct fire-loop period measurement": CLOSED at the MECHANISM level
  with a NEGATIVE RESULT — the direct route (P2 fire-loop walk + P4 tick
  census + P5 meter) shows there IS no fixed vendor period to measure for
  interval-0 pumps; the quantity is the free-run loop rate, and the best
  wall-clock bracket of THAT remains the banked S28-X3 direct count (28-33
  fires/s) + S30-X5 (29.25+-0.5/s). No code change is warranted: 34 sits in
  both bands. A capture tighter than +-3% would need yaw sampling >>29 Hz —
  queued as a named seam ONLY if a future feel complaint lands (TPF7-C
  territory).
- NEW LAWS BANKED this iteration: (L1) fire-loop 0x56608 verbatim incl.
  slot-count guard at caller 0x54812; (L2) tick fn 0x53d84 sole increment,
  sole pointer 0x8b35c, zero-reset 0x545af; (L3) tick rate MEASURED 94.6
  +-0.3 /s; (L4) FPS-DUDE meter law; (L5) tick CONSUMERS census (22 byte-
  hits listed in P2b).
