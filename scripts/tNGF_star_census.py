#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tNG-F F1: vendor refcap starfield colour + radial census vs ours.

D20 F1: "stars are all one color, and they don't appear to be contained
within a volumetric sphere". Measures INSIDE the field rect (chrome-free)
in both images: colour-family histogram of star pixels, radial profile
about the centroid (containment signature: disk => r90/rmax ~ 1 with
rounded cutoff; rect-fill => rmax hugs the corner), and the fitted disk
radius (median radius = near-face disk proxy).
"""
import sys
from collections import Counter
import numpy as np
from PIL import Image

T = 90          # luminance-sum threshold for "star pixel"
FIELD = (8, 8, 372, 358)   # cosmos field interior (refcap: right edge
                           # before desc text; ours same rect)


def classify(p):
    r, g, b = int(p[0]), int(p[1]), int(p[2])
    if r > 150 and g > 150 and b > 150:
        return "white"
    if b >= r and b > g and (b - r) > 20 and b > 60:
        return "blue"
    if (r - b) > 20 and r > 60:
        return "warm"
    if g >= r and g > b and g > 60:
        return "green"
    return "dim"


def census(path, name, field=FIELD):
    im = np.array(Image.open(path).convert("RGB")).astype(int)
    x0, y0, x1, y1 = field
    reg = im[y0:y1 + 1, x0:x1 + 1]
    lum = reg.sum(axis=2)
    mask = lum > T
    ys, xs = np.nonzero(mask)
    px = reg[mask]
    print(f"== {name} {path} field={field}")
    print(f"   star px: {mask.sum()} of {mask.size}")
    if mask.sum() == 0:
        return {}
    c = Counter(classify(p) for p in px)
    tot = sum(c.values())
    print("   colour classes:", {k: f"{v} ({100*v/tot:.0f}%)" for k, v in c.most_common()})
    cx, cy = xs.mean(), ys.mean()
    r = np.hypot(xs - cx, ys - cy)
    print(f"   centroid=({cx:.1f},{cy:.1f}) rmax={r.max():.0f} "
          f"r50={np.percentile(r,50):.0f} r90={np.percentile(r,90):.0f} "
          f"r99={np.percentile(r,99):.0f}")
    nbins = 12
    hist, edges = np.histogram(r, bins=nbins, range=(0, r.max() if r.max() else 1))
    print("   radial hist:", [f"{int(e)}:{int(h)}" for e, h in zip(edges, hist)])
    # corner test: star px inside the 4 corner 40x40 boxes (rect-fill => many)
    h = y1 - y0
    w = x1 - x0
    corners = 0
    for (a, b) in [(0, 0), (0, h - 40), (w - 40, 0), (w - 40, h - 40)]:
        sub = mask[b:b + 40, a:a + 40]
        corners += int(sub.sum())
    print(f"   corner-px (4x40x40): {corners}")
    # per-star colour samples: connected-ish bright px colours
    bright = px[px.sum(axis=1) > 200]
    q = Counter(tuple(p) for p in bright)
    print("   top bright exact colours:", q.most_common(12))
    return {"r50": float(np.percentile(r, 50)), "r90": float(np.percentile(r, 90)),
            "classes": dict(c), "n": int(mask.sum())}


if __name__ == "__main__":
    census("scratchpad/newgame-original.png", "VENDOR refcap")
    for p in sys.argv[1:]:
        census(p, "OURS")
