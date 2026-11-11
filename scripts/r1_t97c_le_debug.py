#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t97c: WATCOM LE object-table re-parse (correct format: name strings AND
description strings inline) + debug-record scan of game/ascend.exe for any
u32/u16 referencing the SO name block.
LAW: ascend.exe is LE; restored-image FILE offset F maps to exe file offset
F+0x2a50 for the loaded image (verify empirically). The SO block sits at exe
file 0x8b8b0 == image FILE 0x88e60 (t94/t97 both verified byte-wise).
Goal: (a) object names = module vocabulary; (b) any debug record (ID Info /
nonresident names) that points AT the block base or its entries = the
symbol tie. RC=0 always if parse completes; prints NEGATIVE honestly."""
import struct

d = open('/home/hrethric/projects/ascendancy/game/ascend.exe', 'rb').read()
le = struct.unpack_from('<I', d, 0x3c)[0]
def W(o): return struct.unpack_from('<H', d, o)[0]
def DW(o): return struct.unpack_from('<I', d, o)[0]

# Empirical exe<->image delta: find image window bytes in exe
win = open('/home/hrethric/projects/ascendancy/work/ascend_restored.bin','rb').read(0x89000)[0x88e60:0x88f00]
j = d.find(win)
print('block found at exe file', hex(j), 'delta', hex(j-0x88e60))
DELTA = j - 0x88e60

nobj = W(le+0x2c); nseg = W(le+0x2e)
offObjTab = DW(le+0x30); offSegTab = DW(le+0x34)
nLNKT = W(le+0x48)
print('nobj', nobj, 'nseg', nseg, 'objTab', hex(offObjTab), 'nLNKT', nLNKT)

p = offObjTab
objs = []
ok = True
for k in range(nobj):
    try:
        ncnt = d[p]; dcnt = d[p+1]; p += 2
        strs = []
        for _ in range(ncnt + dcnt):
            L = d[p]; p += 1
            strs.append(d[p:p+L].decode(errors='replace')); p += L
        flags = W(p); p += 2
        nsegidx = W(p); p += 2
        p += 2*nsegidx
        # LNKT entries: size u16 + offset u32, terminated by size==0 (u16 only)
        lnk = []
        while True:
            sz = W(p)
            if sz == 0:
                p += 2; break
            off = DW(p+2); lnk.append((sz, off)); p += 6
        objs.append((k, strs, flags, lnk[:3]))
    except Exception as e:
        print('PARSE BREAK at obj', k, hex(p), e); ok = False; break
print('parsed objs:', len(objs), 'ok:', ok)
for k, strs, flags, lnk in objs[:60]:
    print(k, '|'.join(strs)[:60], hex(flags), [(s, hex(o)) for s, o in lnk])

# (b) scan whole exe for u32 == exe-file-offset-of-block OR image-linear forms.
# image loads at linear L0; runtime P0 varied. In the FILE, fixup-sites for the
# debug records may store offsets relative to LE data start. Try:
targets = {
    'exe foff of block': j,
    'image file off': 0x88e60,
    'pool-rel': 0x62b0,
}
for name, v in targets.items():
    hits = []
    i = 0
    b4 = v.to_bytes(4, 'little')
    while True:
        k2 = d.find(b4, i)
        if k2 < 0: break
        hits.append(hex(k2)); i = k2 + 1
        if len(hits) > 12: break
    print(f'u32=={name} ({hex(v)}):', hits or 'NONE')
print('RC 0')
