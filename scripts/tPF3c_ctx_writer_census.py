#!/usr/bin/env python3
"""tPF-3c TPF3-B writer census: who WRITES the fill-context table 0x48c33 and
the draw-context 0x4850c fields (esp +0x14 = the fill map pointer read by the
polygon filler 0x62d15 at 0x63015).

Filler law read this session (work/tPF3b_inset.asm + r290_disasm 0x62d15):
  0x62d15(arg1=[0x48c33]+pen*0x100, arg2=vtx, arg3=4, arg4=0x4850c)
  interior (0x63015..): esi=[ebp+0x14]; per pixel: al=[screen]; dl=[eax+esi]
  -> screen byte := MAP[OLD screen byte] with MAP = arg4+0x14 (a 256-entry
  colour TRANSLATION table = the translucency mechanism). The per-pen 256-byte
  blocks are the arg1 CLIP/BOUNDS contexts ([blk+0],+4,+8,+0xc,+0x10 read).
Census: every instruction writing ds:0x48c33 (a3/c7 05/89 /66 c7) and every
write to [reg+0x14] near 0x4850c initialisation. Payload scan only.
"""
import re
import sys

PAY = "work/ascend_payload.bin"
data = open(PAY, "rb").read()

def find_all(needle, ctx=6):
    out, i = [], 0
    while True:
        j = data.find(needle, i)
        if j < 0:
            return out
        out.append(j)
        i = j + 1

# writes to absolute 0x48c33:
# A3 = mov moffs32, eax                -> a3 33 48 00 00
# C7 05 = mov moffs32, imm32           -> c7 05 33 48 00 00
# 89 /r with modrm mod=00 rm=100 disp32 (SIB) OR mod=00 rm=101(disp32)=EB/EC/..
# simplest broad: any '33 48 00 00' occurrence, filtered by preceding opcode
hits = find_all(bytes.fromhex("33480000"))
print("occurrences of '33 48 00 00':", len(hits))
for h in hits:
    lo = max(0, h - 4)
    print(f"  file {h:#x} ctx: {data[lo:h+4].hex()}")

# writes to absolute 0x4850c
hits = find_all(bytes.fromhex("0c854000"))
print("occurrences of '0c 85 40 00':", len(hits))
for h in hits[:20]:
    lo = max(0, h - 4)
    print(f"  file {h:#x} ctx: {data[lo:h+4].hex()}")
