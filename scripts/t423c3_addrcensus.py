#!/usr/bin/env python3
"""t423c3: whole-image access census for a list of absolute guest addresses:
report every site where the address appears as an imm32 operand of a push/mov/movsd-lea
window, plus raw dword-equal offsets (superset). Restored image imagebase 0."""
import sys, struct

PATH = "/home/hrethric/projects/ascendancy/work/ascend_restored.bin"
data = open(PATH, "rb").read()
CODE_LO, CODE_HI = 0x14bb0, 0x82bb0

for t in sys.argv[1:]:
    T = int(t, 16)
    pack = struct.pack("<I", T)
    # raw dword-equal everywhere
    offs = []
    j = 0
    while True:
        j = data.find(pack, j)
        if j < 0:
            break
        offs.append(j)
        j += 1
    print(f"== addr {hex(T)}: dword-equal offsets {[hex(o) for o in offs]}")
    for o in offs:
        if CODE_LO <= o < CODE_HI:
            # show surrounding bytes decoded shallowly: preceding opcode
            ctx = data[max(o-3,0):o+6]
            print(f"   in-code at {hex(o)} ctx {ctx.hex()}")
