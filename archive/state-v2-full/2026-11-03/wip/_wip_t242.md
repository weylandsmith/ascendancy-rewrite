# _wip_t242 — trigger-armed idle adjudication (hand-authored; no generator writes docs/re/_wip_*.md — re-confirmed t225/t226/t228 greps: scripts/r1_idle_probe.py only READS them, gate.sh mentions _wip_ only inside a comment)

## S1 — Axis 1: no sitting (r214_triage.py RC=0 at 2026-10-31T02:21:28Z)
All three TRIGGER-A baselines equal the recorded values for the twenty-ninth
iteration running: ns_mtime 1793294532100000000, size 5,721,578,066,
tail-64KiB md5 9054cc6c66802e6f80431d4ffa1416ee. The script prints its own
"sitting delta: False". Zero comm-class dosbox/ascend.exe processes.
Tail intact: 400 rows / 0 bad json / turn 1086 / 275 distinct / exactly one
16-field key shape. r1_t85g_sitting.py correctly NOT run (t152 trap:
adjudicating an unchanged dir fabricates a sitting).

Baseline age INDEPENDENTLY RECOMPUTED, not carried forward: baseline ns
1793294532.100 == 2026-10-29T17:22:12.100Z; session epoch at triage
1793413288 == 2026-10-31T02:21:28Z => 118755.9 s = 32.9877 h, monotone against
t241's 32.8125 h at 2026-10-31T02:10:57Z (delta 631.0 s == the 10 m 31 s wall
gap exactly). The age chain in STATE.md stays self-corroborating.

## S2 — Axis 2: save axis bit-identical
1409 *.sav/*.gam under /home/hrethric (-xdev; population unchanged since t216).
Newest by %T@ == playcap/save/41.sav ns 1793294530.108 — BIT-IDENTICAL to
t216..t241. #2..#10 are 60/59/58/57/56/55/54/53/52.sav on the 10 s end-series
cadence (1793294520.040 / 510.004 / 500.004 / 489.988 / 479.980 / 469.964 /
459.956 / 449.944 / 439.952). The newest save is OLDER than the timeline
baseline, so the WATCHER-DEATH condition (save newer than timeline => watchers
died and hid a sitting) did NOT fire. Gap baseline - newest re-measured
1793294532.100 - 1793294530.108 = 1.992 s, twenty-fourth consecutive time.

## S3 — Honest negative (ledger unchanged)
NO row closed, none opened; docs/OPEN-QUESTIONS.md byte-untouched. With no
sitting, the two witness classes the open rows need — (a) a multi-volley battle
vs a NON-at-war owner (OQ-016 clamp witnesses, the only thing that closes the
zero-witness residue) and (b) a MID-CAMPAIGN slot with V=dword[0x482fb] > 1 AND
some byte[star+0x15] nonzero (OQ-021 S6 semantic non-join + P7 label question) —
are unobservable from the corpus, and strict-close forbids closing on a
plausible default. OQ-005 (index.txt + dims residue) and OQ-019 (per-commit
attack pricing) need a USER ruling, not measurement. OQ-005 / OQ-016 / OQ-019 /
OQ-021 stay OPEN. Nothing beyond the two adjudication axes was censused (t212
law); no static route re-trod (t213 S7: static corpus formally EXHAUSTED).
ledger_audit deliberately NOT re-run out-of-band (no sitting => the open set
cannot have moved); it runs as a gate stage on this iteration.

## S4 — Watchers (incidental read from the triage census; nothing killed)
Wrapper 27772 (bash, ppid 1, holds NO writer fd) + child 27774 (python3) +
orphans 260988 / 290953 / 292085 (all r1_playcap_watch.py --no-exit). No new
orphans since t215, no retirements. Retiring them remains a supervised-session
decision (USER ASK #3); research iterations must NOT kill them.

## S5 — No new content manufactured
t242 held the ~4-call cap at exactly the two assigned axis calls (plus the
session-start ls/stat that precedes the loop contract). No new code path, no fd
census, no static hunt, no ledger-marker grep, no re-print of the same negative
as a "finding". No steering override applied: no note was prepended to the
session prompt, no OQ-019/OQ-005 ruling appeared in docs/BLOCKED.md, no
supervised-session grant materialised. Scheduling fact (control-plane only,
banked once per t218 law): a twenty-ninth session was again re-armed ~10.5 min
after t241 despite the explicit DO-NOT-RUN-ON-CADENCE clause; the remedy is in
USER ASKS, not in an iteration.
