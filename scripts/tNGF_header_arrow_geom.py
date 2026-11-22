#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tNG-F F2/F3: exact geometry of (a) the black header backing behind
'Player Species' (rows 0..45, x495..640) and (b) the scroll-arrow glyphs
in the vendor refcap. Outputs bounding boxes + colour census.
"""
import numpy as np
from PIL import Image
from collections import Counter

im = np.array(Image.open("scratchpad/newgame-original.png").convert("RGB")).astype(int)

# --- (a) black backing bbox in top-right header zone
z = im[0:46, 494:640]
black = z.sum(axis=2) < 30
ys, xs = np.nonzero(black)
print(f"header black px {len(ys)}; bbox x {xs.min()+494}..{xs.max()+494} "
      f"y {ys.min()}..{ys.max()}")
# column coverage: which x columns have >50% black over rows 5..38
col = black[5:39].mean(axis=0)
runs = [(x + 494) for x in range(len(col)) if col[x] > 0.5]
print("cols >50% black:", runs[:5], "...", runs[-5:] if runs else [], f"n={len(runs)}")
row = black[:, 10:130].mean(axis=1)
print("rows >30% black (x504..624):", [y for y in range(46) if row[y] > 0.3])
# exact fill colour inside the black box away from text
print("sample colours inside box rows 30..36 x510..520:",
      Counter(tuple(im[y, x]) for y in range(30, 37) for x in range(510, 521)).most_common(5))

# --- (b) arrow glyph geometry: bright cyan px in right-edge strips
def arrow(name, y0, y1):
    strip = im[y0:y1, 616:640]
    bright = (strip.max(axis=2) > 200) & (strip[:, :, 2] > strip[:, :, 0])
    ys, xs = np.nonzero(bright)
    if len(ys) == 0:
        print(name, "none")
        return
    print(f"{name}: bright cyan px {len(ys)} bbox x {xs.min()+616}..{xs.max()+616} "
          f"y {ys.min()+y0}..{ys.max()+y0}")
    # glyph shape rows
    for y in range(ys.min(), ys.max() + 1):
        row = "".join("#" if bright[y - y0, x] else "." for x in range(xs.min(), xs.max() + 1))
        print(f"   y={y+y0:3d} {row}")
arrow("UP", 38, 70)
arrow("DOWN", 340, 375)
# groove colours around the arrow
print("groove colours left of arrow (x618..624 rows 44..60):",
      Counter(tuple(im[y, x]) for y in range(44, 61) for x in range(617, 624)).most_common(6))
