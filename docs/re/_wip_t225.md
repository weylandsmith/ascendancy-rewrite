# _wip_t225 — TRIGGER-ARMED IDLE ADJUDICATION (hand-authored; no generator touches docs/re/_wip_*.md)

Purpose per docs/STATE.md NEXT t225: run the two adjudication axes, expect the
idle result, write one line, STOP. This file is deliberately CONTENT-FREE: an
idle iteration cannot move the ledger, so nothing here claims new knowledge.
Twelfth consecutive byte-identical reproduction (t214..t225).

## S1 — Axis 1: timeline baseline (python3 scripts/r214_triage.py, RC=0, session clock 2026-10-30T23:53:29Z)
All three TRIGGER-A baselines equal the recorded values a twelfth iteration
running [verified]:
  ns_mtime  1793294532100000000 == 1793294532100000000 -> True
  size      5721578066          == 5721578066          -> True
  tail-64KiB md5 9054cc6c66802e6f80431d4ffa1416ee      -> True
  script's own verdict line: "=> sitting delta: False"
Game process axis: ZERO comm-class dosbox/ascend.exe processes [verified] — the
process side corroborates the file-side negative, so scripts/r1_t85g_sitting.py
was correctly NOT run (t152 trap: adjudicating an unchanged dir fabricates a
sitting).
Tail health: 400 rows, 0 bad json, turn 1086, 275 distinct keys, exactly ONE key
shape (16-field set unchanged).
Baseline age INDEPENDENTLY RECOMPUTED, not carried forward from STATE: baseline
ns == 2026-10-29T17:22:12.100Z, session clock 2026-10-30T23:53:29Z => 30 h
31 m 17 s = 30.52 h. Monotone against t224's 30.35 h at 23:42:56Z — the delta
0.17 h matches the 10.5 min wall gap between the two sessions, so the age chain
in STATE.md stays self-corroborating rather than a copied number.

## S2 — Axis 2: save axis (one find by %T@, /home/hrethric -xdev, *.sav|*.gam)
1409 files — population unchanged since t216 [verified]. Newest ==
work/r1/playcap/save/41.sav ns 1793294530.108 — BIT-IDENTICAL to t216..t224.
#2..#8: 60.sav 1793294520.040 / 59.sav 1793294510.004 / 58.sav 1793294500.004 /
57.sav 1793294489.988 / 56.sav 1793294479.980 / 55.sav 1793294469.964 /
54.sav 1793294459.956 — the 10 s end-series cadence of the 2026-10-29 13:22
closing saves.
Gap to the timeline baseline: 1793294532.100 - 1793294530.108 = 1.992 s,
re-measured for the seventh consecutive iteration. No save post-dates the
baseline, so the "watchers died and hid a sitting" gap stays CLOSED on this
independent signal (a player who advances leaves a newer autosave slot
regardless of watcher health — t215 law).

## S3 — HONEST NEGATIVE (strict-close, docs/GOAL.txt)
No sitting => the two witness classes the open rows need are UNOBSERVABLE this
iteration: the OQ-016 in-corpus clamp witnesses (attack a non-at-war power) and
the OQ-021 mid-campaign-slot semantic join. OQ-005 (index.txt + dims residue)
and OQ-019 (per-commit attack pricing) need a USER ruling, not measurement.
Therefore NO row closed and NO row annotated; docs/OPEN-QUESTIONS.md untouched.
ledger_audit was NOT run out-of-band (with no sitting the open set cannot have
moved; t219 measured rows=19 open=OQ-005/016/019/021 closed=15 from the primary
source) — it ran only as a finish-sequence/gate stage.
Discipline held: cap ~4 calls (2 assigned axes + 1 generator-safety grep), no
new code path, no fd census, no static hunt (corpus formally EXHAUSTED at t213
S7), no re-print of the same negative as a "finding".
Watcher population as an incidental read of the triage call — wrapper 27772
[bash, ppid 1, holds no writer fd] + child 27774 [python3] + orphans 260988 /
290953 / 292085; uptimes ~4d12h / ~4d12h / ~1d20h / ~1d07h / ~1d07h. No new
orphans since t215, no retirements. Nothing killed (retiring watchers is a
supervised-session decision, user ask #3).
