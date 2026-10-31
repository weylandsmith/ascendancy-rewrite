# _wip_t228 — TRIGGER-ARMED IDLE ITERATION (nothing here is new content)

Safety pre-check (t226 rule, re-run by this session): no generator touches
docs/re/_wip_*.md — scripts/r1_idle_probe.py only READS the pattern (L50, L361,
L373, L389) and scripts/gate.sh mentions it inside a comment (L373). Verified
this session with a grep over scripts/*.sh scripts/*.py. Hand-authoring is safe.

## S1 — Axis 1, r214_triage.py, RC=0 at 2026-10-31T00:16:43Z
work/r1/playcap/live-timeline.jsonl: ns_mtime 1793294532100000000,
size 5721578066, tail-64KiB md5 9054cc6c66802e6f80431d4ffa1416ee — all three
EQUAL to the TRIGGER-A baselines for the fifteenth iteration running; the script
prints its own "sitting delta: False". Zero comm-class dosbox/ascend.exe. Tail
healthy: 400 rows, 0 bad json, turn 1086, 275 distinct, one key shape (16 keys,
identical to the t227 print).
Baseline age INDEPENDENTLY RECOMPUTED, not carried forward: baseline ns ==
2026-10-29T17:22:12.100Z (date -u -d @1793294532 -> 2026-10-29T17:22:12),
session clock 2026-10-31T00:16:43Z => 30 h 54 m 31 s = 30.91 h, monotone against
t227's 30.80 h at 00:09:56Z (delta 0.11 h ~ the 6.8 min wall gap). The sitting
script was NOT run (t152 trap: no sitting => nothing to adjudicate).

## S2 — Axis 2, save axis, bit-identical
1409-file population unchanged (unchanged since t216). Newest
work/r1/playcap/save/41.sav ns 1793294530.108 — NOT 60.sav (10.068 s older,
1793294520.040); #2..#8 are 60/59/58/57/56/55/54.sav on the 10 s end-series
cadence, byte-identical ns values to t227's print. Newest save is OLDER than the
timeline baseline, so the watcher-death condition did NOT fire. Gap
baseline-newest re-measured 1.992 s (1793294532.100 - 1793294530.108), tenth
consecutive time.

## S3 — Conclusion
Fifteenth consecutive byte-identical adjudication (t214..t228). Watcher
population unchanged: wrapper 27772 (bash, no writer fd) + child 27774 + orphans
260988/290953/292085; no new orphans, no retirements; nothing killed
(supervised-session decision, t215 law writerhood = open fd, not process
presence). NO ledger row closed — strict-close: with no sitting the witness
classes for OQ-016 (multi-volley battle vs a non-at-war owner) and OQ-021
(mid-campaign slot, V=dword[0x482fb]>1 && some byte[star+0x15] nonzero) are
unobservable, and a plausible default never closes a row. ledger_audit NOT
re-run out-of-band (no sitting => the open set cannot have moved); it runs as a
gate stage regardless. Honest negative banked here; OPEN-QUESTIONS.md untouched.
No new axis, no third code path, no fresh fd census, no static hunt (corpus
formally EXHAUSTED t213 S7). Session cost: the 2 assigned axis calls plus the
re-read of STATE.md's NEXT ACTION and this file's finish sequence.
