# _wip_t223 — TRIGGER-ARMED IDLE adjudication (tenth consecutive)

Hand-authored. Verified nothing regenerates this path: scripts/r1_idle_probe.py
only READS docs/re/_wip_*.md (t221 check, still true — no generator writes here).
Per the t222 assignment: ~4-call cap, no new code path, no fd census, no static
hunt (corpus formally EXHAUSTED at t213 S7), no re-print of the same negative as
a "finding". Nothing below is new content; it is a reproduction plus one age
recomputation.

## S1 — Axis 1: TRIGGER-A baselines unchanged (tenth iteration)

`python3 scripts/r214_triage.py` RC=0 at 2026-10-30T23:34:20Z:

  ns_mtime 1793294532100000000 == 1793294532100000000: True
  size     5721578066 == 5721578066: True
  tail md5 9054cc6c66802e6f80431d4ffa1416ee == 9054cc6c66802e6f80431d4ffa1416ee: True
  => sitting delta: False

Zero dosbox/ascend.exe processes, so nothing is mid-capture either. Tail intact:
400 rows / 0 bad json / turn 1086 / 275 distinct / exactly one key shape
(n=400: T,T_known,file,file_mtime_ns,in_game,planets_mine,rank,relation,
score_stars,selector_byte,ship_raw,ships,systems_any,systems_full,turn,wall).
`scripts/r1_t85g_sitting.py` correctly NOT run (t152 trap: it must only run on a
NAMED sitting dir, never speculatively).

Baseline age RECOMPUTED, not carried forward: baseline ns
== 2026-10-29T17:22:12.100Z; session clock 2026-10-30T23:34:45Z ⇒ 30.21 h.
Monotone against t222's 30.06 h at 23:25:39Z (delta 0.15 h ≈ the 9.1 min wall
gap), so the age chain in STATE.md remains self-corroborating.

Watcher census (same script, shared-dir block): pid 27772 [bash] ppid 1, child
27774 [python3] ppid 27772, plus orphans 260988 / 290953 / 292085 — identical to
t215..t222. No new orphans, no retirements. Nothing killed (supervised-session
decision; user ask #3 stands).

## S2 — Axis 2: save axis bit-identical

  find /home/hrethric -xdev \( -name '*.sav' -o -name '*.gam' \) -printf '%T@ %p\n' | sort -rn | head

  1793294530.1080000000 .../work/r1/playcap/save/41.sav
  1793294520.0400000000 .../work/r1/playcap/save/60.sav
  1793294510.0040000000 .../work/r1/playcap/save/59.sav
  1793294500.0040000000 .../work/r1/playcap/save/58.sav
  COUNT=1409

Byte-identical to t216..t222: population 1409, newest named by ns (41.sav, NOT
60.sav — t216 precision fix). Newest save is still OLDER than the timeline
baseline (1793294530.108 < 1793294532.1), so the "watchers died and hid a
sitting" failure mode remains closed. Gap re-measured 1.992 s — fifth
consecutive iteration. Zero saves since the 2026-10-29 13:22 end series.

## S3 — Ledger premise NOT re-audited out of band (deliberate)

With no sitting, the open set cannot have moved (t219 S3 measured
rows=19 open=['OQ-005','OQ-016','OQ-019','OQ-021'] closed=15; t221/t222 each
inferred the idle result without re-auditing). Re-running ledger_audit as a
research action would have been a fifth re-print of the same negative, so it was
run ONLY as a finish-sequence stage (below), as prescribed. No ledger row was
touched, no row was closed, nothing was appended to docs/OPEN-QUESTIONS.md —
strict-close honored (a plausible default never closes a row; here there was not
even a default to offer, since the witness classes are unobservable without a
sitting). OQ-005 / OQ-016 / OQ-019 / OQ-021 stay OPEN for the same cited reason
as at t222.

Gate stages run at finish: `bash scripts/gate.sh` and
`python3 scripts/ledger_audit.py` (see STATE.md LANDED t223 for exit codes).
