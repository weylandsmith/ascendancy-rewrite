# t146 working notes — IDLE re-check #33 + (B3) coverage fix

## P1 Probe run (session start)
`python3 scripts/r1_idle_probe.py` at 2026-10-28 01:01:44, RC=0 (session-start
cutoff 01:00:00 from the iter-*.log NAME, per the t117 law):
- (A) NEGATIVE — newest playcap dir playcap-20261014-224611; live-timeline.jsonl
  mtime_ns 1793043841304000000 / 5691796463 B (36th consecutive byte-identical
  reading t111..t146); zero dosbox procs; find sweep 4 files, non-loop: none.
  r1_t85g_sitting.py correctly not run.
- (B) NEGATIVE — clean tracked tree at 7d2ccd7, no STEERING file,
  prompt-68 vs prompt-67 (58/58 lines) digit-stripped delta 0.
- INFRA unchanged since t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774;
  x11vnc.log 2026-10-27 17:30:18 / 30114 — zero connects); transients 161126
  (harness runner) / 161175 (probe child) per the t118 noise law.

## P2 NEW COVERAGE HOLE (B3) — a decision delivered as a COMMIT is invisible
Method (t145 lesson applied): asked what trigger_b() DOES, not what it reads.
Every (B) leg is a WORKING-TREE comparison:
  - `git diff HEAD --name-only` / `git status --porcelain`  -> tree vs HEAD
  - STEERING glob, prompt-note diff                          -> uncommitted
If the user answers stop-report §3 by EDITING AND COMMITTING (the normal way
work lands in this repo — e.g. flipping a rewrite/ default, editing PLAN.md,
annotating an OQ row and committing), HEAD moves, the tree is clean, `git diff
HEAD` is EMPTY, and the probe prints NEGATIVE. Thirty-two idle turns adjudicated
(B) under the implicit assumption that a user answer is never committed.
Measured context: 123 of the repo's commit subjects do NOT match `^t<digits>:`
(human/adopted subjects like "t97 bank:", "1e45a1b t102-side: ..."), so subject
convention is no guard either.

FIX LAW: the harness writes work/r1/loop/journal.tsv AFTER each iteration's
commit, first token of field 6 = that iteration's HEAD sha (verified this
session: journal last row 00:59:07 sha 7d2ccd7 == `git rev-parse HEAD`,
commit ct 2026-10-28 00:58:12 — journal is post-commit, so at session start
HEAD == journal sha UNLESS something new was committed since).
So: at session start compare HEAD vs journal sha; if diverged, enumerate the
commits in <journal-sha>..HEAD WITH FILES; ARM only when a commit touches a
path outside LOOP_OWNED (same set as the (B) delta law); divergence confined to
loop-owned paths (e.g. a crashed iteration whose journal row never landed) is
a CAUTION, never a trigger — same shape as the t117 untracked-files law.
Journal path overridable via env R1_JOURNAL so the leg is testable without
touching the real journal.
