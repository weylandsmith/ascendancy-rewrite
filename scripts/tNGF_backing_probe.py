#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tNG-F F2: species-list backing census, vendor vs ours.

Sample the list-interior NON-portrait zones (four corners of the list rect,
gaps between circles at mid-x) in both images; report exact colours. The
user D20 says ours is MISSING a black backing the vendor has.
"""
import sys
import numpy as np
from PIL import Image

PTS = {
    "corner TL": (512, 46), "corner TR": (626, 46),
    "corner BL": (512, 366), "corner BR": (626, 366),
    "gap1 mid": (514, 118), "gap1 right": (624, 118),
    "gap2 mid": (514, 244), "gap2 right": (624, 244),
    "between-top left": (516, 90),
}

def probe(path, name):
    im = np.array(Image.open(path).convert("RGB")).astype(int)
    print(f"== {name} {path}")
    for k, (x, y) in PTS.items():
        # 3x3 median
        z = im[y - 1:y + 2, x - 1:x + 2].reshape(-1, 3)
        med = np.median(z, axis=0).astype(int)
        print(f"   {k:20s} ({x},{y}) rgb={tuple(med)}")

probe("scratchpad/newgame-original.png", "VENDOR")
for p in sys.argv[1:]:
    probe(p, "OURS")
