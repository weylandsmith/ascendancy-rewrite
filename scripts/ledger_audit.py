#!/usr/bin/env python3
r"""ledger_audit.py — t84 contract-compliance check on docs/OPEN-QUESTIONS.md.

Contract leg test per CLOSED row (whitespace-joined body):
  evidence  : names at least one address/offset/measurement token
  code-site : names a rewrite/ site, or an explicit no-change disposition
              (unchanged / documented default / W-B / fresh-start /
              BLOCKED-USER-LEVEL)
OPEN rows must equal the triaged open set passed via --expect (default:
the 2026-10-13 re-triage; the t82 default was computed WITH the old buggy
classifier and missed OQ-016/OQ-020). Status classification (t85 fix): the
FIRST pipe-wrapped cell starting CLOSED/open/BLOCKED decides the row (the
v1 regex `|\s*open\s*\|` missed `| open (sub-laws CLOSED...` and
`| BLOCKED ... |` rows, and a row is never silently-closed: no status cell
= error). BLOCKED rows count as OPEN (strict-close policy: "Item STAYS
OPEN"). Ledger rows are lines starting ^OQ-<digits>; the closed-index block
uses "- > OQ-" so this tool ignores it (ledger prose must also not WRAP so
that a continuation line starts with "OQ-" — t85 reflow note).
Exit 0 = all legs present and open set matches; 1 = report printed.
"""
import argparse, re, sys

# t158 (strict-close): the evidence leg requires at least one SPECIFIC,
# re-checkable handle. The t84 regex also accepted generic words
# (\bmeasured\b, \bverified\b, law\b, slots?\b, .sav/.gam/.cob/.dip ...), so a
# row closed with "verified by measurement, the law holds" and NO address,
# offset, run dir or test name printed LEDGER AUDIT OK — a prose default grading
# itself as cited, exactly what GOAL.txt forbids. Measured over the 12 real
# closed rows: every one carries >=1 handle below, so tightening adds zero false
# positives (counts in docs/re/stop-report.md §51). NOTE the old regex had no
# FUN_/DAT_ alternative at all, so Ghidra-style citations did not match it.
EVIDENCE_GENERIC = re.compile(
    r"0x[0-9a-fA-F]{3,}|\bmeasured\b|\bverified\b|md5|pointer law|"
    r"live[- ]RAM|\.dip\b|\.gam\b|\.sav\b|\.cob\b|windows\.txt|planitem|"
    r"slots?\b|law\b", re.I)
EVIDENCE = re.compile(
    r"0x[0-9a-fA-F]{3,}"            # Ghidra address / guest-physical address
    r"|FUN_[0-9a-fA-F]{4,}"         # decompiled function name
    r"|DAT_[0-9a-fA-F]{4,}"         # decompiled data symbol
    r"|\bmd5\b"                     # pinned digest
    r"|\br1[a-z0-9]*-\d{6}"         # capture run dir (a reproducible sitting)
    r"|\b\d{1,6}/\d{1,6}\b"         # measured N-of-M reproduction count
    r"|scripts/[A-Za-z0-9_\-]+\.py" # the probe that made the measurement
    r"|docs/re/[a-z0-9_\-]+\.md",   # the banked section holding the law
    re.I)
SITE = re.compile(
    r"rewrite\b|\bunchanged\b|no code change|documented default|"
    r"fresh-start|W-B|not modelled|BLOCKED-USER-LEVEL", re.I)
CELL = re.compile(r"\|\s*([A-Za-z][^|\n]*)")


def status_of(body):
    for m in CELL.finditer(body):
        c = m.group(1).strip()
        if re.match(r"CLOSED\b", c):
            return "CLOSED"
        if re.match(r"open\b", c):
            return "OPEN"
        if re.match(r"BLOCKED\b", c):
            return "BLOCKED"
    return None


