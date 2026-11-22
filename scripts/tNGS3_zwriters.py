#!/usr/bin/env python3
"""tNGS3 Z1 probe 2: writers of star-rec +0x34 (z) + shell-radius immediates.

(1) FP stores: D9 /3 (fstp m32), DD /0 (fsts m32) with disp8=0x34 or
    disp32=0x34 — candidate z writers.
(2) integer immediates 0x1B8 (440) anywhere in code — shell origin.
(3) float 440.0 single site 0x2288d context is handled separately.
"""
import struct

pay = open("work/ascend_payload.bin", "rb").read()
n = len(pay)

fp_stores = []
imm440 = []
for i in range(n - 7):
    b = pay[i]
    # fstp m32 = D9 /3 ; fsts m32 = D9 /1 ; fstp m64 = DD /3
    if b in (0xD9, 0xDD):
        modrm = pay[i + 1]
        reg = (modrm >> 3) & 7
        if b == 0xD9 and reg not in (1, 3):
            continue
        if b == 0xDD and reg != 3:
            continue
        mod = modrm >> 6
        rm = modrm & 7
        if mod == 1 and pay[i + 2] == 0x34:
            fp_stores.append((i, "disp8", pay[i:i + 6].hex(" ")))
        elif mod == 2 and struct.unpack_from("<I", pay, i + 2)[0] == 0x34:
            fp_stores.append((i, "disp32", pay[i:i + 9].hex(" ")))
    if b == 0xB8 + 0 or b in (0xB8, 0xB9, 0xBA, 0xBB, 0xBE, 0xBF):
        if struct.unpack_from("<I", pay, i + 1)[0] == 440:
            imm440.append((i, pay[i:i + 5].hex(" ")))

print(f"FP store to +0x34 candidates: {len(fp_stores)}")
for i, k, bs in fp_stores:
    print(" ", hex(i), k, bs)
print(f"mov r32,440 immediates: {len(imm440)}")
for i, bs in imm440:
    print(" ", hex(i), bs)
