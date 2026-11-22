#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tNG-F F2/F3 refcap probes: species-box backing + scroll-arrow glyph zone."""
import numpy as np
from PIL import Image

im = np.array(Image.open("scratchpad/newgame-original.png").convert("RGB")).astype(int)

def zone(name, x0, y0, x1, y1):
    z = im[y0:y1 + 1, x0:x1 + 1]
    lum = z.sum(axis=2)
    black = (lum < 30).mean()
    print(f"{name:24s} ({x0},{y0})-({x1},{y1}) black<30: {100*black:.1f}% "
          f"mean={z.reshape(-1,3).mean(axis=0).astype(int)}")

zone("species list interior", 508, 42, 630, 370)
zone("species header band", 500, 8, 636, 38)
zone("big field corner TL", 10, 10, 60, 60)
zone("desc panel interior", 380, 50, 470, 150)
zone("arrow up zone", 618, 40, 638, 62)
zone("arrow down zone", 618, 348, 638, 372)
print("--- arrow-up glyph ascii (x616..639 rows 40..62) ---")
z = im[40:63, 616:640]
for y in range(23):
    print("".join("." if z[y, x].sum() < 120 else
                  ("#" if z[y, x].sum() > 500 else "+") for x in range(24)))
print("--- arrow-up colours (unique bright) ---")
from collections import Counter
c = Counter(tuple(z[y, x]) for y in range(23) for x in range(24) if z[y, x].sum() > 200)
print(c.most_common(10))
