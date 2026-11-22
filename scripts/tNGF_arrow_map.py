#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tNG-F F3: dump the vendor UP-arrow cell x616..631 y47..63 as a colour map,
classifying each px into families so the port can replicate the glyph."""
import numpy as np
from PIL import Image
from collections import Counter

im = np.array(Image.open("scratchpad/newgame-original.png").convert("RGB")).astype(int)
z = im[47:64, 615:633]
FAMS = {
    "K": (0, 0, 0),
    "N": (12, 32, 48),   # navy well
    "D": (34, 60, 74),   # dark slate frame
    "M": (79, 116, 126), # mid slate
    "C": (123, 171, 177),# cyan body
    "B": (168, 227, 229),# bright cyan
    "W": (190, 255, 255),# highlight
}

def fam(p):
    best, bd = "?", 1e9
    for k, c in FAMS.items():
        d = sum((int(p[i]) - c[i]) ** 2 for i in range(3))
        if d < bd:
            best, bd = k, d
    return best if bd < 2600 else "?"

for y in range(z.shape[0]):
    print(f"y{47+y:3d}", "".join(fam(z[y, x]) for x in range(z.shape[1])))
print()
c = Counter(tuple(z[y, x]) for y in range(z.shape[0]) for x in range(z.shape[1]))
print("exact:", c.most_common(14))
# down arrow mirrored
z2 = im[356:373, 615:633]
print("--- DOWN ---")
for y in range(z2.shape[0]):
    print(f"y{356+y:3d}", "".join(fam(z2[y, x]) for x in range(z2.shape[1])))
