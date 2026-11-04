# t147 — IDLE re-check #34 (WIP, bank as I go)

Session start 2026-10-28 01:21:48 (from work/r1/loop/iter-20261028-012148-69.log).
HEAD at start: 4ad8a23 (t146).

## Finding 1 — both triggers NEGATIVE (tool, not hand-derived)
`python3 scripts/r1_idle_probe.py` RC=0 @ 01:22:47:
- (A) newest playcap dir playcap-20261014-224611; live-timeline.jsonl
  mtime_ns=1793043841304000000 size=5691796463 — 37th consecutive
  byte-identical reading (t111..t147); zero dosbox procs; find sweep
  cutoff 01:21:48 -> 4 files, non-loop: none; r1_t85g_sitting.py correctly
  NOT run.
- (B) clean tracked tree, no STEERING, B3 HEAD == journal sha 4ad8a23
  (journal row 68 verified by `tail -4 journal.tsv | cat -A`: last tab
  field "(re-check\t4ad8a23 t146: ..."), prompt-69 vs prompt-68 58/58
  lines digit-stripped delta 0.
=> honest negative. No ledger row closed (strict-close). §3 answer still
outstanding after 34 idle turns.

## Finding 2 — RETRACTED fabrication claim (bank as a law, it nearly burned a turn)
I read the probe's infra() source as `PLAYCAP/playcap/vnc/x11vnc.log` and,
when `stat` on that composed path failed, concluded the probe had FABRICATED
the printed "x11vnc.log mtime=.../30114" line. Wrong: PLAYCAP is
work/r1 (r1_idle_probe.py:45), so the leg reads work/r1/vnc/x11vnc.log,
which exists with EXACTLY the printed mtime (2026-10-27 17:30:18.172) and
size (30114, 404 lines). LAW: when a probe's verdict or output contradicts a
hand check, verify the probe's OWN resolved constants
(`grep -n '^[A-Z_]* =' probe.py`) before accusing it — my error was composing
a path from a variable NAME instead of its value. The t146 lesson says to
re-check paths/baseline; this iteration shows the re-check itself must use
resolved values, or it manufactures a false bug report.

## Finding 3 — the real hole (A4): the (A) trigger's liveness assumption is
## printed, never adjudicated
The (A) trigger is unfalsifiable unless the watcher is alive: a new sitting
only becomes visible as (a) a new playcap-* dir, (b) timeline growth, or
(c) a capture-side file newer than session start — and (b)/(c) are produced
BY `scripts/r1_playcap_watch.py` (pid 27774, verified alive this run:
cmdline `python3 scripts/r1_playcap_watch.py
/home/hrethric/projects/ascendancy/work/r1/playcap --no-exit`, fds open on
watch.out, watch.log, live-timeline.jsonl). If the watcher died while the
machine stayed up, Xvfb/x11vnc still print alive, dosbox is gone (user
finished), the timeline never grows, and every (A) leg says NEGATIVE — the
loop would keep reporting steady-state IDLE over a real capture, indefinitely
and undetectably. infra() only pattern-matches `Xvfb|x11vnc|python3` in
`ps` output: it prints python3 pids (this run 163246 = harness
mcp_death_supervisor, 163362 = probe child, both t118 noise) and asserts
liveness in prose without naming the watcher at all. Same class as t145
("touches X" != "adjudicates X") and t146 (all legs read the worktree).
FIX: measure the watcher by cmdline content (script name + the playcap dir),
matched in Python over `ps -eo pid=,args=` (NOT shell grep — self-match trap
t114, and comm truncates to 15 chars so `pgrep -x` on the script name can
never match `python3`). Dead watcher = CANNOT ADJUDICATE (A): print a loud
NOT-ADJUDICATED caution with the repair command, do NOT arm — arming asserts
a user decision that was never made (t117 law); the unverifiable case is the
harness's problem, not a trigger. R1_WATCH_SCRIPT env override so the dead
branch is testable.
