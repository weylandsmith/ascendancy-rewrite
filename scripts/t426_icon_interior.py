#!/usr/bin/env python3
"""t426 probe 2b: the UPPER-LEFT object strictly INSIDE COSMOSWnd.

probe 2 (t426_corner_icon.py) cropped from screen (2,2) and so swallowed the
chrome band (rows 0..6 / cols 0..6 are texture, not the object). This probe
crops strictly inside the window interior (screen rows/cols >= 8) and prints
the object's exact extent, luminance ASCII, and palette histogram on the
vendor scale round(v*255/63).

Read-only; exit 0.
"""
import collections

import numpy as np
from PIL import Image

PAL = open("extracted/ascend01/data/game.pal", "rb").read()
conv = [(round(PAL[3*i]*255/63), round(PAL[3*i+1]*255/63),
         round(PAL[3*i+2]*255/63)) for i in range(256)]


def lab(c):
    for i, cc in enumerate(conv):
        if all(abs(cc[k] - int(c[k])) <= 1 for k in range(3)):
            return "idx%d" % i
    return "OFF%s" % (tuple(int(v) for v in c),)


ref = np.asarray(Image.open(
    "docs/assets/refcap/original-strategic-map.png").convert("RGB")).astype(int)

# COSMOSWnd interior: screen 7,7..465,472; chrome occupies rows 0..6/cols 0..6.
# Scan a generous interior box so the object cannot be clipped by the crop.
R0, C0 = 8, 8
zone = ref[R0:70, C0:70]
nz = zone.sum(axis=2) > 0
ys, xs = np.nonzero(nz)
print("interior non-black extent screen rows %d..%d cols %d..%d"
      % (ys.min()+R0, ys.max()+R0, xs.min()+C0, xs.max()+C0))

print("ASCII screen rows %d..%d x cols %d..%d ('.'=black '-'<=150 '+'<=380 '#')"
      % (R0, 69, C0, 69))
for r in range(zone.shape[0]):
    line = ""
    for c in range(zone.shape[1]):
        s = int(zone[r, c].sum())
        line += "." if s == 0 else ("#" if s > 380 else ("+" if s > 150 else "-"))
    print("%3d %s" % (r+R0, line))

hist = collections.Counter(map(tuple, zone.reshape(-1, 3)))
print("histogram (non-black only):")
for c, n in hist.most_common(12):
    if sum(c) == 0:
        continue
    print("   %-6s %s x%d" % (lab(c), tuple(int(v) for v in c), n))
