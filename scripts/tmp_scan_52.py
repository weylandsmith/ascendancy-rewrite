"""Scan restored code for stores/loads of planet-record offsets +0x52
(queue slot index) and +0x54 (pending item id), decoding 32-bit modrm
displacements properly. Operand-base guesses aside, the disp value is the
record offset when base is the planet-record pointer."""
import re, sys

d = open("work/ascend_restored.bin", "rb").read()
CODE = 0x82bb0

# opcode prefixes we care about: 66 (16-bit op) then 89 store r/m, 8b load r/m,
# C7 store imm; also plain 88/88C6 byte, C6 byte-imm.
def scan():
    hits = {"store+0x52": [], "store+0x54": [], "load+0x52": [], "load+0x54": []}
    i = 0
    while i < CODE - 6:
        o = d[i]
        pre = 0
        if o == 0x66:
            pre = 1
            o = d[i + 1]
        if o not in (0x89, 0x8b, 0x88, 0x8a, 0xc7, 0xc6):
            i += 1
            continue
        modrm = d[i + pre + 1]
        mod = modrm >> 6
        rm = modrm & 7
        disp = None
        length = 0
        if mod == 0 and rm == 5:          # disp32 (absolute-ish)
            disp = int.from_bytes(d[i + pre + 2:i + pre + 6], "little")
            length = 6 + pre
        elif mod == 1:                    # disp8
            disp = struct_i8(d[i + pre + 2])
            length = 3 + pre
        elif mod == 2:                    # disp32
            disp = int.from_bytes(d[i + pre + 2:i + pre + 6], "little")
            length = 6 + pre
        if disp is not None and disp in (0x52, 0x54):
            kind = ("store" if o in (0x89, 0x88, 0xc7, 0xc6) else "load")
            hits[f"{kind}+0x{disp:02x}"].append(hex(i))
        i += max(1, length)
    return hits

def struct_i8(b):
    return b - 256 if b > 127 else b

hits = scan()
for k, v in sorted(hits.items()):
    print(f"{k:12s} {len(v):3d}  {v[:30]}")
