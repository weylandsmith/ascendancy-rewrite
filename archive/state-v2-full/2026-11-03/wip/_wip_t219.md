# t219 — sitting adjudication (two axes only), sixth consecutive idle

Session started 2026-10-30 ~22:55 EDT. Assigned task: docs/STATE.md NEXT t219
(two-call adjudication, four calls max, then FINISH). Static corpus stays
EXHAUSTED per t213 S7 — no static route attempted, none invented.

## S1 — Axis 1: TRIGGER-A baselines byte-identical a SIXTH iteration

`python3 scripts/r214_triage.py` RC=0, verbatim comparisons:

| axis | recorded | this session | equal |
|---|---|---|---|
| ns_mtime (live-timeline.jsonl) | 1793294532100000000 | 1793294532100000000 | yes |
| size | 5,721,578,066 | 5,721,578,066 | yes |
| tail-64KiB md5 | 9054cc6c66802e6f80431d4ffa1416ee | 9054cc6c6680431d4ffa1416ee | yes |

`=> sitting delta: False`. `dosbox/ascend.exe processes: 0` (process side
corroborates the file-side negative). Tail shape sane and unchanged in kind:
last 400 rows, 0 bad-json, turn 1086, 275 distinct rows, one key shape n=400 —
i.e. the file is intact, not truncated or rotated.

Baseline is now 29.63 h old at measurement time (2026-10-30T23:00:15Z).
`scripts/r1_t85g_sitting.py` correctly NOT run — t152 trap: adjudicating an
unchanged directory fabricates a sitting.

## S2 — Axis 2: save axis bit-identical (third time)

`find /home/hrethric -xdev \( -name '*.sav' -o -name '*.gam' \) -printf '%T@ %p\n'
| sort -rn`:

    1793294530.1080000000  work/r1/playcap/save/41.sav
    1793294520.0400000000  work/r1/playcap/save/60.sav
    1793294510.0040000000  work/r1/playcap/save/59.sav
    1793294500.0040000000  work/r1/playcap/save/58.sav
    1793294489.9880000000  work/r1/playcap/save/57.sav

Population 1409 files (unchanged since t216). Newest save is 41.sav, exactly as
t216/t217/t218 recorded, and it PRE-DATES the timeline baseline, so the
"watchers died and hid a sitting" gap stays closed on this iteration too.
Zero saves written since the 2026-10-29 13:22 end-of-sitting series.

PRECISION CORRECTION (small, honest): t218 stated 41.sav sits "1.892 s older"
than the baseline. The arithmetic on the two recorded values is
1793294532.100 − 1793294530.108 = **1.992 s**. The conclusion is unaffected
(sign and magnitude class unchanged: sub-2 s gap, save older than timeline), so
no row and no prior verdict moves — but the number in this file is the correct
one and t218's is a slip in prose, not a measurement conflict.

## S3 — NEW THIS ITERATION: the idle answer's premise was RE-MEASURED, not trusted

Six identical idles means the loop is now answering a question by habit, so the
one claim that the idle answer rests on — "no open row can be advanced without
play or a user ruling" — was checked against the primary source instead of
against earlier WIP files (t213 S7 and t218 S5 both ASSERT this; neither is
evidence of it being true TODAY).

Two independent readings, this session:

1. `python3 scripts/ledger_audit.py` →
   `rows=19 open=['OQ-005', 'OQ-016', 'OQ-019', 'OQ-021'] closed=15` →
   **LEDGER AUDIT OK**. The open set is exactly the four rows named in STATE.md;
   the fifteen others are closed with cited evidence.
2. `grep -n '| open |' docs/OPEN-QUESTIONS.md` → six hits, all inside those four
   rows (232 = OQ-021 threshold; 583 = OQ-005 dims residue; 1240/1403/1431 =
   OQ-019; 1451 = OQ-016 in-flight/in-system residue). No stray `| open |`
   marker anywhere else in the 130 KB ledger.

So the premise HOLDS as of this iteration: 19 rows, 4 open, and all four open
rows need a witness that only new play (OQ-016 multi-volley vs non-at-war owner;
OQ-021 mid-campaign slot / live-st4), a user ruling (OQ-019 pricing, OQ-005
index.txt + dims), or a supervised watchpoint session (OQ-021 writer) can
produce. t219 therefore did NOT find a neglected non-play-gated row — that
negative is itself the useful result, because a stale ledger would have meant
six wasted iterations. [verified: both commands, RC printed above]

## S4 — Watcher population (incidental read of the S1 call, unchanged)

wrapper 27772 (bash, ppid 1, up 4-11:14) + child 27774 (python3) + orphans
260988 / 290953 / 292085 (python3, ppid 1) = 5 processes, 4 orphaned. Identical
to t215..t218; no new orphans, no retirements. Nothing was killed — retiring
them is a supervised-session decision (standing ask 3).

## Verdict

NO SITTING. No ledger row moved (strict-close honored; no plausible default was
allowed to close anything; no new measurement was obtainable). The harness, not
a research iteration, owns the next move: re-arm on the r214_triage trigger
rather than cadence until one of the three user decisions lands.

## Standing user asks (unchanged since t216)

1. PLAY: a few turns mid-campaign attacking a NON-AT-WAR power, then save —
   kills the OQ-016 witness ask and the OQ-021 comparator-firing ask at once.
2. RULE on OQ-019: may the rewrite model per-commit attack pricing?
3. HYGIENE: retire the three orphaned watchers (260988/290953/292085) before the
   next capture. S4 keeps this measurement-stable across t215..t219.
