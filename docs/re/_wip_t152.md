# t152 — IDLE re-check #39 (2026-10-28 ~02:28 EDT)

## Probe verdict
`python3 scripts/r1_idle_probe.py` RC=0 at 02:28:41 (session-start cutoff
02:26:59). Both triggers NEGATIVE. Full detail banked in stop-report §45.

Independent re-verification (t147 law, not trust):
- `stat -c '%Y %y %s'` on the timeline: 1793043841 / 2026-10-26
  15:44:01.304000000 / 5691796463 — exact match to probe AND to
  BASE_MTIME_NS/BASE_SIZE at r1_idle_probe.py:55-56.
- t151's CONTENT baseline reproduced byte-for-byte: head 64 KiB md5
  42a0bed0507f9052e2009ec94e9c27f1, tail 64 KiB md5
  1529ab1ad70ac360f441d819703f943f. The t151 adjudication rule (tail-md5
  match + moved mtime == a touch, not a sitting) is now measured-reproducible,
  not just recorded.
- B3: journal row 73 sha 6ff9ded == HEAD. Prompt pair prompt-74 vs prompt-73
  (58/58) digit-stripped delta 0.
- Cited sites re-read from source: r1_idle_probe.py:335-341 numeric _num sort;
  r1_playcap_watch.py:161 lowercase `glob.glob(.../save/*.sav)`;
  r1_slot.py:49 `.anch-cache.json` in anchors_cached(). All still correct.
- Bank hygiene: `grep -rln stop-report scripts/` -> only r1_idle_probe.py +
  its .pyc; stop-report.md 1514 lines, zero diff vs HEAD before appending.

## THE FINDING — sitting adjudication read the WRONG capture dir silently
Trigger (A)'s re-arm instruction says: on a new capture, "run
scripts/r1_t85g_sitting.py-style adjudication on the new turn-boundary
sitting". The tool that instruction names had a pinned constant:

    scripts/r1_t85g_sitting.py:18  RUN = ".../work/r1/playcap"

There are TWO capture harnesses and they do NOT share an evidence dir
[verified from source]:

| harness | OUT dir | watcher target |
| r1_playcap_vnc.sh (t85b, resumable) | work/r1/playcap (ACCUMULATES) | $OUT/live-timeline.jsonl |
| r1_playcap.sh (t82, one-shot, the one STATE/(A) and stop-report §4 tell the USER to run) | work/r1/playcap-<ts>/ (per-run) | $OUT/live-timeline.jsonl (per-run) |

r1_playcap.sh:78 launches `r1_playcap_watch.py "$OUT"` — the PER-RUN dir — so
a playcap.sh sitting writes a timeline the adjudicator never opens. Confirmed
on disk: 5 playcap-* dirs, 4 of them holding their own live-timeline.jsonl
(4.8 KB .. 284 KB) alongside the 5.7 GB shared one; `find work/r1 -name
live-timeline.jsonl` lists all 5.

Hazard, proven by REAL EXECUTION (this iteration):
    $ python3 scripts/r1_t85g_sitting.py work/r1/playcap-20261014-224611
      trusted turn-change rows: 0 (from work/r1/playcap-20261014-224611)
    $ python3 scripts/r1_t85g_sitting.py            # legacy, no argv
      trusted turn-change rows: 45050 (from .../work/r1/playcap)
The per-run dir holds 65 rows, ALL turn=0 (t82 title-slot law -> untrusted),
i.e. it is an idle boot. The legacy default replays the OLD shared
t1253/1254 sitting and prints relation snapshots, ship events and damage
deltas for a game the user did not play — with zero error and zero
indication of which dir it read. Same failure family as the 0x88 pointer-law
trap: silently-wrong input, plausible output.

Fix (scripts/r1_t85g_sitting.py): RUN = sys.argv[1] if given else the shared
dir (back-compat for t85g's own re-runs), plus the dir echoed in the header
line so any future reading names its source. py_compile clean; both branches
executed above.

Trigger (A) itself is NOT blind to a playcap.sh capture: a new per-run dir is
exactly what the dir leg compares (`newest != "playcap-20261014-224611"` at
r1_idle_probe.py:74 — lexicographic sort of timestamped names == newest
first, and any new timestamp differs from the literal, so it arms). The defect
was downstream of the trigger, in the instruction the NEXT ACTION hands to the
next session.

Lesson generalising t145: auditing whether a tool READS its input is not
enough — when a procedure names a tool AND an object ("run X on the new
capture"), check that the tool can address THAT object. A pinned default that
happens to be the right object for the last 30 turns is not evidence it is
right for the next one.

## Ledger
NO row closed (strict-close honest negative — probe hygiene + tool repair, no
new game-behaviour measurement). Open: OQ-003, OQ-005, OQ-016, OQ-019,
OQ-021, OQ-023. No banked law falsified.
