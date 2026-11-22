#!/usr/bin/env python3
"""tNGS3 W1 static census: who STORES to window field +0xc0 (latch byte)?
Byte-level scan over work/ascend_payload.bin for mov r/m,+0xc0 store forms."""
import struct

pay = open("work/ascend_payload.bin", "rb").read()
n = len(pay)
hits = []
for i in range(n - 8):
    b0 = pay[i]
    j = i
    if b0 == 0x66 and pay[i + 1] in (0x89, 0xC7):
        j = i + 1
    elif b0 not in (0x88, 0x89, 0xC6, 0xC7):
        continue
    modrm = pay[j + 1]
    mod = modrm >> 6
    rm = modrm & 7
    if mod == 1 and pay[j + 2] == 0xC0:
        hits.append((j, "disp8", pay[j:j + 9].hex(" ")))
    elif mod == 0 and rm == 5 and struct.unpack_from("<I", pay, j + 2)[0] == 0xC0:
        hits.append((j, "disp32-abs", pay[j:j + 9].hex(" ")))
    elif mod == 2 and struct.unpack_from("<I", pay, j + 2)[0] == 0xC0:
        hits.append((j, "disp32", pay[j:j + 9].hex(" ")))
print("store-to-+0xc0 sites:", len(hits))
for j, kind, bs in hits:
    print(hex(j), kind, bs)
