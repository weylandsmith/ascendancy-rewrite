#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tNG-F F1: test the UNIFIED-FIELD hypothesis.

Static facts (banked _wip_tNGF F1-M2/M3): the stride-0xd preview table
(DAT_0003067e, circle r300 law) has EXACTLY ONE referrer (its generator
FUN_00022728) — nothing paints it. The state-3 painter body 0x526b4 draws
the big field AND the Begin panel with the SAME record walk: pos =
hiword[rec+3]/5+5, hiword[rec+5]/5+5 (shrunk map), sprite SEL = 4*K + cls
with K = dword[rec+0] (star TYPE, 13-valued), cls = four-way band.
=> Prediction: the big preview field and the Begin panel show the SAME
star set (identical relative pattern, scale 1.0, offset by the panel
origin). Test: star-px centroid patterns in both refcap images.
"""
import sys
import numpy as np
from PIL import Image

def stars(path, rect, T=90, chroma=0):
    im = np.array(Image.open(path).convert("RGB")).astype(int)
    x0, y0, x1, y1 = rect
    reg = im[y0:y1+1, x0:x1+1]
    lum = reg.sum(axis=2)
    sat = reg.max(axis=2) - reg.min(axis=2)
    mask = (lum > T) & (sat > chroma)
    ys, xs = np.nonzero(mask)
    return np.stack([xs, ys], axis=1) + np.array([x0, y0])

def main():
    a = sys.argv[1] if len(sys.argv) > 1 else "scratchpad/newgame-original.png"
    b = sys.argv[2] if len(sys.argv) > 2 else "scratchpad/newgame-original.png"
    big = stars(a, (8, 8, 372, 300), chroma=25)       # avoid summary text rows
    pan = stars(b, (503, 381, 570, 471), chroma=25)   # begin panel left band
    print("big px", len(big), "panel px", len(pan))
    # centroid of each
    print("big centroid", big.mean(axis=0), "panel centroid", pan.mean(axis=0))
    # match: for each panel px, nearest big px distance under translation
    # candidate translation = centroid diff; then chi: fraction of panel px
    # with a big px within 2 px
    d = pan.mean(axis=0) - big.mean(axis=0)
    ok = 0
    for (px, py) in pan[::3]:
        dd = np.abs(big - (np.array([px, py]) - d)).max(axis=1).min()
        if dd <= 2:
            ok += 1
    print(f"translation {d}: matched {ok}/{len(pan[::3])} "
          f"({100*ok/max(1,len(pan[::3])):.0f}%)")

if __name__ == "__main__":
    main()
