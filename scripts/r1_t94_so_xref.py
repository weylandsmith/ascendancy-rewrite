#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t94 helper: census imm references to the SO order-name block and its
runtime copy destination, plus every u32 in the restored image pointing into
the block. R12 file law: work/ascend_restored.bin."""
import struct

data = open('/home/hrethric/projects/ascendancy/work/ascend_restored.bin', 'rb').read()
CODE = (0x14bb0, 0x82bb0)

def imm_scan(v, label):
    pat = v.to_bytes(4, 'little')
    hits = []
    i = CODE[0]
    while True:
        j = data.find(pat, i)
        if j < 0 or j >= CODE[1]:
            break
        hits.append(j)
        i = j + 1
    print(label, hex(v), [hex(h) for h in hits])

imm_scan(0x88e60, 'SOblock_base')
imm_scan(0x7d382, 'DAT7d382')
imm_scan(0x7d38a, 'DAT7d38a')

print('--- u32 anywhere pointing into SO block 0x88e60..0x88f00 ---')
for off in range(0, len(data) - 4):
    v = struct.unpack_from('<I', data, off)[0]
    if 0x88e60 <= v < 0x88f00:
        print(hex(off), '->', hex(v))
