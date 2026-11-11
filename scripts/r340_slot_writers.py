#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r340_slot_writers.py — census: every instruction in FUN_00038f68
(0x38f68..0x394d8) that WRITES a slot-array dword/word (reg base + idx*4).
Supports the t340 residue-(4) closure: the completion handler is expected to
be the sole slot-value writer in the build-queue function."""
import re
import sys

RX = re.compile(r"^\s*([0-9a-fA-F]{4,6}):\t((?:[0-9a-f]{2} )+) *\t(.*)$")
LO, HI = 0x38F68, 0x394D8
STORES = ("mov", "or", "and", "xor", "xor,", "add", "sub", "inc", "dec",
          "bts", "lock", "not", "not,", "shl", "shr")
IDX4 = re.compile(r"\*\s*4\s*\+")
REG = re.compile(r"\b(eax|ebx|ecx|esi|edi|ebp|esp|edx)\b")


def main(path="work/r331_disasm.txt"):
    hits = []
    for line in open(path, errors="replace"):
        m = RX.match(line.rstrip())
        if not m:
            continue
        a = int(m.group(1), 16)
        if not (LO <= a < HI):
            continue
        txt = m.group(3).strip()
        op = txt.split()[0].lower() if txt.split() else ""
        if op not in STORES:
            continue
        # destination operand = first operand; must contain *4 (index scale)
        dest = txt.split(None, 1)[1].split(",")[0] if " " in txt else ""
        if IDX4.search(dest):
            hits.append((hex(a), txt))
    for h in hits:
        print(h[0], h[1])
    print(f"total slot-array *4 store sites in fn: {len(hits)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
