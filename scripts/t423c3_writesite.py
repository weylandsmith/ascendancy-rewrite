#!/usr/bin/env python3
"""t423c3: find writes to an absolute address (imm32 = target as MOV dest)
in the restored image. Covers: C7 /0 with disp32==T (mov [abs],imm),
mov [abs],reg is 89 /0 with modrm SIB disp32==T, and the common vendor
form 8B/89 with SIB 25 (abs). Also FF-group none. Prints hex sites."""
import sys, struct

PATH = "/home/hrethric/projects/ascendancy/work/ascend_restored.bin"
data = open(PATH, "rb").read()
CODE_LO, CODE_HI = 0x14bb0, 0x82bb0

for t in sys.argv[1:]:
    T = int(t, 16)
    pack = struct.pack("<I", T)
    sites = []
    for i in range(CODE_LO, CODE_HI - 8):
        b = data[i]
        if b == 0xA3:  # MOV moffs32, EAX
            if data[i + 1:i + 5] == pack:
                sites.append((i, "A3 mov moffs,eax"))
        elif b == 0x8C:  # MOV m32, Sreg
            modrm = data[i + 1]
            mod = modrm >> 6
            rm = modrm & 7
            if mod == 0 and rm == 5 and data[i + 2:i + 6] == pack:
                sites.append((i, "8C mov m,sreg"))
        elif b in (0x89, 0x88, 0xC7, 0xA2):
            modrm = data[i + 1]
            mod = modrm >> 6
            rm = modrm & 7
            if mod == 0 and rm == 5:  # direct [disp32]
                if data[i + 2:i + 6] == pack:
                    sites.append((i, f"{hex(b)} direct"))
            elif mod == 0 and rm == 4 and data[i + 3:i + 7] == pack:  # SIB no base
                if data[i + 2] in (0x25, 0x0D, 0x15, 0x35):
                    sites.append((i, f"{hex(b)} sib-abs"))
    print(hex(T), len(sites))
    for s in sites:
        print("  ", hex(s[0]), s[1])
