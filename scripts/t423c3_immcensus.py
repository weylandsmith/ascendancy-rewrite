#!/usr/bin/env python3
"""t423c3: whole-image imm32 operand census for given immediates.
Restored image imagebase 0: file offset == address. Scans code region
[0x14bb0,0x82bb0) for MOV reg/imm32 (B8+rd, C7 /0) and any dword window
(equal value anywhere — superset, reported separately)."""
import sys, struct

PATH = "/home/hrethric/projects/ascendancy/work/ascend_restored.bin"
data = open(PATH, "rb").read()
CODE_LO, CODE_HI = 0x14bb0, 0x82bb0

for t in sys.argv[1:]:
    T = int(t, 16) if t.lower().startswith("0x") else int(t)
    pack = struct.pack("<I", T & 0xFFFFFFFF)
    movi = []   # MOV r32, imm32 (B8+r) or C7 /0
    dword = []  # dword equal anywhere (superset incl. operands inside instrs)
    i = CODE_LO
    while i < CODE_HI - 5:
        b = data[i]
        if 0xB8 <= b <= 0xBF:
            if data[i + 1:i + 5] == pack:
                movi.append(hex(i))
            i += 5
            continue
        if b == 0xC7 and (data[i + 1] & 7) == 0:
            if data[i + 2:i + 6] == pack:
                movi.append(hex(i))
            i += 6
            continue
        i += 1
    j = CODE_LO
    while True:
        j = data.find(pack, j, CODE_HI)
        if j < 0:
            break
        dword.append(hex(j))
        j += 1
    print(f"== imm {hex(T)}: MOV-imm sites {len(movi)} | dword-equal {len(dword)}")
    print("   MOV:", " ".join(movi[:80]))
    extra = set(dword) - set(movi)
    print("   other dword offsets:", " ".join(sorted(extra, key=lambda x: int(x,16))[:80]))
