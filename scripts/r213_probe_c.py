#!/usr/bin/env python3
"""t213 probe C — (C1) tail chain after 0x15e7c (back-edges?),
(C2) exhaustive byte-defs of the two phase locals + linear block 0x1632f..0x16364,
(C3) batmode-order vocabulary corroboration (command ids 0x326/0x327/0x328,
    the vendor assert call 0x2a428(id, line) sites in the function).
Usage: r213_probe_c.py [IMG]"""
import sys, re
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

print("== C1 tail chain from 0x15e7c ==")
for a in sorted(fn):
    if 0x15E7C <= a <= 0x16020:
        i = fn[a]
        tag = ""
        if i.mnemonic.startswith("j"):
            for op in i.operands:
                if op.type == 2 and op.imm < 0x15E7C:
                    tag = f"  << BACK-EDGE to {op.imm:#x}"
        print(f"  {a:#07x} {i.mnemonic} {i.op_str}{tag}")
        if i.mnemonic == "ret" and a > 0x15E7C:
            break

print("\n== C2 byte-defs of phase locals (whole function) ==")
for a in sorted(fn):
    o = fn[a].op_str
    m = fn[a].mnemonic
    if m == "mov" and (o.startswith("byte ptr [esp + 0x50]") or o.startswith("byte ptr [esp],")):
        print(f"  {a:#07x} mov {o}")
print("\n== C2b linear block 0x1632f..0x16364 (is 0x16361 straight-line after dl=2?) ==")
for a in sorted(fn):
    if 0x1632F <= a <= 0x16364:
        print(f"  {a:#07x} {fn[a].mnemonic} {fn[a].op_str}")

print("\n== C3 vendor assert calls 0x2a428(id,line) in function (command-id vocabulary) ==")
ids = []
for a in sorted(fn):
    if fn[a].mnemonic == "call" and fn[a].op_str.startswith("0x2a428"):
        bid = bline = None
        for b in sorted((x for x in fn if a - 24 <= x < a), reverse=True):
            o = fn[b].op_str
            if bid is None and fn[b].mnemonic == "mov" and o.startswith("ebx, "):
                try:
                    bid = int(o.split(", ")[1], 0)
                except ValueError:
                    bid = o.split(", ")[1]
            if bline is None and fn[b].mnemonic == "mov" and o.startswith("edx, "):
                try:
                    bline = int(o.split(", ")[1], 0)
                except ValueError:
                    bline = o.split(", ")[1]
        ids.append((hex(a), bid, bline))
print(f"  {len(ids)} assert sites")
print("  ids in [0x300,0x360):", [x for x in ids if isinstance(x[1], int) and 0x300 <= x[1] < 0x360])
print("  first 25:", ids[:25])

# C4: what do 0x16cf0 (tail callee) and command arg mean — first 12 insns of 0x16cf0
print("\n== C4 head of 0x16cf0 (tail callee) ==")
md = Cs(CS_ARCH_X86, CS_MODE_32)
for ins in md.disasm(img[0x16CF0:0x16D20], 0x16CF0):
    print(f"  {ins.address:#07x} {ins.mnemonic} {ins.op_str}")
