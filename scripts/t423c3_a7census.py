#!/usr/bin/env python3
"""t423c3: census every write to window field +0xa7 (the paint-vtable slot
pointer) and every indirect call through [reg+0xa7]+off, in the restored
image (imagebase 0, file offset == address; OQ-008 loader model)."""
import sys

PATH = sys.argv[1] if len(sys.argv) > 1 else \
    "/home/hrethric/projects/ascendancy/work/ascend_restored.bin"
data = open(PATH, "rb").read()
print("size", hex(len(data)))

# MOV r/m32, r32  : 89 /r  with mod!=00 and r/m=100 (SIB) and disp32==0xa7
# MOV r/m32, imm32: C7 /0  likewise
writes = []
for i in range(len(data) - 7):
    op = data[i]
    if op not in (0x89, 0xC7):
        continue
    modrm = data[i + 1]
    mod = modrm >> 6
    rm = modrm & 7
    if mod == 2 and rm == 4:  # disp32 + SIB
        if data[i + 6:i + 10] == b"\xa7\x00\x00\x00":
            writes.append((i, modrm, data[i:i + 11].hex()))
    elif mod == 2 and rm != 4:  # disp32 + reg
        if data[i + 2:i + 6] == b"\xa7\x00\x00\x00":
            writes.append((i, modrm, data[i:i + 7].hex()))
print("== writes to +0xa7:", len(writes))
for a, modrm, hx in writes:
    print(hex(a), hex(modrm), hx)

# FF /2  CALL r/m32 through [reg+disp8/disp32] where disp == 0xa7
calls = []
for i in range(len(data) - 4):
    if data[i] != 0xFF:
        continue
    modrm = data[i + 1]
    if (modrm >> 5) != 4:  # /2 group within 0xFF is reg=010
        continue
    mod = modrm >> 6
    rm = modrm & 7
    if mod == 1 and rm != 4 and data[i + 2] == 0xa7:
        calls.append((i, "disp8", data[i:i + 3].hex()))
    elif mod == 2 and rm != 4 and data[i + 2:i + 6] == b"\xa7\x00\x00\x00":
        calls.append((i, "disp32", data[i:i + 7].hex()))
print("== calls through +0xa7:", len(calls))
for c in calls:
    print(hex(c[0]), c[1], c[2])
