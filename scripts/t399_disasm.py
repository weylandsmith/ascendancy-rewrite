#!/usr/bin/env python3
"""t399: disassemble vendor 3D->2D cosmos projection candidates.
work/ascend_restored.bin is the base-0 restored image (file offset == address).
Usage: python3 t399_disasm.py START END [START END ...]
"""
import sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

data = open("work/ascend_restored.bin", "rb").read()
md = Cs(CS_ARCH_X86, CS_MODE_32)
args = sys.argv[1:]
for i in range(0, len(args), 2):
    lo, hi = int(args[i], 16), int(args[i + 1], 16)
    print(f"===== {lo:#x}..{hi:#x} =====")
    for ins in md.disasm(data[lo:hi], lo):
        print(f"{ins.address:#07x}  {ins.mnemonic}\t{ins.op_str}")
