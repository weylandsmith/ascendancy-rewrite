#!/usr/bin/env python3
"""t402: locate call sites of the static.txt string getter (FUN_00021a20)
that fetch the status-list strings (getter indices 136..141 = the status.cpp
region), and disassemble around them. base-0 image: addr == file offset.
Usage: t402_status_getters.py [img]"""
import sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

IMG = sys.argv[1] if len(sys.argv) > 1 else "work/ascend_restored.bin"
data = open(IMG, "rb").read()
CODE_LO, CODE_HI = 0x14bb0, 0x82bb0
GETTER = 0x21a20

def sites(idx):
    out = []
    i = CODE_LO
    pat = b"\xb8" + idx.to_bytes(3, "little") + b"\x00"  # MOV EAX, imm32
    while True:
        i = data.find(pat, i + 1)
        if i < 0 or i >= CODE_HI:
            break
        # look for a CALL rel32 to GETTER within 16 bytes
        j = i
        while True:
            j = data.find(b"\xe8", j + 1, i + 16)
            if j < 0:
                break
            rel = int.from_bytes(data[j + 1:j + 5], "little", signed=True)
            if (j + 5 + rel) & 0xFFFFFFFF == GETTER:
                out.append(i)
                break
    return out

md = Cs(CS_ARCH_X86, CS_MODE_32)
names = {136: "(%s %s Planet)", 137: "Self-Managed", 138: " - No Progress",
         139: " - %d day%s until completion", 140: "Building %s%s",
         141: "No Project", 147: "Under Construction at %s",
         151: "planets header", 152: "ships header"}
for g in sorted(names):
    s = sites(g)
    print(f"getter {g} ({names[g]}): {len(s)} sites {[hex(x) for x in s]}")

# disassemble the function(s) containing the 136/139/140 sites
targets = sorted(set(sites(136) + sites(139) + sites(140) + sites(141)))
if targets:
    lo = max(CODE_LO, min(targets) - 0x180)
    hi = min(CODE_HI, max(targets) + 0x120)
    print(f"===== disasm {lo:#x}..{hi:#x} =====")
    for ins in md.disasm(data[lo:hi], lo):
        print(f"{ins.address:#07x}  {ins.mnemonic}\t{ins.op_str}")
