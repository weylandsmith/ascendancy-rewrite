#!/usr/bin/env python3
"""r373_quote_audit.py — longest verbatim vendor span per docs/re/*.md (S9a).

Why: docs/re quotes vendor text files (gizmos.txt, help.txt, ...) as
measurement evidence. Short quotes are defensible fair use; a wholesale
paste is not, and would contradict the NOTICE claim ("quoted at lengths we
consider fair use"). This measures, per evidence doc, the longest run of
CONSECUTIVE lines that reproduces vendor text verbatim.

Corpus: every text-ish file under extracted/ (the vendor-derived tree),
decoded cp437 (OQ-007 CLOSED law). Lines are compared stripped, non-empty,
and >= 12 chars (shorter lines are table rows / menu fragments that occur in
prose by coincidence and inflate the metric with no signal — the threshold
is stated so the number is reproducible).

Output: one line per docs/re/*.md with >=1 match:
  <doc>\t<longest consecutive span, lines>\t<first line of that span, 60ch>
Exit 0 always (this is a census, not a gate stage). Threshold for "needs
eyeball" is reported via --warn N (default 25 lines).
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MINLEN = 12


def vendor_lines():
    lines = set()
    for dirpath, _, names in os.walk(os.path.join(ROOT, "extracted")):
        for n in names:
            if not n.lower().endswith((".txt", ".dip", ".gam")):
                continue
            p = os.path.join(dirpath, n)
            try:
                raw = open(p, "rb").read()
            except OSError:
                continue
            if len(raw) > 4_000_000:
                continue
            try:
                txt = raw.decode("cp437")
            except Exception:
                continue
            for ln in txt.replace("\r", "").split("\n"):
                s = ln.strip()
                if len(s) >= MINLEN:
                    lines.add(s)
    return lines


def longest_span(md_path, vset):
    try:
        txt = open(md_path, encoding="utf-8", errors="replace").read()
    except OSError:
        return 0, ""
    lines = [l.strip() for l in txt.split("\n")]
    best, best_i = 0, 0
    i = 0
    n = len(lines)
    while i < n:
        if lines[i] in vset and len(lines[i]) >= MINLEN:
            j = i
            while j + 1 < n and lines[j + 1] in vset and len(lines[j + 1]) >= MINLEN:
                j += 1
            if j - i + 1 > best:
                best, best_i = j - i + 1, i
            i = j + 1
        else:
            i += 1
    return best, (lines[best_i][:60] if best else "")


def main():
    warn = 25
    for a in sys.argv[1:]:
        if a.startswith("--warn"):
            warn = int(a.split("=")[1])
    vset = vendor_lines()
    print(f"# vendor corpus: {len(vset)} distinct lines >= {MINLEN} ch "
          f"(extracted/, cp437)")
    hits, worst = 0, 0
    for n in sorted(os.listdir(os.path.join(ROOT, "docs", "re"))):
        if not n.endswith(".md"):
            continue
        L, first = longest_span(os.path.join(ROOT, "docs", "re", n), vset)
        if L >= 1:
            hits += 1
            worst = max(worst, L)
            flag = "  **OVER-WARN**" if L > warn else ""
            print(f"{n}\t{L}\t{first}{flag}")
    print(f"# docs with vendor spans: {hits}; longest overall: {worst} lines "
          f"(warn threshold {warn})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
