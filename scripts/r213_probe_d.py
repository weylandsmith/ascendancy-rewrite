#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t213 probe D — the two soundness checks S5 rests on:
 (D1) EVERY in-edge of 0x15c14 (the bl=1 init block) and 0x15c34, across the
      WHOLE function -> confirms site-1 phase==1 is unconditional once entered.
 (D2) value of ah feeding 0x16e8b `mov byte [esp],ah` (5th phase-local def);
      print 0x16e40..0x16e90 + all `mov ah,` defs in the function.
 (D3) confirm 0x15e23 has in-edges ONLY {0x16378 jump} and its only out-edge
      to 0x15e7c (tail) — i.e. phase=1 via site-2 buffer never reaches 0x15d98.
Usage: r213_probe_d.py [IMG]"""
import sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

IMG = sys.argv[1] if len(sys.argv) > 1 else "work/ascend_restored.bin"
img = open(IMG, "rb").read()
FLO, FHI = 0x156D4, 0x17C25


def decode(lo, hi):
    out = {}
    off = lo
    while off < hi:
        md = Cs(CS_ARCH_X86, CS_MODE_32)
        md.detail = True
        got = False
        for ins in md.disasm(img[off:hi], off):
            out[ins.address] = ins
            off = ins.address + ins.size
            got = True
        if not got:
            off += 1
    return out


fn = decode(FLO, FHI)
edges = {}
for a, ins in fn.items():
    if ins.mnemonic.startswith("j"):
        for op in ins.operands:
            if op.type == 2:
                edges.setdefault(op.imm, []).append(a)
    if ins.mnemonic not in ("jmp", "ret", "retf"):
        nxt = a + ins.size
        if nxt in fn:
            edges.setdefault(nxt, []).append(a)

print("== D1 in-edges ==")
for t in (0x15C14, 0x15C34, 0x15C63, 0x15E23, 0x15D36, 0x15D8F):
    print(f"  {t:#07x} <- {[hex(x) for x in sorted(edges.get(t, []))]}")

print("\n== D2 ah defs in function ==")
for a in sorted(fn):
    if fn[a].mnemonic == "mov" and fn[a].op_str.startswith("ah,"):
        print(f"  {a:#07x} mov {fn[a].op_str}")
print("  window 0x16e40..0x16e95:")
md = Cs(CS_ARCH_X86, CS_MODE_32)
for ins in md.disasm(img[0x16E40:0x16E95], 0x16E40):
    print(f"    {ins.address:#07x} {ins.mnemonic} {ins.op_str}")

print("\n== D3 out-edges of 0x15e23..0x15e42 (linear? any jcc?) ==")
for a in sorted(fn):
    if 0x15E23 <= a <= 0x15E43:
        print(f"  {a:#07x} {fn[a].mnemonic} {fn[a].op_str}")
