#!/usr/bin/env python3
"""tA1-CONT: cited-record dims + chroma census for the D19-family libs.
Parses .shp per the bbox-diff law (quad u16 @ stream-start-0x10, stream at
stream-start; k0 quad = dir slot 0 i.e. also @s+8). Prints per-record
WxH@(L,T) and mean chroma of decoded pixels (decode = S9 row-walk, colour
via game.pal + DOSBox conv per t417 law... simplified: index-plane chroma).
Run: ~/tools/revenv/bin/python scripts/ta1c_record_census.py [libs...]
"""
import struct, sys, os
import numpy as np

DATA = 'extracted/ascend01/data'
LIBS = sys.argv[1:] or ['suns.shp', 'planets.shp', 'smrace.shp', 'racering.shp', 'raceflag.shp']

def load_lib(path):
    d = open(path, 'rb').read()
    assert d[:4] == b'1.10', path
    count, tsz = struct.unpack('<II', d[4:12])
    starts = [0x10 + tsz]
    for j in range(1, count):
        starts.append(struct.unpack('<I', d[0x10 + (j - 1) * 8:0x14 + (j - 1) * 8])[0])
    starts.append(len(d))
    recs = []
    for k in range(count):
        s, e = starts[k], starts[k + 1]
        # port law (shp.cpp:164-183): stream = k0? rec+8 : rec+0x18;
        # bbox quad = 4 x i32 at stream-0x10
        sp = s + 8 if k == 0 else s + 0x18
        q = sp - 0x10
        if q < 0:
            recs.append((k, 0, 0, 0, 0, None)); continue
        L, T, R, B = struct.unpack('<4i', d[q:q + 16])
        W, H = R - L + 1, B - T + 1
        if W < 1 or H < 1 or sp >= len(d):
            recs.append((k, W, H, L, T, None))
            continue
        idx = decode(d, sp, W, H, e)
        recs.append((k, W, H, L, T, idx))
    return recs

def decode(d, sp, W, H, end):
    """Index-plane decode (S9 walk); returns uint8 WxH (0 = transparent)."""
    px = np.zeros((H, W), np.uint16)
    pos = sp
    for row in range(H):
        col = 0
        while pos < end:
            c = d[pos]; pos += 1
            if c == 0:
                break
            if c == 1:
                col += 1
                pos += 1
            elif c % 2:
                n = c >> 1
                run = np.frombuffer(d, np.uint8, n, pos)
                px[row, col:col + n] = run[:max(0, W - col)]
                col += n; pos += n
            else:
                n = c >> 1
                v = d[pos]; pos += 1
                px[row, col:col + n] = v
                col += n
    return px

def chroma_stats(idx):
    if idx is None:
        return -1
    nz = idx[idx > 0]
    return len(nz)

for lib in LIBS:
    p = os.path.join(DATA, lib)
    if not os.path.exists(p):
        print(f'{lib}: MISSING'); continue
    recs = load_lib(p)
    print(f'== {lib}: {len(recs)} records')
    for k, W, H, L, T, idx in recs:
        nz = chroma_stats(idx)
        print(f'  k{k:<3} {W}x{H}@({L},{T}) opaque {nz}')
