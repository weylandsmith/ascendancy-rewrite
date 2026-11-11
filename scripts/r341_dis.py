#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t341 helper: stream a disassembly range from work/r331_disasm.txt (restored
image, file offsets == guest offsets for obj0 code [0x14bb0,0x82bb0)).

Usage: r341_dis.py START END [--xref]   (hex, END exclusive)
Prints one instruction per line: 'addr  mnem ops'.
--xref additionally prints direct-call xrefs INTO the range.
"""
import re
import sys

PATH = "work/r331_disasm.txt"
PAT = re.compile(r"^\s+([0-9a-f]+):\t([0-9a-f ]+)\t(.*)$")


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
    lo = int(sys.argv[1], 16)
    hi = int(sys.argv[2], 16)
    ins = load()
    for a in sorted(ins):
        if lo <= a < hi:
            print("%05x  %s %s" % (a, ins[a][0], ins[a][1]))
    if "--xref" in sys.argv:
        xr = []
        for a in sorted(ins):
            mn, ops = ins[a]
            if mn.startswith("call") and ops.strip().startswith("0x"):
                try:
                    t = int(ops.strip(), 16)
                except ValueError:
                    continue
                if lo <= t < hi:
                    xr.append("%05x->%05x" % (a, t))
        print("XREF-CALLS-INTO-RANGE:", " ".join(xr) if xr else "NONE")


if __name__ == "__main__":
    main()
