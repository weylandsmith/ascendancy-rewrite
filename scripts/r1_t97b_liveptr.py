#!/usr/bin/env python3
"""t97b: relocated-imm census for the SO block in LIVE RAM.
Static-image census (pool-rel form 0x62b0..0x63a0, alignment-checked
against objdump decode boundaries) found ONLY 0x1dae6. This tool repeats
the census against the RELOCATED value P0+0x88e60..P0+0x88f28 across all
guest RAM of a slot, so any pointer into the block that the loader wrote
(anywhere, incl. data/BSS) is caught. Self-validates via find_base vote +
SO block bytes at B+0x88e60. RC=0 always if a slot self-checks."""
import sys, zipfile
sys.path.insert(0, '/home/hrethric/projects/ascendancy/scripts')
from r1_sav_scan import build_anchors, find_base

PAY = '/home/hrethric/projects/ascendancy/work/ascend_payload.bin'
SAVS = ['/home/hrethric/projects/ascendancy/work/r1/playcap/save/60.sav']
pay = open(PAY, 'rb').read()
anch = build_anchors(pay)
import struct
for p in SAVS:
    mem = zipfile.ZipFile(p).read('Memory')
    votes, _ = find_base(mem, anch)
    B = votes.most_common(1)[0][0]
    blk = mem[B+0x88e60: B+0x88f28]
    if blk[:9] != b'SONothing':
        print('self-check FAIL', p); sys.exit(1)
    # P0 = B + 0x82bb0 (member index of data-intra 0). Relocated ptr values:
    P0 = B + 0x82bb0
    lo, hi = P0 + 0x88e60, P0 + 0x88f28
    print('slot', p, 'B', hex(B), 'P0', hex(P0), 'target', hex(lo), '..', hex(hi))
    hits = []
    i = 0
    while len(hits) < 60:
        j = mem.find((lo).to_bytes(4, 'little'), i)
        if j < 0: break
        hits.append(j); i = j + 1
    # any u32 in RAM within [lo,hi): single pass over byte-aligned offsets
    allhits = []
    try:
        import numpy as np
        # phase 0:
        u0 = np.frombuffer(mem[:len(mem)//4*4], dtype='<u4').astype(np.int64)
        m0 = np.where((u0 >= lo) & (u0 < hi))[0]
        for i in m0: allhits.append((hex(int(u0[i])), hex(int(i)*4)))
        # unaligned phases (rare; cheap strided)
        for ph in (1,2,3):
            tail = mem[ph: ph + (len(mem)-ph)//4*4]
            up = np.frombuffer(tail, dtype='<u4').astype(np.int64)
            mp = np.where((up >= lo) & (up < hi))[0]
            for i in mp: allhits.append((hex(int(up[i])), hex(int(i)*4+ph)))
    except ImportError:
        for k in range(0, len(mem)-4):
            v = int.from_bytes(mem[k:k+4],'little')
            if lo <= v < hi:
                allhits.append((hex(v),hex(k)))
                if len(allhits)>200: break
    print('u32-into-block occurrences (relocated form):', len(allhits))
    for v, k in allhits[:60]:
        # classify: is k-0x88 a code site? code member range = B+0x14bb0? code obj
        print(' val', v, 'at member', k, '(guest phys', hex(int(k,16)-0x88), ')')
print('RC 0')
