#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t341: static census for the factory auto-reserve question.

Restored image work/ascend_restored.bin disassembled at work/r331_disasm.txt
(file offset == guest offset for obj0 code [0x14bb0,0x82bb0)).

Prints:
  1. direct call xrefs into the selector/queue family
  2. every instruction storing to displacement +0x52 (WORD) and +0x54 (BYTE)
     -- the planet build-queue queue-slot / item fields
  3. every read of globals 0x7458e, 0x10ba4 with the enclosing address
Exit codes: 0 always (instrument, not a test).
"""
import re
import sys

PATH = "work/r331_disasm.txt"
PAT = re.compile(r"^\s+([0-9a-f]+):\t([0-9a-f ]+)\t(.*)$")

FAMILY = (0x3EA54, 0x3F130, 0x38BA4, 0x3958C, 0x40018, 0x43B50, 0x3ECB8,
          0x3EF2C, 0x44690, 0x3EB88, 0x38F68)
GLOBALS = ("0x7458e", "0x10ba4")


def load():
    ins = {}
    with open(PATH, errors="replace") as f:
        for line in f:
            m = PAT.match(line.rstrip("\n"))
            if not m:
                continue
            a = int(m.group(1), 16)
            rest = m.group(3)
            parts = rest.split(None, 1)
            ins[a] = (parts[0] if parts else "", parts[1] if len(parts) > 1 else "")
    return ins


def main():
    ins = load()
    print("== 1. direct call xrefs into queue/selector family ==")
    for t in FAMILY:
        cs = ["%05x" % a for a in sorted(ins)
              if ins[a][0].startswith("call") and ins[a][1].strip() == "0x%x" % t]
        print("  ->%05x : %s" % (t, " ".join(cs) if cs else "NONE"))

    print("== 2. stores to +0x52 / +0x54 (queue fields) ==")
    n52 = n54 = 0
    for a in sorted(ins):
        mn, ops = ins[a]
        if mn not in ("mov", "or", "or", "and", "lea", "add", "add", "sub", "inc", "dec"):
            continue
        if "+0x52]" in ops or "+0x54]" in ops:
            # store: displacement on the DESTINATION (first operand)
            dst = ops.split(",")[0]
            if ("+0x52]" in dst) or ("+0x54]" in dst):
                kind = "52" if "+0x52]" in dst else "54"
                if kind == "52":
                    n52 += 1
                else:
                    n54 += 1
                print("  %05x  %-4s %s" % (a, mn, ops))
    print("  counts: +0x52-store=%d +0x54-store=%d" % (n52, n54))

    print("== 3. references to globals %s ==" % ", ".join(GLOBALS))
    for g in GLOBALS:
        hits = ["%05x %s %s" % (a, ins[a][0], ins[a][1]) for a in sorted(ins)
                if g in ins[a][1]]
        print("  %s: %d refs" % (g, len(hits)))
        for h in hits[:60]:
            print("    " + h)


if __name__ == "__main__":
    sys.exit(main())
