#!/usr/bin/env python3
"""tA1 DIMS LAW census over the whole .shp corpus.

Candidate laws per record k (stream start sp):
  A (port current): k==0 dims u32@rec+0 sp=rec+8 ; k>=1 dims u32@rec+16 sp=rec+0x18
  B (bbox u16):     L,T,R,B = signed u16 @ rec+8..0xf ; W=R-L+1 H=B-T+1 ; sp=rec+0x18
Acceptance = EXACT-span walk (the standing discriminator): the S9 row-walk
with (W,H) must consume EXACTLY [sp, span_end) -- delta==0.
Reports per-library tallies; a law must win 100% per library to be the law.
"""
import glob, struct, sys

def walk(d, sp, W, H, end):
    pos = sp
    for row in range(H):
        while True:
            if pos >= end + 4096 or pos >= len(d):
                return False
            c = d[pos]; pos += 1
            if c == 0:
                break
            if c == 1:
                pos += 1
            elif c % 2:
                pos += c >> 1
            else:
                pos += 1
    return pos == end

files = sorted(glob.glob('extracted/ascend01/data/*.shp'))
tot = {'A': 0, 'B': 0, 'none': 0, 'skip': 0}
per = {}
for f in files:
    d = open(f, 'rb').read()
    if len(d) < 0x10 or d[:4] != b'1.10':
        continue
    count, tsz = struct.unpack('<II', d[4:12])
    if 8 * (count + 1) != tsz:
        continue
    starts = [0x10 + tsz]
    for j in range(1, count):
        starts.append(struct.unpack('<I', d[0x10 + (j-1)*8:0x14 + (j-1)*8])[0])
    starts.append(len(d))
    a = b = n = sk = 0
    for k in range(count):
        s, e = starts[k], starts[k+1]
        if e <= s or s >= len(d):
            sk += 1
            continue
        okA = False
        d_off = s if k == 0 else s + 0x10
        spA = s + 8 if k == 0 else s + 0x18
        if d_off + 8 <= len(d):
            W, H = struct.unpack('<II', d[d_off:d_off+8])
            if 2 <= W <= 4096 and 2 <= H <= 4096 and spA < len(d):
                okA = walk(d, spA, W, H, e)
        okB = False
        if s + 16 <= len(d):
            L, T, R, Bm = struct.unpack('<4h', d[s+8:s+16])
            Wb, Hb = R - L + 1, Bm - T + 1
            if 2 <= Wb <= 4096 and 2 <= Hb <= 4096 and s + 0x18 < len(d):
                okB = walk(d, s + 0x18, Wb, Hb, e)
        if okA:
            a += 1
        elif okB:
            b += 1
        else:
            n += 1
    per[f.split('/')[-1]] = (a, b, n, sk, count)
    tot['A'] += a
    tot['B'] += b
    tot['none'] += n
    tot['skip'] += sk

b_libs = [k for k, v in per.items() if v[1] > 0]
a_only = [k for k, v in per.items() if v[1] == 0]
print(f"libraries={len(per)} A_exact={tot['A']} B_exact={tot['B']} none={tot['none']} skip={tot['skip']}")
print(f"B-winning libs ({len(b_libs)}):", ' '.join(b_libs))
print(f"A-only libs ({len(a_only)})")
for k in a_only[:60]:
    v = per[k]
    print(f"  {k}: A={v[0]} none={v[2]} count={v[4]}")
