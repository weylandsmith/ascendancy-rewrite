# t148 working notes — IDLE re-check #35 (2026-10-28 01:41 EDT)

Assignment: IDLE two-trigger probe only (stop-report §6 discipline; no
watch, no census, no ledger touch).

## P1 — probe run
`python3 scripts/r1_idle_probe.py` RC=0 at 01:41:11 (cutoff 01:39:21 from
iter-20261028-013921-70.log). (A) NEGATIVE: newest playcap dir
playcap-20261014-224611; live-timeline.jsonl mtime_ns 1793043841304000000 /
5691796463 B (38th consecutive byte-identical reading t111..t148); zero
dosbox procs; find sweep 4 files all work/r1/loop/; A4 watcher ALIVE pid
27774. (B) NEGATIVE: clean tracked tree at 153a6f4; no STEERING; prompt-70 vs
prompt-69 digit-stripped delta 0 (58/58 lines); B3 HEAD == journal sha
153a6f4. r1_t85g_sitting.py correctly not run.

## P2 — t147 NEAR-MISS law, run preemptively
Resolved the probe's constants from source before trusting the verdict:
r1_idle_probe.py:51 PLAYCAP=work/r1, :52 TIMELINE=PLAYCAP/playcap/
live-timeline.jsonl, :56 BASE_SIZE=5691796463. Independent os.stat: size
5691796463, mtime_ns 1793043841304000000 — exact match with the printed
values. No divergence; verdict reproducible by a fresh reader without
trusting the tool's prose.

## P3 — coverage review (no change made)
(A) legs: playcap dir / timeline size+mtime / dosbox proc / session-start
find sweep / A4 watcher liveness. (B) legs: worktree content delta /
STEERING glob / prompt digit-stripped content diff / B3 committed-decision.
Every documented user-answer route (stop-report §3) has an adjudicating leg.
Asymmetry noted, declined: find-sweep cutoff is session-start, so a
capture-side file between iterations is invisible to that leg alone — but a
real capture always also creates a playcap-<ts> dir and grows the timeline
(both checked against pre-session baselines), so that leg is
redundant-not-blind for captures; tightening it adds false-positive surface.

## P4 — hygiene + finish
Bank hygiene fresh: grep -rln stop-report scripts/ -> only
r1_idle_probe.py + __pycache__ (no regeneration trap); stop-report.md zero
diff vs HEAD at 1292 lines before appending §41. Ledger untouched
(strict-close honest negative). Gate + ledger audit run at finish.
