#!/usr/bin/env python3
# t326b: name gizmo rows around the 0x1c/0x1d/0x1e dispatch keys.
# Law: gizmo rec = idx*0x6a + 0x7650c (cited combat.md); dispatch reads
# BYTE[[edi]+1] where edi walks the table (0x17c37: mov al,[eax+0x1]).
# Also dump what values 0x4c/0x4d/0x4e (76/77/78) index into at
# [esi+0x1a92+edi*4] (the fn 0x17b2c consumer at 0x17cf8..0x17d11).
import struct
data = open("work/ascend_payload.bin", "rb").read()
base = 0x7650c
stride = 0x6a
for i in (70, 71, 72, 75, 76, 77, 77, 78, 79, 28, 29, 30):
    off = base + i * stride
    row = data[off:off + stride]
    j = 0
    while j < len(row) and not (32 <= row[j] < 127):
        j += 1
    name = b""
    while j < len(row) and 32 <= row[j] < 127:
        name += bytes([row[j]])
        j += 1
    w33 = struct.unpack("<H", row[0x33:0x35])[0]
    b1 = row[0x1]
    p36 = struct.unpack("<I", row[0x36:0x3a])[0]
    dup = " DUP" if i in (71, 77) else ""
    print(f"idx {i:3d} off {hex(off)} name={name!r:30} byte+1={b1:#04x} word+0x33={w33:#06x} dword+0x36={p36}{dup}")
