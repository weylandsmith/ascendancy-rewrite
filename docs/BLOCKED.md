# BLOCKED.md — RESOLVED 2026-10-04g: option C chosen by the user

## DECISION (2026-10-04g, user)

Proceed under **C (hybrid), B-priority**. Operationally this means:

1. All rule/formula work continues on the data-first route (B): extracted
   plaintext tables, manual prose, targeted disassembly, cited to
   extracted-file offsets (contract-permitted), ambiguities to
   OPEN-QUESTIONS. Nothing changes about how work is done today.
2. **R1 is attempted once per session** via `scripts/r1_attempt.sh`
   (mechanically enforced: `scripts/launch_ralph.sh` runs it at session start
   when `work/r1/attempt-*` is >12 h old; a long-lived session re-checks the
   same timestamp at turn start per STATE.md NEXT ACTION). The attempt is
   bounded by construction and NEVER mounts `game/` — dosbox runs from a
   scratch copy in `work/r1/game/` (safety invariant, gate 3n pins it).
3. Whenever an attempt prints `R1 LIVE` (exit 0 + PAYLOAD HIT), the loop
   upgrades formulas to exact (Campaign::attackScore/defenseScore/economy
   phases, each cited to its OQ entry) and closes those OQs. Exit 1 = normal
   negative under C — record one line in STATE.md, do not retry the turn.
   Exit 2 = harness error — fix the harness; never log it as a negative.

## Verified environment facts (harness-building session 2026-10-04g)

- dosbox-x 2025.02.01 **makes itself untraceable early in startup**: from the
  same-uid parent, `PTRACE_ATTACH` (16) and `PTRACE_SEIZE` (0x4206) both
  return EPERM, and `/proc/<pid>/maps` is EACCES from t+2 s onward, while the
  identical probes on a plain `sleep` child succeed (the harness self-check
  in `scripts/r1_tracer.py`). yama ptrace_scope=0, TracerPid=0.
  ⇒ the **external-tracer capture route is dead on this box** without
  emulator-side changes. Do not write a fourth ptrace probe; the mechanism is
  dosbox-side.
- The first real attempt ran through the harness and recorded cleanly
  (`work/r1/attempt-*/tracer.log`: `TRACABLE=no`, exit 1, no stray
  processes, log bounded).
- dosbox-x `-time-limit <n>` exists (help text) and is used by the harness.

## Remaining R1 route [unverified — pilot before trusting]

`dosbox-x -break-start` ("Break into debugger at startup" — strings verified
in the binary; the debugger also prints an "Enter Debugger Command" prompt).
The debugger runs IN-process, so it sidesteps the ptrace block. Its command
grammar (memory dump syntax, output destination) is UNKNOWN — pilot it
manually under a pty with `timeout` + exact-name kill before automating;
the DOSBOX RULE EOF-spam trap (STATE.md KNOWN-ISSUES) applies exactly when a
debugger prompt is left at EOF.

## Residual R1-blocked items (updated 2026-10-05f)

OQ-003 (.gam save map), OQ-005 (.shp pixel codec), OQ-006 (headerless sample
rate), OQ-010 (combat arithmetic), OQ-019 (ship design screen). OQ-017
(vendor .fnt fonts) left this list on 2026-10-05f: the codec closed
statically and the UI now renders with the vendor faces themselves.
Retrofitting exact formulas after completion stays cheap: they are constants
and small arithmetic, each cited to its OQ entry.

## The original question (kept for the record)

The shipped `ascend.exe` (OS/2 LE, Watcom) exposes its control flow
statically (269 functions bootstrapped, file order == memory order) but not
its data identities: no static constant base maps code-side addresses to the
data the code reads (four independent tests, all refuted — docs/re/loader.md
§4). Routes considered:

  A. Runtime dump (R1): drive the original in dosbox-x, dump memory after
     data load, correlate pointers against extracted files, re-run Ghidra
     fixed-base, lift formulas conventionally. Exact fidelity; untested
     route; risk of turns with no output.
  B. Data-first (R2): implement from verified extracted tables, manual
     prose, targeted disassembly; constants cite extracted-file offsets
     (explicitly contract-allowed); ambiguities to OPEN-QUESTIONS.
  C. Hybrid: B for everything, plus R1 attempts interleaved once per
     session, upgrading formulas to exact whenever a dump succeeds. ← CHOSEN
