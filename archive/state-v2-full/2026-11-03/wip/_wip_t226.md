# _wip_t226 — TRIGGER-ARMED IDLE ADJUDICATION (hand-authored; no generator touches docs/re/_wip_*.md)

Purpose per docs/STATE.md NEXT t226: run the two adjudication axes, expect the
idle result, write one line, STOP. This file is deliberately CONTENT-FREE: an
idle iteration cannot move the ledger, so nothing here claims new knowledge.
Thirteenth consecutive byte-identical reproduction (t214..t226).

## S1 — Axis 1: timeline baseline (python3 scripts/r214_triage.py, RC=0, session clock 2026-10-31T00:01:37Z)
All three TRIGGER-A baselines equal the recorded values a thirteenth iteration
running [verified]:
  ns_mtime  1793294532100000000 == 1793294532100000000 -> True
  size      5721578066          == 5721578066          -> True
  tail-64KiB md5 9054cc6c66802e6f80431d4ffa1416ee      -> True
  script's own verdict line: "=> sitting delta: False"
Game process axis: ZERO comm-class dosbox/ascend.exe processes [verified] — the
process side corroborates the file-side negative, so scripts/r1_t85g_sitting.py
was correctly NOT run (t152 trap: adjudicating an unchanged dir fabricates a
sitting).
Tail health: 400 rows, 0 bad json, turn 1086, 275 distinct, exactly ONE key
shape (the same 16-field set as t214..t225).
Baseline age INDEPENDENTLY RECOMPUTED, not carried forward from STATE: baseline
ns == 2026-10-29T17:22:12.100Z, session clock 2026-10-31T00:01:37Z => 30 h
39 m 25 s = 30.66 h. Monotone against t225's 30.52 h at 2026-10-30T23:53:29Z —
the delta 0.14 h matches the 8.1 min wall gap between the two sessions, so the
age chain in STATE.md stays self-corroborating rather than a copied number.

## S2 — Axis 2: save axis (one find by %T@, /home/hrethric -xdev, *.sav|*.gam)
1409 files — population unchanged since t216 [verified]. Newest ==
work/r1/playcap/save/41.sav ns 1793294530.108 — BIT-IDENTICAL to t216..t225.
#2..#8 continue the 10 s end-series cadence: 60.sav 1793294520.040 /
59.sav 1793294510.004 / 58.sav 1793294500.004 / 57.sav 1793294489.988 /
56.sav 1793294479.980 / 55.sav 1793294469.964 / 54.sav 1793294459.956.
Every save is OLDER than the timeline baseline (1793294532.100), so the
WATCHER-DEATH condition (a save newer than an unchanged timeline) is NOT
present — gap 1793294532.100 - 1793294530.108 = 1.992 s, re-measured an eighth
consecutive time and identical each time.

## S3 — Honest negative (strict-close)
No sitting => no new capture => the witness classes that the four open rows
require are unobservable this iteration. NO row closed: OQ-005 (index.txt +
dims residue), OQ-016 (multi-volley attack on a non-at-war power — the
zero-witness clamp residue), OQ-019 (per-commit attack pricing ruling),
OQ-021 (mid-campaign slot with V=dword[0x482fb]>1 and byte[star+0x15] nonzero)
all stay OPEN per docs/GOAL.txt (a plausible default never closes).
Ledger was NOT re-audited out-of-band: with no sitting the open set cannot have
moved (t221..t225 precedent), and both checks ran as gate stages at the end of
this iteration. Nothing beyond the two adjudication axes was censused (t212
law); no static route was re-trod (t213 S7: corpus formally EXHAUSTED); no new
code path, no fd census, no watcher killed (supervised-session decision —
population unchanged: wrapper 27772 bash holding no writer fd, child 27774,
orphans 260988/290953/292085, no new orphans, no retirements).
Call budget: 2 assigned axis calls total, then the finish sequence — inside the
~4-call cap.
