# _wip_tPF7b — COSMOS / SYSTEMCAM PUMP CADENCE (sibling defect of tPF-7)

Sitting check ran FIRST (scripts/r1_t85g_sitting exit 0, work/r1/tPF7b_pre_sitting.out:
45,227 trusted rows, newest t=1335 — byte-set identical to tPF7_pre_sitting.out;
stale assignment stood).

## P1 THE DEFECT
- ui.cpp:3556 and ui.cpp:3560-3561 pump cam (cosmos map) and systemCam every
  Camera3d::kSpinTickMs = 1000 ms (cam3d.h:95). The vendor law (tPF-7 P5): BOTH
  windows self-register their pump msg on an interval-0 slot (cosmos msg 0x3b
  poster 0x26c66 -> 0x56374; reswin msg 0x3a 0x47713), and the fire-loop 0x56608
  fires interval-0 slots EVERY pass. The port therefore runs 29x slow — the same
  defect class tPF-7 fixed for the research pump.

## P2 THE CADENCE NUMBER (cited, no new measurement needed)
- 58.5 +-1 deg/s MEASURED live at the pump leg (tNG-S S30-X5, basis integration,
  run dbg-tngh-20261123-130254; pump fire witnessed win 0xfd2310 latch=1)
  / 2.0 deg-per-tick VERBATIM immediate (S27-X2, 0x27a32; cam3d.h kRotStepDeg)
  = 29.25 passes/s => period 34.19 ms => kFireLoopMs = 34.
- CROSS-CHECK (independent channel): S28-X3 direct fire-count 28-33 fires/s =
  30.3-35.7 ms; 34 sits inside. Circuit 360/2*0.034 = 6.12 s, inside the
  tngs_s28 pin band 5.4-6.3 s and the user stopwatch 5.3 s family.
- DO NOT re-cite the t302 "~1/s" (REFUTED-ROUTES tNG-S S28: poll-limited census;
  the figure measured OUR poll loop, never the pump). The initial registration
  delay ebp=0x168=360 clock units (S28-X0) stays unit-unknown and IRRELEVANT to
  the steady-state rate — the fire-loop `add [slot+0x12], interval` with
  interval=0 makes steady-state rate = fire-loop period ONLY.

## P3 DECISION (decide once, cite once)
- SINGLE SHARED CONSTANT: Camera3d::kFireLoopMs = 34 in cam3d.h, derivation
  cited THERE. ui.cpp cosmos + systemCam pump gates switch to it.
- ResCam::kPumpMs = 34 (tPF-7, CLOSED) is NOT touched — same quantity, its own
  header already cites _wip_tPF7 P6; the ui.cpp wiring pin for "ResCam::kPumpMs"
  stays load-bearing. cam3d.h comment notes the identity of the two constants.
- kSpinTickMs is DELETED (its only remaining consumers were the two pump gates;
  the pins reference it in comments only — grep-verified).

## P4 INSTRUMENT
- The cosmos pump tick has NO log today ("ui cam yaw" ui.cpp:1341 fires on PRESS
  only). Add change-only witness line in the pump block: "ui cosmos pump yaw
  %.2f" after cam.tick() (rotation has no clamps — yaw changes every fire;
  tRSV1d change-only precedent). Witness counts these during a hold window.

## P5 WITNESS LAW (cosmos dial = TOGGLE, not hold)
- t416 dial law: press latches (inactive->start, same->stop, opposite->flip);
  NO release leg exists for cosmos dials (the tPF-7 release family 0x38/0x39 is
  RESWIN-only). Witness: press RotLeft (486,379 per t411 dial walk) -> expect
  >=10 pump lines in 2 s (~58 at cadence; old 1000 ms pump <=2) -> press again
  -> 0 pump lines in the following 2 s (toggle-off freezes; no sticky).

## P6 DOC CORRECTIONS (so nothing re-tightens on 1000 ms)
- cam3d.h:92-95 comment block ("t425 CADENCE UPGRADE ... t302 MEASURED ...
  vendor-measured (t302)") — the unearned citation, replaced by the P2 derivation.
- cam3d.h:40-46 header PORT LAW line "pump cadence kSpinTickMs (vendor ~1/s
  measured t302)" — corrected.
- docs/re/t399-galaxy-map-3d.md:140 "live ~1/s t302" — corrected in place.
- docs/re/_wip_t425.md:49/104-108 (the 250->1000 "measurement-backed" claim) —
  append dated correction, do not rewrite the historical record.

## P7 WITNESS + INSTRUMENT RESULT (2026-11-26)
- INSTRUMENT FLAW round 1: the new pump lines lacked fflush -> block-buffered
  (tPF-5 trap re-witnessed a THIRD time); live census saw 2 lines then a burst
  (log tail later held 71). Fixed with std::fflush after each pump printf.
- MEASUREMENT-WINDOW FLAW round 2: T_MS bracketed the stop leg too -> rate
  read 11/s. Fixed to bracket the latch window only (tPF-7 witness precedent).
- VERDICT PASS (seed 5, scratch Xvfb :99 killed BY PID): idle 0 pump lines
  (latch-gated, never free-running); latched 62 fires / 2002 ms = 30/s INSIDE
  the S28-X3 band 28-33 (old 1000 ms pump <= 2); toggle-off press -> 0 fires.
- HONEST NEGATIVE: the systemCam pump line is WIRED (pin-checked, same loop,
  same constant) but its own cadence leg was not separately witnessed — the
  cosmos leg measures the shared fire-loop.
## P8 SHIPPED
- cam3d.h: kSpinTickMs DELETED, kFireLoopMs=34 with the full derivation;
  header PORT-LAW comment corrected (no doc re-tightens on 1000 ms).
- ui.cpp: both pump gates -> Camera3d::kFireLoopMs; change-only witness lines
  "ui cosmos/sysview pump yaw" + fflush; every comment naming the retired
  constant reworded (the wiring pin asserts kSpinTickMs is GONE from both
  files — comments included, so re-anchoring needs an explicit pin edit).
- tests/test_campump_tpf7b.cpp x2 (cadence self-consistency vs BOTH measured
  bands + circuit band; wiring count==2 + retired-name-gone + instruments +
  ResCam::kPumpMs untouched). CMakeLists entry ADDED (tPF-4 trap avoided).
  Suite 576 -> 578/0/0.
- docs/re/t399-galaxy-map-3d.md S-pump line corrected in place; dated
  correction appended to docs/re/_wip_t425.md (record kept).

## P9 t425_mapctl_witness RE-RUN NOTE (regression check)
- Cam legs PASS (press-law 'ui cam yaw' lines fire; 0 'ui cosmos pump yaw' at
  idle = latch-gating intact). The maroon/navy WELL pixel census FAILs on THIS
  environment only: the witness reuses production Xvfb :9 which runs 800x600x16
  (ps-verified) — 16-bit depth collapses idx80/idx242 discrimination. t425c
  landed PASS on a 24-bit scratch server. NOT a tPF-7b regression: the diff is
  pump-block + comments only (git diff --stat: cam3d.h/ui.cpp); well law
  untouched. ENV HAZARD banked: pixel-census witnesses must assert the server
  bit-depth (or start their own 24-bit Xvfb BY PID), never inherit :9.
