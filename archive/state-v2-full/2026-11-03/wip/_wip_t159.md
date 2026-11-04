# t159 — IDLE re-check #46 (2026-10-28, session start 04:40:29 EDT) — WIP

## Trigger adjudication (tool-run, not hand-derived)
`python3 scripts/r1_idle_probe.py` at 04:40:29 => RC=0, VERDICT "IDLE — neither
trigger". Valid wording: tracked tree was CLEAN at session start (0e8c8e9), so
no t155/B5 CANDIDATE ambiguity.

(A) NEGATIVE —
  newest playcap dir playcap-20261014-224611;
  live-timeline.jsonl mtime_ns 1793043841304000000 / 5691796463 B — 49th
  consecutive byte-identical reading (t111..t159); INDEPENDENTLY re-statted
  this turn (`stat -c '%Y %y %s'` -> 1793043841 / 2026-10-26 15:44:01.304 /
  5691796463) and equal to the probe's BASE_MTIME_NS/BASE_SIZE;
  (A6) content baseline reproduced an EIGHTH time: head 64 KiB md5
  42a0bed0507f9052e2009ec94e9c27f1 / tail 1529ab1ad70ac360f441d819703f943f
  (recomputed by hand-side python, match_frozen True/True);
  zero dosbox procs; find sweep -> 4 files, non-loop: none;
  A4 watcher ALIVE pid 27774; A5 none (save/*.sav = 20, all match the glob).
  r1_t85g_sitting.py correctly NOT run.

(B) NEGATIVE —
  `git diff HEAD --name-only` empty; `git status --porcelain` (tracked) empty;
  untracked loop-owned none; untracked outside loop-owned none (B4 clean);
  STEERING file none; B3 HEAD == journal sha 0e8c8e9 (no commits outside the
  loop since the last iteration); prompt pair prompt-81.txt vs prompt-80.txt
  (58/58 lines) digit-stripped delta 0.
  => stop-report §3 answers still outstanding after 46 idle turns.

Ledger both legs: `ledger_index_check.py` LEDGER INDEX OK (record rows=18
open=[OQ-003,OQ-005,OQ-016,OQ-019,OQ-021,OQ-023] closed=17 ids listed; STATE
index open set identical). `ledger_audit.py` LEDGER AUDIT OK.

## Bank hygiene (fresh, before appending §52)
`grep -rln stop-report scripts/` -> scripts/r1_idle_probe.py (docstring),
scripts/ledger_audit.py. stop-report.md = 1901 lines, ZERO diff vs HEAD
(`git diff HEAD --stat -- docs/re/stop-report.md` empty) => hand-authoring safe;
last section header is §51 at line 1834.

## RE-ARM MECHANISM MEASURED ALIVE (new evidence class, was never in any doc)
No doc states what keeps the loop going, so I measured it (`ps -eo pid,ppid,
etime,args`, never pgrep per t114): tmux session `ascendloop` pid 78558 (PPid 1,
17:12:59 elapsed) -> bash -c 78559 -> `bash scripts/loop_one_task.sh` 78561, and
this iteration is 183520 `timeout -s KILL 12600 hermes chat --query-file
work/r1/loop/prompt-81.txt` -> 183522 hermes. journal.tsv last row
`2026-10-28 04:37:53  80 OK 0 (re-check  0e8c8e9 t158...`; fail_streak 0; 81
prompt files; no crontab. WHY IT MATTERS: the loop's whole value is that a NEW
session starts on its own, and if 78561 died the idle turns would simply stop
appearing with no artifact naming the cause. Accepted boundary banked: the
supervisor is NOT inside gate.sh or the idle probe (an idle turn can only observe
it, and the probe's A4 leg adjudicates the WATCHER, not the supervisor), so a
supervisor death is un-adjudicated by design. Repair route if it is ever found
dead: `tmux new-session -d -s ascendloop 'rm -f .../loop/STOP; bash
.../scripts/loop_one_task.sh >> .../loop/loop.out 2>&1'` (the exact command line
78558 still shows), and check for work/r1/loop/STOP first.

## FINDING (t159): the completion state could never pass the audit — FIXED
Method (t158 corollary: audit the GRADER): never-before-run case = ledger with
ZERO open rows, i.e. GOAL.txt:2's own completion condition ("gate exits 0 AND
no item open"). Fixture /tmp/t159-f6.md (all 18 rows CLOSED, handles in every
status cell, verified all_closed=True n=18 via la.rows/status_of):
  1. audit with the DEFAULT --expect => RC=1 OPEN-SET MISMATCH — correct and
     expected (the default is a hand-maintained copy of the open set; editing it
     to "" is the completing session's job, history: t84 shipped, t89 and t100
     edited it at each closure).
  2. audit with `--expect ''` => RC=1 "MISMATCH vs expected ['']" — THE HOLE.
     `"".split(",") == [""]`, so want={""} and an empty open set can NEVER
     equal it. `--expect ''` is the only CLI way to express completion, so the
     grader made the goal's terminal state permanently red even when done
     correctly. ledger_index_check.py on the same fixture + an emptied STATE
     index block was already RC=0 — only the audit leg was broken.
  FIX (scripts/ledger_audit.py, one line + rationale comment):
  `want = {x.strip() for x in a.expect.split(",") if x.strip()}`.
  Validated by real execution, four branches, fixtures deleted after:
  (a) real ledger + real default => OK RC=0 (byte-identical regression);
  (b) fixture + --expect '' post-patch => OK RC=0;
  (c) clone with the default string emptied (the completing session's actual
      edit shape) + fixture => OK RC=0;
  (d) same clone vs the REAL ledger => FAILED RC=1 loudly (empty default cannot
      silently bless open rows). py_compile OK.

## ACCEPTED BOUNDARIES measured this turn (documented, deliberately not fixed)
1. status_of is position-dependent: the FIRST pipe-wrapped cell starting
   CLOSED/open/BLOCKED decides the row (ledger_audit.py:52-61, t85 design).
   Fixture F5 proved a careless paste "| CLOSED t40 note |" into OQ-021's
   QUESTION field flips the row to CLOSED. Both gate-3t legs still caught it
   (audit RC=1 open-set mismatch; index RC=1 "STATE lists OQ-021 open; record
   says CLOSED") — LOUSY MESSAGE, NO SILENT GREEN. A strict column-position
   rule was rejected: real rows OQ-003/OQ-012/OQ-016 legitimately put
   status-shaped words outside column 2 (e.g. OQ-016 "| open (sub-laws CLOSED:
   income channel law 138/139...)"), so enforcement would false-positive
   without first reformatting the record — out of scope for an idle turn.
2. --expect remains a hand-maintained duplicate of the open set (t84 design);
   every closure must edit it. Deriving it from the record would be circular;
   the mismatch message names both sets so the repair is mechanical.
3. Loop supervisor (see above) is observable but un-adjudicated by design.

## Gate traversal verified (answers t158's open question in the negative)
Stage 3t IS unavoidable: gate.sh has `set -u` but NOT `set -e`, `err()` only sets
fail=1, and the ONLY `exit` is `exit $fail` at gate.sh:464 — so 3t at :418/:421
runs on every invocation, including the harness post-flight
(loop_one_task.sh:119 `bash scripts/gate.sh > post_gate.log`). No early-exit
route exists. t158's enforcement therefore holds; nothing to fix there.

## In-progress probe (t158 law, third recursion test)
t158 law: "shipping a checker is not enforcement — the checker must sit in a
path the loop cannot exit through." t158 wired ledger_audit + ledger_index_check
into gate.sh stage 3t (gate.sh:418, :421 confirmed by grep this turn). Open
question for THIS turn, asked with the t145/t158 method (what does the leg DO
with its input; can the path be exited without it):
  1. Does the harness post-flight actually traverse gate.sh, i.e. is stage 3t
     reachable from the loop's own exit path (loop_one_task.sh)?
  2. What does ledger_index_check.py DO with STATE.md — does its parser see the
     whole ledger block, or can a row hide from it the way v1 ids hid behind the
     exemption t157 recorded?
