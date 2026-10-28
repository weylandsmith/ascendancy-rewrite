# t161 WIP — IDLE re-check #48

## Session-start trigger state (measured 2026-10-28 05:15:28, clean tree at b9cf937)
- Trigger (A) NEGATIVE — probe RC=0. Newest playcap dir playcap-20261014-224611;
  live-timeline.jsonl size 5691796463 / mtime 2026-10-26 15:44:01.304
  (mtime_ns 1793043841304000000 per the probe; NOTE: `stat -c %Y` returns SECONDS,
  so the hand re-stat must be `stat -c %y` + size, or python st_mtime_ns — t161
  measured `stat -c '%Y'` print 1793043841 (1e9 too small) which naively != the
  probe's nanosecond baseline. Harmless here (size + date string match) but it is
  the same class as the t147 near-miss: resolve the unit of the constant you are
  comparing against before calling it a divergence.).
- (A6) content baseline reproduced a TENTH time: hand-measured head 64 KiB md5
  42a0bed0507f9052e2009ec94e9c27f1 / tail 64 KiB md5
  1529ab1ad70ac360f441d819703f943f; last row still t1254 (systems_any 36,
  planets_mine 36, T_known 50, wall 15:44:01). 50th consecutive byte-identical
  reading t111..t161.
- A4 watcher ALIVE pid 27774; A5 none (save/*.sav = 20); zero dosbox procs;
  find sweep 4 files, non-loop: none.
- Trigger (B) NEGATIVE — clean tracked tree at b9cf937 at session start (verdict
  wording valid per t155/B5), no STEERING, B3 HEAD == journal sha b9cf937
  (journal row 82, ct 2026-10-28 05:12:48, OK, fail_streak 0), prompt pair
  prompt-83.txt vs prompt-82.txt (58/58 lines) digit-stripped delta 0.
- ledger_index_check.py: LEDGER INDEX OK; record rows=18
  open=[OQ-003,OQ-005,OQ-016,OQ-019,OQ-021,OQ-023] closed=12.
- Infra unchanged since t112 (Xvfb 1196 / x11vnc 1207 / watcher 27774;
  x11vnc.log 2026-10-27 17:30:18 / 30114 — zero connects).

## THE FINDING (measured 05:2x, before any edit) — a CLOSED row can vanish from
## STATE's index and `LEDGER INDEX OK` still prints. TWO real rows are missing RIGHT NOW.
Method: import the checker's own sets (ledger_audit.rows/status_of,
v1_block_ids, state_index) and ask which record ids no leg compares. Result on the
real pair of files:
  LEG A  rec_open - idx_open                          = []
  LEG B  idx_open - rec_open                          = []
  LEG C  idx_closed - rec_closed - V1_IDS             = []
  LEG D  idx_open & idx_closed                        = (empty, leg exists)
  UNCOVERED  rec_closed - idx_closed                  = ['OQ-022', 'OQ-024']  <-- LIVE DRIFT
Read the legs off ledger_index_check.py:111-124 — every leg is indexed on the
OPEN side or on entries the INDEX already has. The record having a CLOSED row the
index never mentions moves nothing. 19 closed ids exist in the record (12 main-table
rows + 7 v1-block ids); STATE lists 17.
Origin: not a new edit. `git log -S'OQ-022' -- docs/STATE.md` newest hit is t57c;
OQ-024 newest t44 — neither id has been TOUCHED in STATE's ledger block since t157
re-derived it. t157's repair re-derived the OPEN side (the side its own legs could
see) and hand-copied the closed list, dropping 2 rows. Same recursion as t158
finding t157's law unenforced: t161 finding t157's FIX incomplete. Third member of
the t159 family ("a grader that cannot represent a shape grades it as absent"):
t159 empty open set, t160 constant-vs-record drift, t161 missing closed row.
Hazard (why it matters even though the closed side is not a menu): GOAL.txt:2 +
STATE.md:12-13 declare the block mirrors the record, and a session that resumes
"from STATE.md ALONE" cannot learn OQ-022/OQ-024 EXIST — it cannot avoid re-filing
work already closed, and the t159 CLOSURE NOTE (empty open ledger) is graded off
the same block that silently loses ids.
SECOND UNCOVERED SHAPE (same class — the tools disagree about the ID SET, not the
status): `st = {oid: status_of(b) for oid,b in R}` (ledger_index_check.py:90 and
ledger_audit.py:100) — a duplicated id in the RECORD collapses silently and LAST
WINS. Measured: real record rows=18 distinct=18, zero duplicates, so no live harm;
the realistic duplicate (a wrap line like the real record's line 488
"OQ-023 (not an RE unknown).") is caught only because its status_of is None ->
NO-STATUS fires in both tools (loud, wrong message). Cheap deterministic leg.
FIX DECISION: hard DIVERGENCE, not CAUTION — t155/t156 law: a rule that reaches
only a buried line is unenacted, and here the invariant is stated in the file's own
header. Legs added to ledger_index_check.py: (E) record-CLOSED missing from STATE's
closed list (prints pasteable `- "OQ-NNN ..."` repair stub), (F) duplicate id in the
record. Real record must go GREEN after repairing STATE with the 2 rows.

## Probe target for this iteration (t160's law, fifth application)
t160 derived ledger_index_check's V1_IDS from the record and reconciled it against
a code pin. The reconciliation guards the ID SET. Un-audited shape: what the
skipped v1 block does to a row's STATUS and to DUPLICATES —
 (i) a row that legitimately lives in the main table appearing a SECOND time in
     the v1 block (duplicate id): which status wins for the index diff?
 (ii) an id inside the v1 block is exempt from both "absent from record" legs —
      so does a v1-block id that is genuinely OPEN anywhere get reported at all?
 Read source first (ledger_index_check.py, ledger_audit.py rows()/status_of),
 then measure on fixtures by real execution. No fixture survives the turn.
