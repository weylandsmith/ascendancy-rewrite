# t153 WIP — IDLE re-check #40 + (B4) untracked-ownership leg

Session start 2026-10-28 02:48:55; probe run 02:50:35.

## Measured state (frozen here before any edit)
- Trigger (A) NEGATIVE — `python3 scripts/r1_idle_probe.py` RC=0 @ 02:50:35
  (cutoff 02:48:55): newest playcap dir playcap-20261014-224611; timeline
  mtime_ns 1793043841304000000 / 5691796463 B; zero dosbox procs; find sweep
  4 files, non-loop none; A4 watcher ALIVE pid 27774; A5 none (save/*.sav=20).
- Independent re-verification OUTSIDE the probe (t147/t148 law): baseline
  constants re-read from source (r1_idle_probe.py:55-56
  BASE_MTIME_NS=1793043841_304_000_000 / BASE_SIZE=5691796463) and `stat`
  re-run directly -> size 5691796463 exact match.
- t151 CONTENT BASELINE REPRODUCED for the 3rd time: head-64KiB md5
  42a0bed0507f9052e2009ec94e9c27f1, tail-64KiB md5
  1529ab1ad70ac360f441d819703f943f — both byte-identical to the banked pair.
- Trigger (B) NEGATIVE — clean tracked tree at HEAD 1abf176, no STEERING file,
  B3 HEAD == journal last-row sha 1abf176, prompt pair prompt-75 vs prompt-74
  (58/58 lines) digit-stripped delta 0.
- t152 argv law re-verified from source (r1_t85g_sitting.py:26-27
  DEFAULT_RUN / RUN = sys.argv[1] ...). Correctly NOT run (no sitting).
- Bank hygiene: `grep -rln stop-report scripts/` -> only r1_idle_probe.py +
  its .pyc; stop-report.md 1581 lines, zero diff vs HEAD before appending.

## The iteration's finding (in progress)
Reviewed the full (B) trigger surface for the t145-class defect ("the leg reads
the right input and does the wrong thing with it"). Legs: B1 working-tree
content diff + name-globbed STEERING file; B3 HEAD-vs-journal sha (committed
route); B2 prompt content diff.

GAP: the untracked line (r1_idle_probe.py:245-247) prints `??` entries as
"informational, NOT a trigger" for ALL paths. t117's law was earned against the
LOOP'S OWN untracked files (docs/re/_wip_*.md), but it is applied universally,
so a user decision delivered as a NEW FILE (docs/ANSWER.md, notes.md) is
invisible forever — the STEERING leg only globs the literal names
`docs/STEERING* STEERING*`, so it does not cover this route either.

Measured safety of splitting by ownership: `git status --porcelain
--untracked-files=all` = 0 lines at this clean session start; `.gitignore`
covers the loop's whole scratch surface (build/, build-*/, rewrite/build/,
.logs/, __pycache__/, *.pyc, .venv/, .cache/, .cache_check, *.log, work/), and
git status never lists ignored files — so a non-ignored untracked file outside
LOOP_OWNED has no loop-tool origin.

Plan: add (B4) — untracked split by LOOP_OWNED ownership; foreign untracked
ARMS, loop-owned untracked stays informational (t117 preserved). Validate by
real execution on 4 branches, fixtures deleted after.
