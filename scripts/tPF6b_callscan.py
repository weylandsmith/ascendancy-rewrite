"""tPF6-B: exhaustive rel32 call-site census for the vendor placement checker
0x3830c and the REQUIRES predicate 0x46d3c over the obj0 code range.

Usage: ~/tools/revenv/bin/python scripts/tPF6b_callscan.py [TARGET_HEX ...]
Prints each call site (address of the call opcode) grouped by target.
"""
import sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

data = open('work/ascend_restored.bin', 'rb').read()
LO, HI = 0x14bb0, 0x82bb0          # obj0 code range (pointer law, OQ-011 CLOSED)
targets = {int(a, 16) for a in sys.argv[1:]} or {0x3830c, 0x46d3c}

hits = {t: [] for t in targets}
i = LO
while i < HI - 5:
    if data[i] == 0xE8:
        rel = int.from_bytes(data[i + 1:i + 5], 'little', signed=True)
        t = (i + 5 + rel) & 0xFFFFFFFF
        if t in hits:
            hits[t].append(i)
        i += 5
    else:
        i += 1
for t in sorted(hits):
    print(f"target {t:x}: {len(hits[t])} call sites")
    for a in hits[t]:
        print(f"  {a:x}")
