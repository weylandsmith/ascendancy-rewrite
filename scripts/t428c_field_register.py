#!/usr/bin/env python3
"""t428c field-backdrop registration: does 17np k4/k5 register in witness B?

Witness B = work/r1/screens/t254/02_planet_detail.png (800x600, screen origin
(80,100): png = screen + (80,100)). Records = decoded index planes from
tools/shp_pngdump (work/r1/shp_png/t428c/raw/17np--{4,5}.idx), colours via
game.pal 6-bit scaled (t188 law).

For each record: exhaustive offset scan of LIT pixels only; report best
offset + hit count. CONTROLS: (1) colour-shuffle (geometry kept, pairing
killed) at the best offset x5 seeds; (2) fresh-array random-offset search
(rebuilt arrays, no reuse of scan state) to confirm the peak is the global
optimum and its height is consistent.

Exit 0 always (measurement script)."""
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOL = 8

pal = np.fromfile(os.path.join(ROOT, "extracted/ascend01/data/game.pal"),
                  dtype=np.uint8).reshape(256, 3).astype(np.int32)
scaled = (pal * 255) // 63
W = np.array(Image.open(os.path.join(ROOT, "work/r1/screens/t254/"
                   "02_planet_detail.png")).convert("RGB"), dtype=np.int32)
Hh, Ww, _ = W.shape


def hits(ys, xs, c, ox, oy):
    yy = ys + oy
    xx = xs + ox
    ok = (yy >= 0) & (yy < Hh) & (xx >= 0) & (xx < Ww)
    d = np.abs(W[yy[ok], xx[ok]] - scaled[c[ok]]).max(1)
    return int((d <= TOL).sum()), int(ok.sum())


def full_scan(name, rec):
    kimg = np.fromfile(os.path.join(ROOT, "work/r1/shp_png/t428c/raw",
                                    f"17np--{rec}.idx"),
                       dtype=np.uint8).reshape(*RECSIZE[rec])
    ys, xs = np.nonzero(kimg)
    c = kimg[ys, xs]
    best = (-1, None)
    for oy in range(-kimg.shape[0] + 10, Hh - 10):
        yy = ys + oy
        oky = (yy >= 0) & (yy < Hh)
        if oky.sum() * 10 < len(ys):
            continue
        for ox in range(-kimg.shape[1] + 10, Ww - 10):
            h, n = hits(ys[oky], xs[oky], c[oky], ox, oy)
            if n * 10 < len(ys):
                continue
            if h > best[0]:
                best = (h, (ox, oy))
    h, (ox, oy) = best
    print(f"{name}: lit={len(ys)} best={h} ({100*h/len(ys):.1f}%) at png offset ({ox},{oy}) = screen ({ox-80},{oy-100})")
    rng = np.random.default_rng(7)
    shuf = []
    for _ in range(5):
        p = rng.permutation(len(c))
        shuf.append(hits(ys, xs, c[p], ox, oy)[0])
    print(f"{name}: colour-shuffle control at best offset: {shuf} (pairing {'REAL' if max(shuf) < h/2 else 'INCONCLUSIVE'})")
    # fresh-array random search (independent rebuild)
    kimg2 = np.fromfile(os.path.join(ROOT, "work/r1/shp_png/t428c/raw",
                                     f"17np--{rec}.idx"),
                        dtype=np.uint8).reshape(*RECSIZE[rec])
    ys2, xs2 = np.nonzero(kimg2)
    c2 = kimg2[ys2, xs2]
    rbest = (-1, None)
    for _ in range(120000):
        o_x = int(rng.integers(-600, 750))
        o_y = int(rng.integers(-300, 550))
        h, n = hits(ys2, xs2, c2, o_x, o_y)
        if n * 10 < len(ys2):
            continue
        if h > rbest[0]:
            rbest = (h, (o_x, o_y))
    print(f"{name}: fresh-array random 120k-offset best={rbest[0]} at {rbest[1]}"
          f" (background must stay < {h}/2: {'PASS' if rbest[0] < h/2 else 'FAIL'}"
          f"; a sharp peak NOT recurring at random offsets is expected)")


RECSIZE = {4: (357, 625), 5: (316, 416)}
full_scan("k4", 4)
full_scan("k5", 5)
