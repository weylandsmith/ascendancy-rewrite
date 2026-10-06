# BLOCKED.md — v2 (decision history in archive/ralph-v1/BLOCKED.md)

## Standing decision (NOT re-openable)
Option C hybrid, B-priority, chosen by the user 2026-10-04: data-first work
plus R1 runtime capture via dosbox-x save states, no cadence limit (abolished
2026-10-05). Full rationale and the refuted A/B fork: archive/ralph-v1/BLOCKED.md.

## Current blocks
NONE — the loop has live, bounded routes for every open item (docs/STATE.md
LEDGER). If this section becomes non-empty, each entry needs: the question,
the best default in force meanwhile, and what evidence/machine would settle
it. Under strict-close policy such items STAY OPEN (never converted to
FINAL-DEFAULT closures); the loop keeps other workstreams moving.

## R1 runbook (mandatory safety invariants — a run without them is a bug, not research)
Route: scripts/r1_savestate.sh (+ r1_sav_scan.py per-run base; never hard-code
B). Deep capture: scripts/r1_deepcapture.sh. Invariants (enforced statically
by gate 3n):
- dosbox NEVER mounts pristine game/ — scratch copy under work/r1/ only
- headless-safe config: output=x11 under Xvfb for captures needing vblank
  autosave (host-clock autosave is checked at vblank — dummy video = no
  saves); nosound=true; stdin=/dev/null
- -time-limit always; all output bounded (head -c); DOSBOX RULE in STATE.md
- kill ONLY pkill -x dosbox-x
- exit codes: 0 = base derived / upgrade formulas; 1 = normal negative,
  record ONE line in STATE.md, no in-turn retry; 2 = harness bug, fix it

## Closed-as-dead capture routes (do not resurrect; full trail in
## docs/REFUTED-ROUTES.md)
- external ptrace tracer: dosbox-x 2025.02.01 makes itself untraceable
  (ATTACH/SEIZE EPERM, maps EACCES by t+2 s) — dead on this box
- dosbox-x -break-start: superseded by save states AND carries the EOF-spam
  trap; do not pilot
- static absolute-base schemes: four refuted, fifth forbidden — the runtime
  pointer law (OQ-011 CLOSED) is the answer
