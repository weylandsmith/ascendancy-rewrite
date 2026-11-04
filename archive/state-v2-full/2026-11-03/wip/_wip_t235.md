# _wip_t235 — TRIGGER-ARMED IDLE adjudication (2026-10-31)

## S1 — Axis 1: r214_triage.py (one call, RC=0)
Run at 2026-10-31T01:21Z wall (session epoch 2026-10-31T01:21:33Z).

TRIGGER-A baselines for work/r1/playcap/live-timeline.jsonl — all three EQUAL:
  - full-ns mtime 1793294532100000000 == baseline: True
  - size 5,721,578,066 == baseline: True
  - tail-64KiB md5 9054cc6c66802e6f80431d4ffa1416ee == baseline: True
  - script's own verdict line: "sitting delta: False"

Game process axis: zero comm-class dosbox/ascend.exe processes.
Watcher census: unchanged population — wrapper 27772 (bash, ppid 1, no
writer-fd) + child 27774 (python3) + orphans 260988/290953/292085
(all --no-exit, ppid 1). No new orphans, no retirements. Nothing killed
(supervised-session decision per standing USER ASK 3).
Tail healthy: 400 rows, 0 bad json, turn 1086, 275 distinct, one key shape.

Baseline age INDEPENDENTLY RECOMPUTED:
  baseline ns 1793294532.100 == 2026-10-29T17:22:12.100Z
  (date -d @1793294532.100 -u, this session); session epoch
  2026-10-31T01:21:33Z => age 115161.2 s = 31.9892 h, monotone against
  t234's 31.6800->31.8455 h series (delta 517.3 s == the 8m37s wall gap
  exactly); gap to the save axis re-measured
     1793294532.100 - 1793294530.108 = 1.992 s (seventeenth consecutive
     identical measurement).

## S2 — Axis 2: save axis (one find, ns precision, t215 law + t216 fix)
Newest == playcap/save/41.sav ns 1793294530.1080000000 (NOT 60.sav,
10.068 s older; end-series cadence 60/59/58/57/56/55/54/53/52 confirmed).
Population 1409 files — bit-identical to t216..t234.
Newest save is OLDER than the timeline baseline => watcher-death gap stays
closed (no actionable inversion).

## S3 — Honest negative (ledger untouched)
No sitting => witness classes (multi-volley vs non-at-war owner for OQ-016;
mid-campaign slot byte[star+0x15] for OQ-021) are UNOBSERVABLE this
iteration. Per strict-close, nothing closes: OQ-005/016/019/021 stay OPEN.
OPEN-QUESTIONS.md not touched. No new code path, no fd census, no static
hunt (corpus formally EXHAUSTED at t213 S7). ledger_audit NOT re-run
out-of-band (no sitting => the open set cannot have moved; gate stages run
both ledger checks — see finish sequence). Twenty-second consecutive
byte-identical adjudication (t214..t235). Cap held: 2 assigned axis calls
plus finish-sequence bookkeeping only.
