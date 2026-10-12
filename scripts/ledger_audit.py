#!/usr/bin/env python3
"""ledger_audit.py — t84 contract-compliance check on docs/OPEN-QUESTIONS.md.

Contract leg test per CLOSED row (whitespace-joined body):
  evidence  : names at least one address/offset/measurement token
  code-site : names a rewrite/ site, or an explicit no-change disposition
              (unchanged / documented default / W-B / fresh-start /
              BLOCKED-USER-LEVEL)
OPEN rows must equal the triaged open set passed via --expect (default:
the 2026-10-12 triage). Ledger rows are lines starting ^OQ-<digits>; the
closed-index block uses "- > OQ-" so this tool ignores it.
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


def rows(path):
    out, cur, buf = [], None, []
    for l in open(path, encoding="utf-8"):
        m = re.match(r"^OQ-(\d+)", l)
        if m:
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
    ap.add_argument("--expect", default="OQ-010,OQ-003,OQ-021,OQ-023,OQ-005,OQ-019")
    a = ap.parse_args()
    want = {x.strip() for x in a.expect.split(",")}
    R = rows(a.ledger)
    openl = [oid for oid, b in R if re.search(r"\|\s*open\s*\|", b)]
    closed = [(oid, b) for oid, b in R if oid not in openl]
    bad = []
    for oid, b in closed:
        if not EVIDENCE.search(b):
            bad.append((oid, "evidence"))
        elif not SITE.search(b):
            bad.append((oid, "code-site"))
    ok = set(openl) == want and not bad
    print(f"rows={len(R)} open={sorted(openl)} closed={len(closed)}")
    if set(openl) != want:
        print(f"OPEN-SET MISMATCH vs expected {sorted(want)}")
    for oid, leg in bad:
        print(f"MISSING {leg}: {oid}")
    print("LEDGER AUDIT OK" if ok else "LEDGER AUDIT FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
