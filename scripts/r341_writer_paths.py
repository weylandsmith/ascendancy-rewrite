#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t341 decisive census: every path into the queue writer fn 0x38840.

Restored image disasm work/r331_disasm.txt (file offset == guest offset for
obj0 code). Prints:
  1. direct callers of 0x38718 (queue-store worker) and 0x3875c (cell picker)
  2. ALL direct callers of 0x38840 with the owning function span
     (work/functions_full.tsv)
  3. call-site ranges of fn 0x38f68 / 0x3e6e0 (phase order anchors)
Exit 0 always.
"""
import re
import sys

PATH = "work/r331_disasm.txt"
PAT = re.compile(r"^\s+([0-9a-f]+):\t([0-9a-f ]+)\t(.*)$")


def load():
    ins = {}
    for line in open(PATH, errors="replace"):
        m = PAT.match(line.rstrip("\n"))
        if not m:
            continue
        a = int(m.group(1), 16)
        rest = m.group(3)
        parts = rest.split(None, 1)
        ins[a] = (parts[0] if parts else "", parts[1] if len(parts) > 1 else "")
    return ins


def spans():
    fs = []
    for l in open("work/functions_full.tsv").read().splitlines()[1:]:
        p = l.split("\t")
        if len(p) > 1 and p[1].strip():
            fs.append((int(p[0], 16), int(p[1], 16)))
    fs.sort()
    return fs


def own(fs, a):
    for s, sz in fs:
        if s <= a < s + sz:
            return "%05x(+%x)" % (a - s, sz)
    return "DARK"


def main():
    ins = load()
    fs = spans()
    for tgt in (0x38718, 0x3875C, 0x38840, 0x38818):
        cs = [a for a in sorted(ins)
              if ins[a][0].startswith("call") and ins[a][1].strip() == "0x%x" % tgt]
        print("callers of %05x (%d):" % (tgt, len(cs)))
        for a in cs:
            print("   %05x in fn %s" % (a, own(fs, a)))
    # indirect calls (call [reg] / call [mem]) inside 0x38000..0x41000
    ind = [a for a in sorted(ins)
           if ins[a][0] == "call" and not ins[a][1].strip().startswith("0x")
           and 0x38000 <= a < 0x41000]
    print("indirect calls 0x38000..0x41000:", " ".join("%05x %s %s" % (a, ins[a][0], ins[a][1]) for a in ind) or "NONE")
    for tgt in (0x38F68, 0x3E6E0):
        cs = [a for a in sorted(ins)
              if ins[a][0].startswith("call") and ins[a][1].strip() == "0x%x" % tgt]
        print("callers of %05x:" % tgt, ["%05x@fn%s" % (a, own(fs, a)) for a in cs])
    return 0


if __name__ == "__main__":
    sys.exit(main())
