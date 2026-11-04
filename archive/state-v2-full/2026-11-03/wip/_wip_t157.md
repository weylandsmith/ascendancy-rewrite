# t157 WIP — IDLE re-check #44 (2026-10-28 03:55 EDT)

## Trigger adjudication (tool + hand, both negative)
`python3 scripts/r1_idle_probe.py` RC=0 at 03:55:39 (cutoff 03:53:57),
verdict line "IDLE — neither trigger" — valid per t155/B5 because the tree was
CLEAN at session start (HEAD 1f62e45, `git status --porcelain` empty).
(A): newest playcap dir playcap-20261014-224611; live-timeline.jsonl
mtime_ns 1793043841304000000 / 5691796463 B (47th consecutive byte-identical
reading t111..t157) — re-statted independently with `stat -c '%Y %s'`, equal to
BASE_MTIME_NS/BASE_SIZE (r1_idle_probe.py:78-79); t156 (A6) content baseline
reproduced a SIXTH time head 42a0bed0507f9052e2009ec94e9c27f1 / tail
1529ab1ad70ac360f441d819703f943f, last row still {"file":"60.sav","turn":1254};
zero dosbox procs; find sweep 4 files, non-loop none; A4 watcher ALIVE pid
27774; A5 none (save/*.sav = 20, all match the watcher glob).
(B): no STEERING file; B3 HEAD == journal sha 1f62e45 (journal.tsv last tab
field re-read independently, not only via the probe); prompt pair prompt-79 vs
prompt-78 (58/58 lines) digit-stripped delta 0.

## THE FINDING — control-plane hole: STATE.md's LEDGER index had drifted 6 rows
STATE.md:12-13 declares the ledger block "statuses mirror
docs/OPEN-QUESTIONS.md ... Update BOTH or neither." Measured divergence with
ledger_audit.py's OWN classifier (imported, not eyeballed), rows=18:

  authoritative record (OPEN-QUESTIONS.md, the closing-evidence file):
    OPEN  = OQ-003 OQ-005 OQ-016 OQ-019 OQ-021 OQ-023   (closed = 12)
  STATE.md fast index:
    open  = OQ-003 OQ-021 OQ-020 OQ-005 OQ-006 OQ-012 OQ-025 OQ-015 OQ-016 OQ-019
    closed= OQ-001 OQ-002 OQ-007 OQ-008 OQ-009 OQ-011 OQ-017 OQ-013 OQ-014 OQ-004
            OQ-018 OQ-010

  6 divergences:
   - OQ-020 listed open; record CLOSED t100 (STATE's own 2nd-level text even
     says "CLOSED t100" inside the open entry)
   - OQ-006 listed open; record CLOSED 2026-10-07 (device rate 22050 MEASURED,
     chain 0x5622 -> 0x68816 -> 0x68882 -> setter 0x6e000, OPEN-QUESTIONS.md:381-388)
   - OQ-012 listed open; record CLOSED t78
   - OQ-025 listed open; record CLOSED t79
   - OQ-015 listed open; record CLOSED 2026-10-08 (OPEN-QUESTIONS.md:475-488)
   - OQ-023 MISSING entirely; record OPEN (relation-state ENUM semantics,
     OPEN-QUESTIONS.md:264+)

  Mechanism of the drift: the open entries are the historical *scope-narrowing*
  narratives (OQ-012 "(a)...(d)", OQ-015 "DA_ template selection order", etc).
  Each sub-leg closure was recorded INLINE in the entry text, but no turn ever
  moved the entry to `closed:` — so a leg closing silently demoted the row's
  index status by omission. Nothing detects it:
   - scripts/gate.sh never calls ledger_audit.py (grep: no match) — verified;
   - scripts/loop_one_task.sh:122 DOES run it post-flight, and post_audit.log
     has been OK for every idle iteration, but the audit only compares
     OPEN-QUESTIONS.md against its own hard-coded --expect set. It cannot see
     STATE.md: its docstring says the STATE closed-index uses "- > OQ-" and is
     therefore ignored (ledger_audit.py:16-18) — and in fact STATE.md's block
     uses `- "OQ-...` bullets, so the docstring's description of the fast index
     is itself stale. The two files are checked against a THIRD fixed list.
   Consequence: a fresh session that follows the header comment ("resume from
   THIS file alone") reads 10 open rows, 5 of them already closed, and misses
   the one genuinely open row it might otherwise act on (OQ-023). Every idle
   turn since the drift inherited that false menu; the loop never acted on it
   because idle turns don't pick tasks from the index.

## Repair enacted (this iteration)
Re-derived the index from the record with the audit's classifier; rewrote the
open list to the true 6 rows (pointing at evidence in the record rather than
carrying stale narrative), kept v1 ids in `closed:` (they are the v1 rows the
record holds in its "- > OQ-" index block, OPEN-QUESTIONS.md:931-937), and
added OQ-006/012/015/020/025 to closed: with their record-cited closures.
Header comment now states the derivation command so the next turn can re-derive
instead of hand-maintaining.

## Honest negatives
NO ledger row closed this iteration (strict-close: no cited measurement of a
field law was taken; the repair is bookkeeping, and the *audit* of bookkeeping
is what it measured). OQ-023 stays open — RE residual (relation-enum semantics)
needs an interactive original session with an injected transition; the rewrite
engine build behind it is build work, not measurement. No law falsified.
game/ untouched; no capture, watch, or census run against the live corpus.
