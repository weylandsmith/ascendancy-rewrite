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

EVIDENCE = re.compile(
    r"0x[0-9a-fA-F]{3,}|\bmeasured\b|\bverified\b|md5|pointer law|"
    r"live[- ]RAM|\.dip\b|\.gam\b|\.sav\b|\.cob\b|windows\.txt|planitem|"
    r"slots?\b|law\b", re.I)
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
    ap.add_argument("--expect", default="OQ-003,OQ-021,OQ-023,"
                                        "OQ-005,OQ-019,OQ-016")
    a = ap.parse_args()
    want = {x.strip() for x in a.expect.split(",")}
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
