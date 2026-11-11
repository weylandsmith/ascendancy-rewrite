#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t211: who reaches block 0x4a350? Decode obj0 and list ALL branch edges
(jcc rel8/rel32, jmp rel, call rel) whose TARGET == 0x4a350, plus fallthrough
check (does any decoded insn END exactly at 0x4a350)."""
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
img = open("work/ascend_restored.bin", "rb").read()

def decode_all(lo, hi):
    out = {}
    off = lo
    while off < hi:
        md = Cs(CS_ARCH_X86, CS_MODE_32); md.detail = True
        got = False
        for ins in md.disasm(img[off:hi], off):
            out[ins.address] = ins
            off = ins.address + ins.size
            got = True
        if not got:
            off += 1
    return out

TGT = 0x4a350
insns = decode_all(0x49000, 0x4b000)
print("== branch edges targeting", hex(TGT), "==")
for a, i in sorted(insns.items()):
    if i.mnemonic.startswith(("j", "call")) and i.op_str.startswith("0x"):
        try:
            if int(i.op_str, 16) == TGT:
                print(f"  {a:#07x} {i.mnemonic} {i.op_str}")
        except ValueError:
            pass
ends = [hex(a) for a, i in insns.items() if a + i.size == TGT]
print("insns ending exactly at target (fallthrough):", ends)
for a in (0x4a340,):
    pass
# print tail of 0x49f54 body for the record
print("== 0x4a340..0x4a360 ==")
for a in sorted(insns):
    if 0x4a340 <= a < 0x4a360:
        print(f"  {a:#07x} {img[a:a+insns[a].size].hex():<12} {insns[a].mnemonic} {insns[a].op_str}")
