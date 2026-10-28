# t158 WIP — IDLE re-check #45 + wire the ledger checkers into the enforcement path

## Trigger readings (session start 04:17:08, probe RC=0)
(A) NEGATIVE: newest playcap dir playcap-20261014-224611; live-timeline.jsonl
mtime_ns 1793043841304000000 / 5691796463 B (independently re-statted via
stat -c, equal to BASE); (A6) head 42a0bed0507f9052e2009ec94e9c27f1 /
tail 1529ab1ad70ac360f441d819703f943f reproduced a SEVENTH time, last row still
t1254; zero dosbox procs; find sweep non-loop none; A4 watcher ALIVE pid 27774;
A5 none (save/*.sav = 20).
(B) NEGATIVE: clean tracked tree at ec8a5ee; no STEERING; B3 HEAD == journal sha
ec8a5ee (journal row 79, last tab field); prompt-80 vs prompt-79 (58/58)
digit-stripped delta 0.
ledger_index_check at session start: LEDGER INDEX OK (open =
OQ-003/005/016/019/021/023, closed 12 record rows).

## FINDING H1 — the t157 checker is itself prose-enforced
t157's generalised law: "a documented invariant between TWO files is enforced by
nobody who only reads one of them — ship a checker and point the prose AT the
checker." t157 shipped the checker but pointed the prose at a HUMAN RUNNING IT.
Measured (grep -c ledger_index_check): gate.sh 0, loop_one_task.sh 0. The only
automatic post-flight checks are gate.sh + ledger_audit.py
(loop_one_task.sh:119-124). So if a future session edits STATE.md's index block
and never runs the tool, nothing goes red — the exact drift shape t157 measured
returns within one careless turn. Loop is alive (pids 78558/78559/78561), so
this post-flight path is the live enforcement surface.
FIX: add stage 3t to gate.sh running ledger_index_check.py; the loop's
post-flight gate.sh call then arms it automatically, and so does every manual
`bash scripts/gate.sh` (incl. this loop's finish sequence). Cheap: 0.1 s.

## FINDING H2 — the strict-close auditor accepts prose as evidence
ledger_audit.py's EVIDENCE regex matches generic WORDS as a passing leg:
\bmeasured\b, \bverified\b, law\b, slots?\b, .sav/.gam/.cob/.dip, windows.txt.
A row closed with the sentence "verified by measurement, the law holds" and ZERO
re-checkable handle passes "LEDGER AUDIT OK" — while GOAL.txt's verification
clause says a plausible default never closes a row and closure must NAME its
evidence (address / offset / live-RAM measurement). Also the regex's address
alternative is `0x[0-9a-f]{3,}` only, so Ghidra-style FUN_00044a44 / DAT_00013bc5
do NOT match it at all.
MEASURED (imported classifier over the 12 real closed rows, per-handle counts):
all 12 carry at least one SPECIFIC handle (0x-address, FUN_/DAT_, md5, capture
run dir r1xxx-NNNNNN, N/M count, scripts/*.py, docs/re/*.md section, pin test
name), so tightening costs zero false positives on real closures:
  OQ-010 82 hex | OQ-022 13 | OQ-024 5 | OQ-020 9 | OQ-006 7 | OQ-013 7 |
  OQ-014 4 | OQ-018 5 | OQ-004 1 hex + md5 | OQ-025 0 hex but 1 rundir + 15
  ratios + toolpath + docsec | OQ-012 0 hex but 2 rundirs + 2 ratios +
  toolpath + docsec | OQ-015 0 hex but 2 FUN_ + 5 ratios + docsec.
FIX: require >=1 specific handle; generic words no longer close the leg.
Validate by REAL execution: HEAD's record passes unchanged (no retroactive red)
+ a prose-only fixture row FAILS naming the row + a no-handle fixture fails.

## Not touched
No ledger row closed (no new measurement this iteration — strict-close honest
negative). game/ untouched. No watch/census run against the live capture.