def rows(path):
    """Ledger rows: lines starting ^OQ-<digits>; continuation lines are
    indented or non-OQ text. t85: a continuation line that WRAPS to start
    with 'OQ-' (e.g. prose '... ->\\nOQ-023 (not an RE unknown).') is not a
    row — require a pipe within the line's first 60 chars to count."""
    out, cur, buf = [], None, []
    for l in open(path, encoding="utf-8"):
        m = re.match(r"^OQ-(\d+)\b", l)
        if m and "|" in l[:60]:
            if cur:
                out.append((cur, " ".join(buf)))
            cur, buf = m.group(0), [l]
        elif cur:
            buf.append(l)
    if cur:
        out.append((cur, " ".join(buf)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", default="docs/OPEN-QUESTIONS.md")
    ap.add_argument("--expect", default="OQ-019,OQ-016")
    # t367: OQ-005 CLOSED by the D1 USER RULING (ruling page 2026-11-09 12:45,
    # DECISIONS.md verbatim block; shp.md S28; corner-anchor fallback + pin
    # TEST(shp_corner_anchor_fallback_t367)) — removed from this default the
    # same way t292/t195/t181 removed their closed rows.
    # t292: OQ-021 CLOSED by the live presenter witness (sel 0->5 by 0x24d9f,
    # rank 0x24dab, end-ctrl.txt on screen; score.md S20, run
    # work/r1/t290-poke-a40-20261103-165405) — removed from this default the
    # same way t195/t189b/t181 removed their closed rows.
    # t195: OQ-026 CLOSED by the rewrite visibility layer + pin
    # (campaign_visibility_law_oq026_t195; ships.md S23 L10) — removed from
    # this default the same way t189b/t181 removed their closed rows.
    # t193: OQ-026 (visibility layer / rec+0x20+star+0x16 consumer) OPENED by
    # the mid-game share-path witnesses (ships.md S23 L7/L8) — added to this
    # default the same way t181/t189b re-triaged rows.
    # t189b re-triage: OQ-023 CLOSED by the observed state-3 event
    # (cell0i=celli0=3 @t1335, +10/+10, arbiter scripts/r1_t188_state3_arbiter.py
    # RC=0 re-run; docs/re/diplomacy.md §13+§16) — removed from this default the
    # same way t181 removed OQ-003. The row's engine-build residual (trade/
    # third-party emitter) is tracked in docs/PLAN.md A7, not the RE ledger.
    # t181 re-triage: OQ-003 CLOSED by measured three-class disclaim
    # (scripts/r1_t181_banddiff.py; docs/re/savegame.md §t181) — removed from
    # this default so gate stage 3t (which calls with NO --expect) stays
    # meaningful: the default IS the triaged open set, per the docstring.
    a = ap.parse_args()
    # t159: drop empty tokens. "".split(",") == [""], so `--expect ''` — the
    # ONLY way to express the completion state (zero open rows) — compared the
    # empty open set against {""} and printed OPEN-SET MISMATCH RC=1 forever.
    # With every row closed, gate stage 3t (which calls this with the DEFAULT)
    # or an explicit --expect '' could never exit green, making GOAL.txt's own
    # completion condition (gate 0 AND no open rows) unreachable by
    # construction. Measured on fixture /tmp/t159-f6.md (all 18 rows CLOSED):
    # pre-patch --expect '' => RC=1 MISMATCH; post-patch => RC=0; the real
    # ledger with the real default is byte-identical OK either way.
    want = {x.strip() for x in a.expect.split(",") if x.strip()}
    R = rows(a.ledger)
    st = {oid: status_of(b) for oid, b in R}
    nost = [oid for oid, s in st.items() if s is None]
    openl = [oid for oid, s in st.items() if s in ("OPEN", "BLOCKED")]
    closed = [(oid, b) for oid, b in R if st[oid] == "CLOSED"]
    bad = []
    for oid, b in closed:
        if not EVIDENCE.search(b):
            bad.append((oid, "evidence"))
        elif not SITE.search(b):
            bad.append((oid, "code-site"))
    ok = set(openl) == want and not bad and not nost
    print(f"rows={len(R)} open={sorted(openl)} closed={len(closed)}")
    if nost:
        print(f"NO STATUS CELL (row neither open nor closed — strict-close "
              f"violation): {sorted(nost)}")
    if set(openl) != want:
        print(f"OPEN-SET MISMATCH vs expected {sorted(want)}")
    for oid, leg in bad:
        print(f"MISSING {leg}: {oid}")
    print("LEDGER AUDIT OK" if ok else "LEDGER AUDIT FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
