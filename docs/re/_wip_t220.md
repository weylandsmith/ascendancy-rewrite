# t220 — sitting adjudication (two axes only), seventh consecutive idle

Session 2026-10-30T23:09Z. Assigned task: docs/STATE.md NEXT t220 = trigger-armed
idle, two axes, no third code path. No steering note was prepended to this
session's prompt; no user ruling appeared on OQ-019/OQ-005 in docs/BLOCKED.md;
no supervised-session grant was granted. So the two axes were run and nothing
else.

## S1 — Axis 1 (r214_triage.py, RC=0): idle, seventh consecutive time
All three TRIGGER-A baselines equal the recorded values again:
  ns_mtime  1793294532100000000  == baseline  -> True
  size      5,721,578,066        == baseline  -> True
  tail-64KiB md5 9054cc6c66802e6f80431d4ffa1416ee == baseline -> True
  => script's own verdict line: "sitting delta: False"
Zero dosbox/ascend.exe comm-class processes. r1_t85g_sitting.py correctly NOT
run (t152 trap: adjudicating an unchanged capture dir fabricates a sitting).
Tail shape intact and healthy: last 400 rows, 0 bad json, turn 1086, 275
distinct keys, one key shape (n=400). Baseline age at 2026-10-30T23:09:59Z =
29.80 h (t219 measured 29.63 h ten minutes earlier).

## S2 — Axis 2 (save axis, one find by %T@): bit-identical to t216..t219
Newest *.sav/*.gam anywhere under /home/hrethric (-xdev, 1409 files — same
population count as t216/t217/t218/t219):
  1793294530.1080000000  work/r1/playcap/save/41.sav
  1793294520.0400000000  work/r1/playcap/save/60.sav
  1793294510.0040000000  work/r1/playcap/save/59.sav
  1793294500.0040000000  work/r1/playcap/save/58.sav
Gap to the timeline baseline = 1793294532.1 - 1793294530.108 = 1.992 s
(re-measured in-session; confirms t219's fix of t218's 1.892 s slip). No save
post-dates the baseline, so the "watchers died and hid a sitting" gap stays
closed on the independent signal. Zero saves since the 2026-10-29 13:22 end
series.

## S3 — Ledger: NO row moved, and no new content claimed
Strict-close honored: with no sitting there is no new witness class, so OQ-016
(clamp witnesses) and OQ-021 (comparator firing + writer watchpoint) stay open
unmodified; OQ-019 needs the per-commit attack-pricing ruling; OQ-005 needs
index.txt + dims. docs/OPEN-QUESTIONS.md was NOT touched this iteration
(nothing to annotate). No static route re-trod (t213 S7 exhaustion stands),
no fresh fd census (stable t215..t219), no repeat ledger audit presented as
content (t219 S3 owns that measurement; both ledger checks still ran as GATE
stages, as required).

## S4 — Incidental watcher read (from the triage call's own fixed census)
wrapper 27772 [bash, ppid 1] + writer child 27774 + orphans 260988 / 290953 /
292085; script reports total 5 processes, 4 flagged orphaned (it counts the bash
wrapper, which holds no writer fd, in that flag). No new orphans and no
retirements since t215's census. Nothing was killed — orphan retirement remains
a supervised-session user decision, not a research-iteration action.
