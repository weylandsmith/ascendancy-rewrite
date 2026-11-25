#!/usr/bin/env python3
"""tPF-3c TPF3-B probe: inventory class-colour pixel DENSITY per vendor
planet capture, before looking at any image.

Claim under test (docs/re/_wip_tPF3.md F6): at the refcap state the polygon
filler 0x62d15 paints the SAME colour as the tile base (no-op): interiors are
EXACTLY conv(pal 150) teal, zero class-blend px. The F6 census measured the
433 refcap (teal-class planet). This probe asks whether ANY banked capture
shows red/green/blue CLASS cell interiors (a non-teal cell) that could
falsify the no-op, and counts px per colour family per image.

Class line colours (F9 verbatim): 0 black / 117 red / 146 green / 255 blue /
12 white. A class-colour INTERIOR would be a solid region of the same palette
index, so the honest discriminator is run AREA, not raw count: outline px are
thin (1px), interiors are 2D blobs. Report per image: count, and the max
square-blob side (count of a 5x5 all-class window) per colour.
"""
import os, sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAL = open(os.path.join(ROOT, "extracted/ascend01/data/game.pal"), "rb").read()

def conv(i):
    r, g, b = PAL[3 * i], PAL[3 * i + 1], PAL[3 * i + 2]
    return np.array([(r << 2) | (r >> 4), (g << 2) | (g >> 4), (b << 2) | (b >> 4)], dtype=np.int16)

TOL = 12
NAMES = {"white": 12, "red": 117, "green": 146, "blue": 255, "teal150": 150, "black": 0}

def max_blob_side(m, k=5):
    """largest k-eroded extent: number of all-True kxk windows (interior px)."""
    h, w = m.shape
    if h < k or w < k:
        return 0
    ii = m.astype(np.int32)
    # integral image
    S = np.zeros((h + 1, w + 1), dtype=np.int64)
    S[1:, 1:] = np.cumsum(np.cumsum(ii, axis=0), axis=1)
    win = S[k:, k:] - S[:-k, k:] - S[k:, :-k] + S[:-k, :-k]
    return int((win == k * k).sum())

def main():
    imgs = sys.argv[1:] or [
        "scratchpad/original-planet-screen-build-list.png",
        "scratchpad/original-planet-screen-click-on-square-adjacent-to-structure.png",
        "scratchpad/original-planet-screen-popup-after-clicking-non-adjacent-square.png",
        "scratchpad/planet-screen-iter-433-v-original.png",
        "scratchpad/planets-screen-original.png",
        "work/r1/screens/t254/02_planet_detail.png",
    ]
    for p in imgs:
        path = p if os.path.isabs(p) else os.path.join(ROOT, p)
        im = np.asarray(Image.open(path).convert("RGB")).astype(np.int16)
        h, w, _ = im.shape
        print(f"{p}  {w}x{h}")
        for name, idx in NAMES.items():
            c = conv(idx)
            m = ((np.abs(im[:, :, 0] - c[0]) <= TOL) &
                 (np.abs(im[:, :, 1] - c[1]) <= TOL) &
                 (np.abs(im[:, :, 2] - c[2]) <= TOL))
            n = int(m.sum())
            if n:
                ys, xs = np.nonzero(m)
                print(f"    {name:8s} px={n:7d} bbox=({xs.min()},{ys.min()})-({xs.max()},{ys.max()}) interior5x5={max_blob_side(m)}")

if __name__ == "__main__":
    main()
