#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tNG-F F4/F5: Begin panel refcap facts.
(a) COLOURED star px (sat>25, not green-ring family) bbox + radial fit vs the
    panel rect — is the vendor field a circle, and where?
(b) green ring inner hole vs portrait content bbox (centre + radius).
"""
import numpy as np
from PIL import Image

im = np.array(Image.open("scratchpad/newgame-original.png").convert("RGB")).astype(int)

# (a) coloured star px in panel band x503..570 y382..471
z = im[381:472, 502:633]
sat = z.max(axis=2) - z.min(axis=2)
r, g, b = z[:, :, 0], z[:, :, 1], z[:, :, 2]
green = (g > r + 30) * (g > b + 20) * (g > 90)          # ring family
col = (sat > 25) * ~green
ys, xs = np.nonzero(col)
print(f"coloured px {len(ys)}; x {xs.min()+502}..{xs.max()+502} "
      f"y {ys.min()+381}..{ys.max()+381}")
cx, cy = xs.mean() + 502, ys.mean() + 381
rr = np.hypot(xs + 502 - cx, ys + 381 - cy)
print(f"centroid ({cx:.1f},{cy:.1f}) r50={np.percentile(rr,50):.0f} "
      f"r90={np.percentile(rr,90):.0f} rmax={rr.max():.0f}")
hist, edges = np.histogram(rr, bins=10, range=(0, rr.max() if len(rr) else 1))
print("radial:", [f"{int(e)}:{int(h)}" for e, h in zip(edges, hist)])

# (b) ring hole: green px annulus extents at x=600 and y=417/418
colv = im[381:472, 600]
gv = np.nonzero((colv[:, 1] > colv[:, 0] + 30) * (colv[:, 1] > 90))[0] + 381
print("green rows @x600:", gv.tolist())
rowh = im[418, 560:640]
gh = np.nonzero((rowh[:, 1] > rowh[:, 0] + 30) * (rowh[:, 1] > 90))[0] + 560
print("green cols @y418:", gh.tolist())

# portrait content inside hole: non-black, non-green px within r<23 of (600,417.5)
yy, xx = np.mgrid[388:448, 570:631]
d = np.hypot(xx - 600.0, yy - 417.5)
sub = im[388:448, 570:631]
lum = sub.sum(axis=2)
content = (d < 23) * (lum > 60)
ys2, xs2 = np.nonzero(content)
print(f"portrait content px {content.sum()} bbox x {xs2.min()+570}..{xs2.max()+570} "
      f"y {ys2.min()+388}..{ys2.max()+388}; centre "
      f"({xs2.mean()+570:.1f},{ys2.mean()+388:.1f})")
