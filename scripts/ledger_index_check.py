#!/usr/bin/env python3
r"""ledger_index_check.py — t157: diff STATE.md's fast ledger index against the
authoritative record (docs/OPEN-QUESTIONS.md), using ledger_audit's OWN status
classifier so the two checks can never disagree by parser.

Why (t157 measurement): STATE.md declares "statuses mirror OPEN-QUESTIONS.md,
update BOTH or neither", yet hand-mirroring had drifted 6 rows (OQ-006/012/
015/020/025 listed open while CLOSED in the record; OQ-023 open but MISSING
from the index). Nothing caught it: gate.sh never runs ledger_audit.py, and
ledger_audit.py checks the record only against its hard-coded --expect list —
it cannot see STATE.md (its docstring describes a "- > OQ-" index format STATE
never used). A fresh session resuming from STATE.md ALONE got a 10-row menu
with 5 stale rows and one missing row.

Legs:
  1. parse the record -> authoritative open/closed sets (ledger_audit.rows +
     status_of; BLOCKED counts open per strict-close policy).
  2. parse STATE.md's `ledger:` block (two-space `closed:`/`open:` keys,
     four-space `- "OQ-NNN` entries; continuation lines are indented).
  3. DIVERGENCE = record-open rows missing from the index open list; index-open
     rows the record calls CLOSED; index entries for ids absent from the record
     entirely (v1 ids OQ-001..011/017 are exempt: they close in the record's
     "- > OQ-" index block which ledger_audit ignores BY DESIGN).
Exit 0 = index consistent; 1 = divergence listed (never silent).
Env R1_STATE / R1_LEDGER override paths for fixtures.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ledger_audit as la  # noqa: E402  (same parser on purpose)

STATE = os.environ.get("R1_STATE", "docs/STATE.md")
LEDGER = os.environ.get("R1_LEDGER", "docs/OPEN-QUESTIONS.md")
# ids the record closes in its "- > OQ-" v1 block (ledger_audit skips those
# rows by design), so their absence from rows() is not a divergence.
# t160: this literal was a hand-maintained DUPLICATE of the record's v1 block
# (fourth instance of the family: t157 index, t158 grader regex, t159
# --expect, t160 exemption set) and was never compared to anything, so BOTH
# drift directions were bad: the block gaining/losing an id silently re-scoped
# which ids escape every cross-check (deleted block => 7 v1 closures vanish from
# grader AND index while both print OK), while the literal going stale armed
# false DIVERGENCE on a legitimate edit. Now DERIVED from the record each run
# and RECONCILED against V1_IDS_EXPECTED below, so the duplicate became the
# leg: block-vs-code disagreement fails loudly in both directions.
V1_IDS_EXPECTED = {"OQ-001", "OQ-002", "OQ-007", "OQ-008", "OQ-009",
                   "OQ-011", "OQ-017"}


def v1_block_ids(path):
    """Ids closed in the record's '- > OQ-' index block (the region
    ledger_audit.rows() skips). t84 contract shapes these lines; grep-verified
    the ONLY 7 lines matching '^- > ' in the real record are '^- > OQ-' ones,
    so no non-id line can pollute the set."""
    ids = set()
    for l in open(path, encoding="utf-8"):
        m = re.match(r"^- > (OQ-\d+)\b", l)
        if m:
            ids.add(m.group(1))
    return ids


def state_index(path):
    """Return (open_ids, closed_ids) from STATE.md's ledger: block."""
    keys = {"closed": [], "open": []}
    cur = None
    in_block = False
    for l in open(path, encoding="utf-8"):
        if l.startswith("ledger:"):
            in_block = True
            continue
        if in_block and l.startswith("## "):
            break
        if not in_block:
            continue
        m = re.match(r"^  (closed|open):\s*$", l)
        if m:
            cur = m.group(1)
            continue
        if cur:
            m = re.match(r'^    - "(OQ-\d+)', l)
            if m:
                keys[cur].append(m.group(1))
    return set(keys["open"]), set(keys["closed"])


def main():
    R = la.rows(LEDGER)
    st = {oid: la.status_of(b) for oid, b in R}
    rec_open = {o for o, s in st.items() if s in ("OPEN", "BLOCKED")}
    rec_closed = {o for o, s in st.items() if s == "CLOSED"}
    nost = sorted(o for o, s in st.items() if s is None)
    idx_open, idx_closed = state_index(STATE)
    V1_IDS = v1_block_ids(LEDGER)

    problems = []
    # t160 reconciliation leg: the record's v1 block IS the source of truth for
    # which ids legitimately escape rows(); the code literal is the pin that
    # notices the block being edited away. Disagreement fails in BOTH
    # directions — a deleted block (7 closures silently ungraded) and an
    # added/renamed id (a v2 row wrongly exempted from every cross-check) each
    # print the exact delta.
    if V1_IDS != V1_IDS_EXPECTED:
        problems.append(
            "v1 BLOCK vs code literal drift: block_only="
            f"{sorted(V1_IDS - V1_IDS_EXPECTED)} literal_only="
            f"{sorted(V1_IDS_EXPECTED - V1_IDS)} — reconcile the record's "
            "'- > OQ-' block and V1_IDS_EXPECTED (the block is the contract; "
            "update the literal ONLY to match a real record edit)")
    for o in sorted(rec_open - idx_open):
        problems.append(f"record-OPEN {o} missing from STATE open list")
    for o in sorted(idx_open - rec_open):
        if o in rec_closed:
            problems.append(f"STATE lists {o} open; record says CLOSED")
        elif o not in V1_IDS:
            problems.append(f"STATE lists {o} open; id absent from record")
    for o in sorted(idx_closed - rec_closed - V1_IDS):
        if o not in rec_open:
            problems.append(f"STATE lists {o} closed; id absent from record")
        else:
            problems.append(f"STATE lists {o} closed; record says OPEN")
    for o in sorted(idx_open & idx_closed):
        problems.append(f"{o} listed in BOTH index lists")

    print(f"record rows={len(R)} open={sorted(rec_open)} closed={len(rec_closed)}"
          + (f" NO-STATUS={nost}" if nost else ""))
    print(f"STATE index open={sorted(idx_open)}")
    print(f"closed={sorted(idx_closed)}")
    if nost:
        print("LEDGER INDEX FAILED (record row without a status cell)")
        return 1
    for p in problems:
        print("DIVERGENCE:", p)
    print("LEDGER INDEX OK" if not problems else "LEDGER INDEX FAILED")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
