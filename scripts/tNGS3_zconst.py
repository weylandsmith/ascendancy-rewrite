#!/usr/bin/env python3
"""tNGS3 Z1 probe 3: the constants + reset imm of the star-pos generator
FUN_00022878 (0x22b2c..0x22cb1): 3x rng%1000-500 -> FUN_00052fa0 -> *s."""
import struct

pay = open("work/ascend_payload.bin", "rb").read()
print("bytes 22aee:", pay[0x22aee:0x22af9].hex(" "))
imm = struct.unpack_from("<I", pay, 0x22aee + 7)[0]
print("reset imm32:", hex(imm), "as f32:", struct.unpack("<f", struct.pack("<I", imm))[0])
for a in (0x836fc, 0xb50):
    d = struct.unpack_from("<I", pay, a)[0]
    f = struct.unpack("<f", struct.pack("<I", d))[0]
    print(f"[{a:#x}] = {d:#010x} as f32 = {f}")
