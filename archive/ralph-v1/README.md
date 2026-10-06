# ralph-v1 archive — snapshot, 2026-10-06

Loop-control files as they stood when the v1 goal contract (re-implement the
single-player game) completed. Moved here for later analysis; the live loop
uses fresh replacements at the original paths (docs/GOAL.txt, docs/STATE.md,
docs/PLAN.md, docs/BLOCKED.md, scripts/launch_ralph.sh).

Repository state at snapshot time:
  branch main, commit ba9e1b9ef91d5caf1850a989363ac8a15a110ad6
  ("TURN-ADVANCE capture LIVE: turn counter u16 phys 0x254e10 +
  TURN-BOUNDARY law for planet records", 2026-10-05 23:22 -0400)
  gate: ALL CHECKS PASS (milestone=6); run_tests: 83/83 (re-verified
  2026-10-06 morning, before the move).

Contents (verbatim v1, unchanged):
  GOAL.txt          v1 contract (complete game, R1 fork resolutions inside)
  STATE.md          v1 working memory — full turn log 2026-10-03..2026-10-05l
  PLAN.md           v1 phase list P0..P6 (note: its .tsv='text .bin' claim
                    was later FALSIFIED; erratum carried into docs/PLAN.md)
  BLOCKED.md        v1 decision record (option C chosen; tracer dead;
                    -break-start superseded)
  OPEN-QUESTIONS.md v1 ledger with full per-item evidence text (the live
                    docs/OPEN-QUESTIONS.md is now a closeout ledger whose
                    rows cite back to this file; do-not-retry prohibitions
                    were copied into docs/REFUTED-ROUTES.md)

Everything else (docs/FINDINGS.md, docs/re/*, docs/PLAYTHROUGH.md, rewrite/,
scripts/*, extracted/) stayed in place — research artifacts, not loop control.
