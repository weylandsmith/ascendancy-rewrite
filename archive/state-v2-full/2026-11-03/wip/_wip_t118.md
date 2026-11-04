# t118 — IDLE re-check #5 (2026-10-27, session started 22:10:42 EDT)

Assignment: docs/STATE.md "## NEXT ACTION (exactly one)" = IDLE block — run
`python3 scripts/r1_idle_probe.py` at session start, before editing docs. No
steering note (prompt-40.txt is byte-identical to prompt-39.txt modulo digits;
`grep -in steering` hits only the standing instruction line at :14).

## P1 — Tool run (first execution by a session other than its author)
`python3 scripts/r1_idle_probe.py` at 22:12:21.769 EDT -> **PROBE_RC=0**,
VERDICT line "IDLE — neither trigger; honest negative, keep the IDLE block".
This is the first INDEPENDENT validation of the t117 tool: the t117 session was
its author and had already hand-adjudicated the same signals, so until now no
fresh reader had tested whether the tool's printed evidence is sufficient to
reproduce the verdict without extra probing. It is — every leg prints its own
number (mtime_ns, size, dir name, pid table, diff output), and all of them
matched my hand re-reads below. No tool defect found this iteration.

## P2 — Trigger (A) NEW CAPTURE: NEGATIVE
- newest playcap dir `playcap-20261014-224611` (unchanged since t111;
  `selftest-t111-playcap` correctly excluded by the tool).
- `work/r1/playcap/live-timeline.jsonl` mtime_ns=1793043841304000000
  (= 2026-10-26 15:44:01.304 EDT) size=5691796463 — byte-identical to the
  frozen baseline, 8th consecutive identical reading (t111..t118).
- dosbox procs: none.
- `find work/r1 -type f -newermt 2026-10-27 22:10:42` -> 4 files, all under
  work/r1/loop/ (harness bookkeeping), non-loop: none.
- Consequence: `scripts/r1_t85g_sitting.py` correctly NOT run.

## P3 — Trigger (B) USER DECISION: NEGATIVE
- HEAD at session start = 35a9027 (t117); `git diff HEAD --name-only` empty;
  `git status --porcelain` (tracked) empty; no untracked files at probe time.
- No delta outside loop-owned paths (the decisive sub-leg per the t117 law).
- No STEERING file. The stop-report §3 answer (accept/reject documented
  defaults OQ-003 entropy / OQ-005 dims / OQ-019 sugar-cube / OQ-023
  threshold-only; authorize capture sittings; resume t89a code work) is still
  outstanding after five idle turns.

## P4 — Infra liveness (why the negatives are trustworthy) + one noise note
Xvfb :9 pid 1196 (11d06h), x11vnc :5910 pid 1207 (11d06h), watcher python3
pid 27774 (1d14h) — all alive. `x11vnc.log` mtime 2026-10-27 17:30:18 / 30114 B
unchanged since t112: still ZERO connect attempts against the t111-FIXED
launch path.
NEW (minor, worth knowing so the next session doesn't chase it): the probe's
INFRA leg printed two extra python3 rows besides the watcher pair —
127729 = `~/.hermes/hermes-agent/tools/mcp_death_supervisor.py` (ppid 127711,
started 22:10:42 = this session's harness) and 127778 (already gone when I
re-checked with `ps -p`, so a transient child of the probe run itself: the
probe shells out via `subprocess.run(..., shell=True)`, so its own
git/find/stat children appear in a `ps -eo` snapshot taken mid-run).
Neither is capture-side: the (A) find sweep — which is the load-bearing leg —
saw no non-loop file, and the dosbox leg is `comm`-matched so it cannot pick
these up. Do NOT treat Hermes-own or probe-own python rows as trigger evidence;
the trigger classes are dosbox processes and capture files, nothing else.

## P5 — Ledger
No row touched, no row closed. Strict-close: an honest idle negative is not
measurement of game behaviour. Loop stands 12 closed / 6 open
(OQ-003, OQ-005, OQ-016, OQ-019, OQ-021, OQ-023) — `scripts/ledger_audit.py`
LEDGER AUDIT OK. No banked law falsified. No code change, no game/ change, no
watch or census run (per stop-report §6 discipline: an idle turn is the
two-trigger probe and nothing else).
