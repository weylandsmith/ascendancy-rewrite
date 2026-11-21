#!/usr/bin/env python3
"""tNG-C3: cos_star k0..k8 palette census — what does each class sprite look
like (docs/re/_wip_tNGC.md F15-3)."""
import struct
import numpy as np

d = open('extracted/ascend01/data/cos_star.shp', 'rb').read()
count = struct.unpack_from("<I", d, 4)[0]
tsz = struct.unpack_from("<I", d, 8)[0]
te = 0x10 + tsz
starts = [te] + [struct.unpack_from("<Q", d, 0x10 + 8 * k)[0] for k in range(count - 1)]
pal = np.fromfile('extracted/ascend01/data/game.pal', dtype=np.uint8).reshape(256, 3).astype(int)
pal8 = (pal << 2) | (pal >> 4)

def decode(d, rec, W, H, limit, off):
    plane = np.full((H, W), -1, dtype=np.int16)
    i = rec + off
    for r in range(H):
        x = 0
        while i < limit:
            C = d[i]; i += 1
            if C == 0:
                break
            if C == 1:
                x += d[i]; i += 1
            elif C & 1:
                n = C >> 1
                for v in d[i:i + n]:
                    if x < W:
                        plane[r, x] = v
                    x += 1
                i += n
            else:
                n = C >> 1
                v = d[i]; i += 1
                for _ in range(n):
                    if x < W:
                        plane[r, x] = v
                    x += 1
    return plane

for k in range(0, 9):
    rec = starts[k]
    if k == 0:
        w, h = struct.unpack_from("<II", d, rec)
        off = 8
    else:
        w, h = struct.unpack_from("<II", d, rec + 0x10)
        off = 0x18
    plane = decode(d, rec, w, h, len(d), off)
    vals = sorted(set(int(v) for v in plane.flatten() if v >= 0))
    cols = {v: tuple(int(c) for c in pal8[v]) for v in vals}
    print(f"k{k} dims {w}x{h}: {cols}")
