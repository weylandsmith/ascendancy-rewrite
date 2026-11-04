# t221 — WIP (idle adjudication, eighth iteration, deliberately content-free)

Session start 2026-10-30T23:18:02Z. No steering note was prepended to this
session's prompt, so the assigned two axes (docs/STATE.md NEXT ACTION t221) were
the whole job. Per the t221 sizing clause the session was capped at ~4 calls
with no new code path, no fd census, no static hunt, and no re-print of the same
negative as if it were a finding.

## S1 — Axis 1: no sitting (TRIGGER-A all three equal, 8th running)

`python3 scripts/r214_triage.py` RC=0 at 2026-10-30T23:18:02Z:

  ns_mtime 1793294532100000000 == 1793294532100000000: True
  size     5721578066          == 5721578066:          True
  tail md5 9054cc6c66802e6f80431d4ffa1416ee == 9054cc6c66802e6f80431d4ffa1416ee: True
  => sitting delta: False
  dosbox/ascend.exe processes: 0
  tail shape: 400 rows / 0 bad json / turn 1086 / 275 distinct / one key shape

Baseline age 29.94 h (measured in-session: `time.time()` 1793402305.901 vs
baseline 1793294532.100). t220's 29.80 h at 23:09:59Z plus ~8.4 min is exactly
consistent, so the age stamps on both iterations are mutually corroborating
rather than independently suspicious. `scripts/r1_t85g_sitting.py` was
correctly NOT run — with no sitting delta it would only re-read the same tail
(docs/BLOCKED.md t152 trap).

## S2 — Axis 2: save axis bit-identical (watcher-death gap stays closed)

  find /home/hrethric -xdev \( -name '*.sav' -o -name '*.gam' \) -printf '%T@ %p\n' | sort -rn

  count = 1409 files (population unchanged since t216)
  #1 1793294530.1080000000 .../work/r1/playcap/save/41.sav
  #2 1793294520.0400000000 .../work/r1/playcap/save/60.sav   (10.068 s older)
  #3 1793294510.0040000000 .../work/r1/playcap/save/59.sav

Newest save is 41.sav at ns 1793294530.108 — BIT-IDENTICAL to t216/t217/t218/
t219/t220. Gap to the timeline baseline re-measured 1.992 s
(1793294532.100 - 1793294530.108), confirming t219's correction of t218's
1.892 s slip for the third consecutive iteration. The newest save remains
OLDER than the timeline baseline, so the failure mode the axis exists to catch
— watchers dying and hiding a sitting behind a newer save — did not occur.
Zero saves since the 2026-10-29 13:22 end series.

## S3 — Adjudication and honest negative

EIGHT consecutive byte-identical adjudications stand (t214..t221). Both
adjudication axes and the watcher population (wrapper 27772 bash / no writer fd,
child 27774, orphans 260988/290953/292085 — no new orphans, no retirements,
now stable ~15 h) are unchanged. Nothing killed: killing watchers is a
supervised-session decision, not a research-iteration action.

HONEST NEGATIVE: no ledger row moved. OQ-016, OQ-021, OQ-019 and OQ-005 all
stay OPEN. With no sitting there are no witnesses, so OQ-016's multi-volley
clamp witnesses and OQ-021's mid-campaign slot comparator firing
remain unobservable; OQ-019 and OQ-005 wait on a user ruling. Under strict-close
an idle reproduction cannot close anything, and this iteration deliberately
manufactured no eighth angle to look busy (t220's idle discipline, applied).
docs/OPEN-QUESTIONS.md untouched — nothing there needed annotating.

The next move remains new play or a user decision, not another research
iteration. Re-arm the harness on the r214_triage trigger against the three
TRIGGER-A baselines in S1.
