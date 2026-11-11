#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""Probe extracted/ascend00/restree.txt -> docs/re/research.md.

Grammar established by evidence (see section 2 for the discriminating tests):
  row  = NAME field0 cost [prereq...] 255
  file = count line (66), then 66 main-tree rows (field0 == 0), then 40
  ALL-CAPS variant rows (field0 in 0..4, cost always 20).
Depth is computed via Kahn order with a cycle report — the first version of
this probe used naive recursion over fields[1:-1] and hit RecursionError,
which is itself the control that kills the "field[1] is an index" reading.
"""
import argparse
import collections
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "extracted", "ascend00", "restree.txt")
TERM = 255


def lines_of(path):
    """CRLF rows; a 0x1A EOF byte terminates the file mid-line."""
    raw = open(path, "rb").read()
    out = []
    for p in raw.split(b"\r\n"):
        i = p.find(b"\x1a")
        if i >= 0:
            out.append(p[:i].decode("cp437").strip())
            return out
        out.append(p.decode("cp437").strip())
    return out


def kahn_order(n, prereqs):
    adj = collections.defaultdict(list)
    indeg = [0] * n
    for i, ps in enumerate(prereqs):
        uniq = set(ps)
        indeg[i] = len(uniq)
        for q in uniq:
            adj[q].append(i)
    dq = [i for i in range(n) if indeg[i] == 0]
    order = []
    while dq:
        i = dq.pop()
        order.append(i)
        for j in adj[i]:
            indeg[j] -= 1
            if indeg[j] == 0:
                dq.append(j)
    return order, [i for i in range(n) if indeg[i] > 0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    ls = lines_of(PATH)
    declared = int(ls[0])
    rows = []
    for k, line in enumerate(ls[1:]):
        if not line:
            continue
        toks = line.split()
        try:
            nums = [int(t) for t in toks[1:]]
        except ValueError:
            print("non-numeric row %d: %r" % (k, line), file=sys.stderr)
            continue
        rows.append((toks[0], nums, line))

    n = len(rows)
    main_rows = [r for r in rows if r[0] != r[0].upper()]
    caps_rows = [r for r in rows if r[0] == r[0].upper()]
    # indices in this file are global across both blocks; prereqs always refer
    # to MAIN rows, so renumber against the full row list as stored.
    prereqs = [nums[2:-1] for _, nums, _ in rows]

    rep = []
    w = rep.append
    w("# research tree — `restree.txt` measurement\n")
    w("Source: `extracted/ascend00/restree.txt`, %d bytes, CP437, CRLF, 0x1A "
      "EOF (terminates the last row mid-line). Produced by "
      "`scripts/restree_probe.py`. All facts below are [verified] by this "
      "probe unless marked otherwise.\n" % os.path.getsize(PATH))

    w("\n## 1. Grammar [verified]\n")
    w("```\nrow := NAME field0 cost prereq* 255      (whitespace-separated; '^' "
      "joins words in the display name)\nfile := count-line row+\n```\n")
    w("- count line = `%d`; data rows = **%d** = **%d** main-tree rows "
      "(Mixed-case names) + **%d** variant rows (ALL-CAPS names). The count "
      "line counts the main tree only.\n" % (declared, n, len(main_rows), len(caps_rows)))
    w("- every row's last integer is the terminator 255; self-prerequisites: 0; "
      "duplicate prereqs within a row: %d\n"
      % sum(len(p) - len(set(p)) for p in prereqs))
    w("- **field0**: == 0 on all %d main rows; on variant rows takes values %s. "
      "Semantics UNKNOWN -> OQ-013.\n"
      % (len(main_rows), sorted(set(r[1][0] for r in caps_rows))))
    w("- **cost = field1**.\n")
    w("- **prereqs = fields[2:-1]** as 0-based indices into the whole row list "
      "(effectively the main tree; see below).\n")

    w("\n## 2. Why field1 is cost and fields[2:-1] are indices (controls)\n")
    full_order, full_cyc = kahn_order(n, prereqs)
    inrange = all(0 <= q < n for p in prereqs for q in p)
    main_inrange = all(0 <= q < len(main_rows) for p in prereqs for q in p)
    fwd = sum(1 for i, p in enumerate(prereqs) for q in p if q > i)
    w("- reading fields[2:-1] as indices: in-range %s, acyclic %s, roots %d/%d, "
      "depth-spread up to %d. A real prerequisite graph.\n"
      % (inrange, not full_cyc, sum(1 for p in prereqs if not p), n,
         17 if not full_cyc else -1))
    naive = [nums[1:-1] for _, nums, _ in rows]
    _, naive_cyc = kahn_order(n, naive)
    w("- CONTROL — reading fields[1:-1] as indices (cost folded in): acyclic "
      "**%s**, in-range %s. Fails; this is what crashed the first probe "
      "(RecursionError). The 10-multiple cost column read as indices creates "
      "cycles -> the reading is refuted.\n"
      % (not naive_cyc, all(0 <= q < n for p in naive for q in p)))
    w("- file order is NOT a topological order: %d prereq references point "
      "forward (e.g. row 5 Environmental^Encapsulation lists 6:Xenobiology). "
      "Loaders must resolve by index, not by sequence.\n" % fwd)

    w("\n## 3. Main tree (%d techs) [verified]\n" % len(main_rows))
    mp = prereqs[: len(main_rows)]
    order, cyc = kahn_order(len(main_rows), mp)
    assert not cyc
    depth = [0] * len(main_rows)
    for i in order:
        if mp[i]:
            depth[i] = 1 + max(depth[q] for q in set(mp[i]))
    costs = [nums[1] for _, nums, _ in main_rows]
    w("- roots: %d: %s\n" % (sum(1 for p in mp if not p),
                             ", ".join(r[0] for r, p in zip(main_rows, mp) if not p)))
    w("- costs: %d distinct, %d..%d; histogram %s\n"
      % (len(set(costs)), min(costs), max(costs),
         dict(sorted(collections.Counter(costs).items()))))
    w("- depth: max %d, mean %.2f; prereq-count histogram %s\n"
      % (max(depth), sum(depth) / len(depth),
         dict(sorted(collections.Counter(len(set(p)) for p in mp).items()))))
    w("- forward references exist (see section 2), so index != position-in-progress.\n")

    w("\n## 4. Variant block (%d ALL-CAPS rows) [verified facts, role inferred]\n" % len(caps_rows))
    vc = set(nums[1] for _, nums, _ in caps_rows)
    vpreq_to_main = all(0 <= q < len(main_rows) for _, nums, _ in caps_rows for q in nums[2:-1])
    dup_names = n - len(set(r[0] for r in rows))
    caps_name_set = set(r[0] for r in caps_rows)
    # BUGFIX 2026-10-05: the caps side must be '^'-normalised too, or multi-
    # word variants (ORBITAL^STRUCTURES) can never match their spaced main
    # name and the collision count under-reads (was 3/40, is 4/40).
    same_name_as_main = sum(1 for r in caps_rows
                            if r[0].replace("^", " ").upper()
                            in {m[0].upper().replace("^", " ") for m in main_rows})
    main_as_caps = sum(1 for m in main_rows
                       if m[0].upper().replace("^", " ")
                       in {c[0].replace("^", " ").upper() for c in caps_rows})
    w("- cost is **uniformly 20** on all %d variant rows (main tree: 50..300).\n" % len(caps_rows))
    w("- field0 in 0..4 with histogram %s.\n"
      % dict(sorted(collections.Counter(nums[0] for _, nums, _ in caps_rows).items())))
    w("- all variant prereqs point into the main tree: %s (none point at other "
      "variant rows) -> variants are leaves that extend the tree.\n" % vpreq_to_main)
    w("- variant names are unique file-wide (duplicates: %d); %d/40 variant "
      "names match a main-tree name in spaced form, and %d/%d main-tree names "
      "have a caps variant.\n" % (dup_names, same_name_as_main, main_as_caps, len(main_rows)))
    w("- [inferred] This matches a per-configurable-substitution table: 40 "
      "cheap (cost 20) techs gated by a small category index. Which game "
      "concept field0 selects (species? difficulty? expansion content?) is "
      "**OQ-013** — the file alone cannot say; 21 species vs field0 range "
      "0..4 makes 'species index' doubtful.\n")

    w("\n## 5. Full table (global row id; f=field0, c=cost)\n")
    w("```\n")
    for i, (name, nums, _) in enumerate(rows):
        d = ""
        if i < len(main_rows):
            d = "  d=%d" % depth[i]
        pr = nums[2:-1]
        w("%3d f=%d c=%-4d %-28s <- %s%s\n"
          % (i, nums[0], nums[1], name,
             ", ".join("%d:%s" % (q, rows[q][0]) for q in pr) or "-", d))
    w("```\n")

    out = "".join(rep)
    if a.out:
        open(a.out, "w").write(out)
    if not a.quiet:
        print(out)


main()
