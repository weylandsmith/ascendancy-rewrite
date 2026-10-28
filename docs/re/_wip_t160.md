# t160 WIP — IDLE re-check #47 (in progress)

Session start 2026-10-28 ~05:00 (probe ran 05:01:53). HEAD at start = 87b41a4
(t159). Clean tracked tree at session start => verdict wording valid per t155/B5.

## TRIGGER (A) — NEGATIVE (probe RC=0, 05:01:53)
- newest playcap dir: playcap-20261014-224611
- live-timeline.jsonl mtime_ns=1793043841304000000 size=5691796463 ==
  BASE_MTIME_NS/BASE_SIZE (50th consecutive byte-identical reading t111..t160);
  independently re-statted outside the probe (`stat -c` size 5691796463).
- (A6) content baseline reproduced a NINTH time: head 64 KiB md5
  42a0bed0507f9052e2009ec94e9c27f1 / tail 64 KiB md5
  1529ab1ad70ac360f441d819703f943f; last row still
  {"file":"60.sav","turn":1254,"T":50,"score_stars":14,...}
- dosbox procs: none. find work/r1 -newermt <session start> -> 4 files, non-loop
  none. A4 watcher ALIVE pid 27774. A5 none (save/*.sav = 20, all match glob).
- r1_t85g_sitting.py correctly NOT run (t152 law: only on an armed (A)).

## TRIGGER (B) — NEGATIVE
- git diff HEAD --name-only empty; status --porcelain (tracked) empty;
  untracked loop-owned none; untracked outside loop-owned none; delta outside
  loop-owned none.
- STEERING file: none.
- B3: HEAD == journal sha 87b41a4 (journal row 81, ct 2026-10-28 04:59:16,
  re-read independently outside the probe) => no commits outside the loop.
- prompt pair prompt-82.txt vs prompt-81.txt (58/58 lines) digit-stripped
  delta 0.
- §3 answers outstanding after forty-seven idle turns; t113 LOOP-END PROPOSAL
  stands.

## LEDGER (touched: index audited, no row changed)
- ledger_index_check.py: LEDGER INDEX OK — record rows=18
  open=[OQ-003,OQ-005,OQ-016,OQ-019,OQ-021,OQ-023] closed=12; STATE index
  open identical.
- ledger_audit.py: LEDGER AUDIT OK (same sets).

## IN PROGRESS
t145-family audit of the one hand-maintained exemption list left in the ledger
checks: ledger_index_check.py:38 `V1_IDS = {OQ-001,002,007,008,009,011,017}` —
ids exempted from BOTH "absent from record" legs because ledger_audit skips the
record's "- > OQ-" v1 block by design. Question: is that blessing derived from
the record's v1 block, or does it hide a decision made inside the skipped
region? (Same shape as t159's hand-maintained --expect duplicate.)
