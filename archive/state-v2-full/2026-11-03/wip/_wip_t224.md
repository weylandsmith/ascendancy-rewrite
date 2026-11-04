# _wip_t224 — trigger-armed idle adjudication (hand-authored; no generator
# touches docs/re/_wip_*.md — re-grepped scripts/ this iteration, only
# scripts/r1_idle_probe.py references the pattern and it only READS it)

Idle iteration. No sitting, no steering note, no user ruling materialised.
This file exists so STATE.md stays short; NOTHING in it is new content — it is
the eleventh byte-identical reproduction of the t214..t223 adjudication, plus an
independently recomputed baseline age. Deliberately ~4 tool calls
(2 assigned axes + 1 age/grep check), per the t224 assignment.

## S1 — Axis 1: scripts/r214_triage.py RC=0 at 2026-10-30T23:42:2xZ
All three TRIGGER-A baselines for work/r1/playcap/live-timeline.jsonl equal the
recorded values for the eleventh iteration running [verified]:
  ns_mtime  1793294532100000000 == 1793294532100000000  True
  size      5,721,578,066       == 5,721,578,066        True
  tail-64KiB md5 9054cc6c66802e6f80431d4ffa1416ee       True
The script prints its own "sitting delta: False". ZERO comm-class
dosbox/ascend.exe processes, so scripts/r1_t85g_sitting.py was correctly NOT run
(t152 trap: adjudicating an unchanged dir fabricates a sitting).
Tail intact: 400 rows / 0 bad json / turn 1086 / 275 distinct / exactly ONE key
shape (n=400, the standard 15-key capture row).

Baseline age RECOMPUTED, not carried forward: baseline ns 1793294532.100 ==
2026-10-29T17:22:12.100Z; session clock 2026-10-30T23:42:56Z ⇒ 1 d 6 h 20 min
44 s == 30.35 h. Monotone against t223's 30.21 h at 23:34:45Z (delta 0.14 h ≈
the 8.2 min wall gap), so the age chain in STATE.md remains self-corroborating.

## S2 — Axis 2: save axis (find /home/hrethric -xdev *.sav/*.gam, %T@-sorted)
1409 files — population unchanged since t216. Newest six, all in
work/r1/playcap/save/ and all the 2026-10-29 13:22 end-of-sitting series:
  41.sav 1793294530.108   <-- newest
  60.sav 1793294520.040
  59.sav 1793294510.004
  58.sav 1793294500.004
  57.sav 1793294489.988
  56.sav 1793294479.980
BIT-IDENTICAL to t216..t223. Newest save is still OLDER than the timeline
baseline ns 1793294532.100, so the "watchers died and hid a sitting" gap stays
closed on the independent signal (t215 law: a player who advances leaves a newer
autosave slot regardless of watcher health). Gap re-measured
1793294532.100 - 1793294530.108 = 1.992 s — sixth consecutive iteration.

## S3 — Honest negative (strict-close; no ledger row moved)
No sitting ⇒ the two witness classes remain unobservable, so:
  OQ-016 — zero in-corpus clamp/attack witnesses (needs a multi-volley battle vs
           a NON-at-war owner). STAYS OPEN.
  OQ-021 — displayed-count writer needs a runtime watchpoint (static route
           EXHAUSTED t212); comparator firing + the mid-campaign-slot semantic
           join need a mid-campaign save. STAYS OPEN.
  OQ-005 — needs a USER ruling on the index.txt + dims residue, not measurement.
           STAYS OPEN.
  OQ-019 — needs a USER ruling on per-commit attack pricing. STAYS OPEN.
No plausible default was allowed to close anything. ledger_audit was NOT run
out-of-band (with no sitting the open set cannot have moved; t219 measured
rows=19 open=OQ-005/016/019/021 closed=15); it ran only as a gate stage.
No new code path, no fd census, no static hunt (corpus formally EXHAUSTED t213
S7), nothing beyond the two adjudication axes censused (t212 law).

WATCHERS (incidental read from the triage call): wrapper 27772 [bash, ppid 1,
holds NO writer fd] + child 27774 [python3] + orphans 260988 / 290953 / 292085.
No new orphans since t215, no retirements (uptime ~4d12h / ~1d20h / ~1d07h /
~1d07h). Nothing killed — retiring them is a supervised-session decision
(user ask #3), not a research-iteration action.
