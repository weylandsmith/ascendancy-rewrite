# _wip_t236 — trigger-armed idle adjudication (hand-authored; 23rd consecutive)

Session clock 2026-10-31T01:30:34Z. No steering note prepended to this session's
prompt; no OQ-019/OQ-005 ruling visible in docs/BLOCKED.md changes (tree was
clean at 0335505). No override applies; the two assigned axes ran and nothing
else was censused (t212 law), no static route re-trod (t213 S7).

## S1 — Axis 1: r214_triage.py RC=0, no sitting
- ns_mtime 1793294532100000000 == baseline: True
- size 5,721,578,066 == baseline: True
- tail-64KiB md5 9054cc6c66802e6f80431d4ffa1416ee == baseline: True
- script's own verdict line: "sitting delta: False"
- ZERO comm-class dosbox/ascend.exe processes.
- r1_t85g_sitting.py correctly NOT run (t152 trap: adjudicating an unchanged dir
  fabricates a sitting).
- Baseline age INDEPENDENTLY RECOMPUTED: baseline ns == 2026-10-29T17:22:12.100Z;
  session epoch 1793410235 == 2026-10-31T01:30:35Z ⇒ 115702.9 s = 32.1397 h.
  Monotone against t235's 31.9892 h at 01:21:33Z (Δ 541.8 s == the 9 m 02 s wall
  gap between the two sessions exactly). Age chain stays self-corroborating.

## S2 — Axis 2: save axis bit-identical
1409 *.sav/*.gam under /home/hrethric (population unchanged since t216).
Newest playcap/save/41.sav ns 1793294530.108 — bit-identical to t216..t235.
#2..#10: 60/59/58/57/56/55/54/53/52.sav on the 10 s end-series cadence
(1793294520.040 / 510.004 / 500.004 / 489.988 / 479.980 / 469.964 / 459.956 /
449.944 / 439.952). Newest save OLDER than the timeline baseline ⇒ the
watcher-death condition did NOT fire. Gap baseline − newest re-measured
1.992 s (1793294532.100 − 1793294530.108), eighteenth consecutive measurement.

## S3 — Honest negative (the ledger outcome)
No sitting ⇒ the two witness classes the open rows need — (a) a multi-volley
battle vs a NON-at-war owner (OQ-016 clamp witnesses) and (b) a mid-campaign
slot with V=dword[0x482fb]>1 AND some byte[star+0x15] nonzero (OQ-021 S6
semantic join + P7 label) — are unobservable from the corpus. Strict-close
forbids closing on a plausible default, so OQ-005 / OQ-016 / OQ-019 / OQ-021
STAY OPEN and docs/OPEN-QUESTIONS.md is untouched. ledger_audit deliberately NOT
re-run out-of-band (no sitting ⇒ the open set cannot have moved); it ran as a
gate stage on this iteration. No rewrite code touched.

Watcher population incidental read (from the triage call, not a new census):
wrapper 27772 (bash, no writer fd) + child 27774 + orphans 260988/290953/292085;
no new orphans, no retirements; nothing killed (supervised-session decision,
USER ASK #3).
