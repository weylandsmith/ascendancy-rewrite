#!/usr/bin/env python3
"""t428e k5 origin test: does 17np record 5 register at the clip-rect-derived
candidate origins in witness B?

Asm (work/t198_planwin.asm 0x3c7bc..0x3c82d, docs/re/_wip_t428e.md E1/E3): the
planet paint body blits 17np record 5 behind a PLANLIST-widget gate, with a
clip struct {112, ?, 528} (528-112 = 416 = k5 width). windows.txt ln1503-1512:
PLANLIST rect X0 120 Y0 120 X1 520 Y1 420; PLANETALLOC (parent, ln1486) is the
full-screen 0,0..639,479 window, so child rects are screen coords.

This script only MEASURES hit counts at named candidate origins (no scan) plus
a narrow +/-40 refinement around the best, so the peak shape is visible.
Exit 0 always (measurement script)."""
import os

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

kimg = np.fromfile(os.path.join(ROOT, "work/r1/shp_png/t428c/raw/17np--5.idx"),
                   dtype=np.uint8).reshape(316, 416)
ys, xs = np.nonzero(kimg)
c = kimg[ys, xs]


def hits(ox, oy):
    yy = ys + oy
    xx = xs + ox
    ok = (yy >= 0) & (yy < Hh) & (xx >= 0) & (xx < Ww)
    d = np.abs(W[yy[ok], xx[ok]] - scaled[c[ok]]).max(1)
    return int((d <= TOL).sum()), int(ok.sum())


# png = screen + (80,100) (t428c law), so a shape painted at screen (sx,sy)
# has its top-left at png offset (sx+80, sy+100).
CAND = {
    "clipx0+PLANLIST(112,120)": (112 + 80, 120 + 100),
    "PLANLIST-rect(120,120)":   (120 + 80, 120 + 100),
    "t428c-peak(224,107)":      (224 + 80, 107 + 100),
    "blit2(408,296)":           (408 + 80, 296 + 100),
    "origin(0,0)":              (80, 100),
    "field-blit1(7,115)":       (7 + 80, 115 + 100),
}
res = {}
for name, (ox, oy) in CAND.items():
    h, n = hits(ox, oy)
    res[name] = h
    print(f"{name:26s} png({ox},{oy}) hits={h:5d}/{len(ys)} "
          f"({100*h/len(ys):5.2f}%) onscreen={n}")

best = max(res, key=lambda k: res[k])
box = CAND[best]
print(f"\nrefinement +/-40 around {best}:")
grid = {}
for dy in range(-40, 41, 4):
    row = []
    for dx in range(-40, 41, 4):
        row.append(hits(box[0] + dx, box[1] + dy)[0])
    grid[dy] = row
top = sorted(((v, dy, dx) for dy, r in grid.items() for dx, v in zip(range(-40, 41, 4), r)), reverse=True)[:5]
for v, dy, dx in top:
    h, _ = hits(box[0] + dx, box[1] + dy)
    print(f"  screen ({box[0]+dx-80},{box[1]+dy-100}) hits={h}")

rng = np.random.default_rng(11)
perm_best = []
for _ in range(5):
    p = rng.permutation(len(c))
    yy = ys + box[1]; xx = xs + box[0]
    ok = (yy >= 0) & (yy < Hh) & (xx >= 0) & (xx < Ww)
    d = np.abs(W[yy[ok], xx[ok]] - scaled[c[p][ok]]).max(1)
    perm_best.append(int((d <= TOL).sum()))
print(f"\ncolour-permute control at best: {perm_best}")
