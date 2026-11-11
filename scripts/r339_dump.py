#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t339 — dump a verbatim disasm range from work/r331_disasm.txt.
Usage: r339_dump.py START [END]  (hex, inclusive)."""
import re, sys
INSN = re.compile(r"^\s+([0-9a-f]+):\s*((?:[0-9a-f]{2}[ ]?)+)\s+(.*)$")
lo = int(sys.argv[1], 16)
hi = int(sys.argv[2], 16) if len(sys.argv) > 2 else lo + 0x40
with open("work/r331_disasm.txt", errors="replace") as f:
    for line in f:
        m = INSN.match(line)
        if not m:
            continue
        a = int(m.group(1), 16)
        if a < lo:
            continue
        if a > hi:
            break
        print(f"{m.group(1)}:\t{m.group(3).split('#')[0].strip()}")
