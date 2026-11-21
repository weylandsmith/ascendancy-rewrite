#!/usr/bin/env python3
"""tNG-C3 wheel pixel decode — render 3cfgnew k10/k11/k12 planes via the
shp.h S9 codec + game.pal, and compare rows against our live render to
locate the lens-band artifact (docs/re/_wip_tNGC.md F15-1)."""
import struct
import numpy as np
from PIL import Image

P = "extracted/ascend01/data/3cfgnew.shp"

def parse(p):
    d = open(p, "rb").read()
    count = struct.unpack_from("<I", d, 4)[0]
    tsz = struct.unpack_from("<I", d, 8)[0]
    te = 0x10 + tsz
    starts = [te] + [struct.unpack_from("<Q", d, 0x10 + 8 * k)[0] for k in range(count - 1)]
    ends = starts[1:] + [len(d)]
    return d, count, starts, ends

def decode(d, rec, W, H, limit):
    """S9 walk into a W x H plane; -1 = untouched (transparent skip).
    Writes clamp at W (position still advances)."""
    plane = np.full((H, W), -1, dtype=np.int16)
    i = rec + 0x18
    for r in range(H):
        x = 0
        while i < limit:
            C = d[i]; i += 1
            if C == 0: break
            if C == 1:
                x += d[i]; i += 1
            elif C & 1:
                n = C >> 1
                for v in d[i:i+n]:
                    if x < W: plane[r, x] = v
                    x += 1
                i += n
            else:
                n = C >> 1
                v = d[i]; i += 1
                for _ in range(n):
                    if x < W: plane[r, x] = v
                    x += 1
    return plane

d, count, starts, ends = parse(P)
pal = np.fromfile("extracted/ascend01/data/game.pal", dtype=np.uint8).reshape(256,3).astype(int)
pal8 = (pal << 2) | (pal >> 4)

print("palette probes:", {i: tuple(pal8[i]) for i in (48,54,57,58,59,60,98,103,117,151,189,190,196,199,200,251,252,254)})

for k in (10, 11, 12):
    a, b = struct.unpack_from("<II", d, starts[k] + 0x10)
    plane = decode(d, starts[k], a, b, len(d))
    # rows 20..32 palette values, unique runs
    print(f"\n== k{k} plane {a}x{b}")
    for r in range(20, 33):
        row = plane[r]
        s = ''.join('.' if v < 0 else str(min(int(v) % 10, 9)) for v in row)
        vals = sorted(set(int(v) for v in row if v >= 0))
        print(f" r{r}: {s} vals={vals}")
