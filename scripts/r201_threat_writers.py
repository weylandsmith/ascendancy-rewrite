#!/usr/bin/env python3
"""t201 — writer/reader census for planet threat bytes +0x58/+0x59.

Scans obj0 code [0x14bb0,0x82bb0) in work/ascend_restored.bin (base-0
address space, OQ-008/OQ-011 law) with capstone for every instruction whose
memory operand has disp32 == 0x58 or 0x59 (any base reg). Classifies:
  W = store to the byte/dword (mov [m],r / inc / dec / or|and|xor|add|sub [m],*)
  R = read
Prints site address, mnemonic, op-string. Context attribution (planet vs
ship vs other) is done by the caller manually via field-identity anchors;
the census itself is mechanical and exhaustive.

Usage: r201_threat_writers.py [IMG]
"""
import sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

img = open(sys.argv[1] if len(sys.argv) > 1 else "work/ascend_restored.bin", "rb").read()
LO, HI = 0x14BB0, 0x82BB0
md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = True

WRITE_MN = {"mov", "movzx", "movsx", "inc", "dec", "neg", "neg", "xchg",
            "or", "and", "xor", "add", "sub", "sbb", "shl", "shr", "sar",
            "stosb", "stosd", "rep stosb", "rep stosd", "movabs"}

rows = []
# t201 PITFALL: sequential capstone disasm STOPS at the first data gap
# (region ends coverage at 0x1ca34 of [0x14bb0,0x82bb0)). Resume by skipping
# 1 byte on StopIteration until the window is consumed.
off = LO
while off < HI:
    end = off  # if this disasm run yields nothing, we skip 1 byte
    it = md.disasm(img[off:HI], off)
    try:
        while True:
            ins = next(it)
            for o in ins.operands:
                if o.type == 3 and o.mem.disp in (0x58, 0x59) and ins.reg_name(o.mem.base):
                    is_write = ins.mnemonic in WRITE_MN and o is ins.operands[0]
                    rows.append((ins.address, "W" if is_write else "R",
                                 ins.mnemonic, ins.op_str))
                    break
            end = ins.address + ins.size
    except StopIteration:
        pass
    off = end if end > off else off + 1

import collections
by_addr = {}
for a, w, m, ops in rows:
    by_addr[a] = (w, m, ops)
wc = sum(1 for v in by_addr.values() if v[0] == "W")
print(f"total sites={len(by_addr)}  W={wc}  R={len(by_addr)-wc}")
for a in sorted(by_addr):
    w, m, ops = by_addr[a]
    print(f"{a:05x} {w} {m} {ops}")
