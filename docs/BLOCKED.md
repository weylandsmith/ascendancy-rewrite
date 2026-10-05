# BLOCKED.md — RESOLVED 2026-10-04g: option C chosen by the user

## DECISION (2026-10-04g, user)

Proceed under **C (hybrid), B-priority**. Operationally this means:

1. All rule/formula work continues on the data-first route (B): extracted
   plaintext tables, manual prose, targeted disassembly, cited to
   extracted-file offsets (contract-permitted), ambiguities to
   OPEN-QUESTIONS. Nothing changes about how work is done today.
2. **R1 runtime capture** — CADENCE WINDOW ABOLISHED 2026-10-05 (user
   decision): the 12 h/once-per-session rate limit is gone. The route is now
   `scripts/r1_savestate.sh` (docs/re/r1-savestate.md): dosbox-x autosave
   writes full-guest-RAM ZIP save states; `scripts/r1_sav_scan.py` derives
   the member-offset base of the live image from unanimous high-entropy
   anchors (measured B=0x1BF4D8, 6/6 slots, per-run data — never hard-code).
   The old tracer route (`scripts/r1_attempt.sh`, external ptrace) stays
   dead on this box and is kept only for the record. Every run keeps the
   safety invariants: scratch copy (never mounts `game/`), headless,
   `-time-limit`, `pkill -x dosbox-x`, size-capped output.
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

## Remaining R1 route — SUPERSEDED 2026-10-05 (savestate route LIVE)

Kept for the record: `dosbox-x -break-start` ("Break into debugger at
startup" — strings verified in the binary) was the planned in-process route.
It was never needed: the same session's SAVESTATE route (docs/re/
r1-savestate.md) captured the live image without any debugger or ptrace.
Do not pilot `-break-start` now; the DOSBOX RULE EOF-spam trap (STATE.md
KNOWN-ISSUES) applies exactly when a debugger prompt is left at EOF, and
there is nothing left for it to prove.

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
