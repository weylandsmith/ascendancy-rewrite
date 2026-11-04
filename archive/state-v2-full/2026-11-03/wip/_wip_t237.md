# t237 — TRIGGER-ARMED IDLE ADJUDICATION (24th consecutive, no new content)

Deliberately content-free per the t221..t236 cap law: two assigned axis calls,
no new code path, no fd census, no static hunt, no out-of-band ledger audit.

## S1 — Axis 1: r214_triage.py (RC=0, 2026-10-31T01:37Z)
All three TRIGGER-A baselines byte-identical to t214..t236:
  full-ns mtime 1793294532100000000 == baseline (True)
  size          5721578066          == baseline (True)
  tail-64KiB md5 9054cc6c66802e6f80431d4ffa1416ee == baseline (True)
  script's own verdict line: "sitting delta: False"
Game process census: zero comm-class dosbox/ascend.exe.
Tail healthy: 400 rows, 0 bad json, turn 1086, 275 distinct, one key shape.
Sitting script (r1_t85g_sitting.py) correctly NOT run — t152 trap (no delta
=> nothing to adjudicate).

Baseline age INDEPENDENTLY RECOMPUTED (not trusted from STATE):
  baseline ns 1793294532.1 == 2026-10-29T17:22:12.100Z
  session epoch 1793410677 == 2026-10-31T01:37:57Z
  => 116144.9 s = 32.2625 h old.
  Monotone vs t236's 32.1397 h at 01:30:35Z; delta 442.0 s == the 7 m 22 s
  wall-clock gap between the two sessions exactly.

## S2 — Axis 2: save axis (one find, ns precision)
Population 1409 files — unchanged since t216.
Newest: work/r1/playcap/save/41.sav ns 1793294530.108 (correct newest per the
t215 law + t216 ns-precision fix; NOT 60.sav).
#2..#10 = 60/59/58/57/56/55/54/53/52.sav on the ~10 s end-series cadence.
All saves OLDER than the timeline baseline => watcher-death gap stays closed.
Gap re-measured: 1793294532.100 - 1793294530.108 = 1.992 s (19th consecutive
identical measurement).

## S3 — Honest negative (ledger untouched)
No sitting => the witness classes (multi-volley vs non-at-war owner for OQ-016;
mid-campaign star with byte[star+0x15] nonzero for OQ-021) are UNOBSERVABLE in
this session's data. Under strict-close, nothing closes:
OQ-005 / OQ-016 / OQ-019 / OQ-021 stay OPEN. OPEN-QUESTIONS.md was not modified.
Cheap re-derivation only (grep '| open |' docs/OPEN-QUESTIONS.md -> 6 markers,
all inside those four rows — same as t219's measured premise); ledger_audit ran
ONLY as a gate stage.
Watcher population unchanged: wrapper 27772 (bash, no writer fd) + child 27774
+ orphans 260988/290953/292085. No new orphans, no retirements. Nothing killed
(research iterations must not kill watchers — supervised-session decision).
CONSEQUENCE (unchanged since t218): the next move is new play or a user
decision, not another research iteration.
