#!/usr/bin/env python3
"""t211 probe A: call graph inside the [ship+0x62]==0 leg 0x49f54, plus
whole-image E8 caller census of 0x49f54, plus writers of [reg+0x62]."""
import sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_32, CS_OP_MEM, CS_OP_REG, CS_OP_IMM

IMG = sys.argv[1] if len(sys.argv) > 1 else "work/ascend_restored.bin"
img = open(IMG, "rb").read()
CODE_LO, CODE_HI = 0x14bb0, 0x82bb0

def decode(lo, hi):
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

# 1) calls inside 0x49f54 body (functions_full: entry 0x49f54 size 1020 -> ..0x4a34f)
body = decode(0x49f54, 0x4a360)
print("== calls inside 0x49f54..0x4a360 ==")
for a, i in sorted(body.items()):
    if i.mnemonic == "call":
        print(f"  {a:#07x} call {i.op_str}")
rets = sorted(hex(a) for a, i in body.items() if i.mnemonic in ("ret", "retf"))
print("ret sites:", rets)

# 2) E8 callers of a target over the whole code range
def callers_of(tgt):
    out = []
    for a in range(CODE_LO, CODE_HI - 5):
        if img[a] == 0xE8:
            rel = int.from_bytes(img[a + 1:a + 5], "little", signed=True)
            if a + 5 + rel == tgt:
                out.append(a)
    return out

print("\n== E8 callers of 0x49f54 ==", [hex(x) for x in callers_of(0x49f54)])
print("== E8 callers of 0x4a360 ==", [hex(x) for x in callers_of(0x4a360)])
print("== E8 callers of 0x49f28 ==", [hex(x) for x in callers_of(0x49f28)])
