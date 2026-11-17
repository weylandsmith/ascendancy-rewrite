#!/usr/bin/env python3
# t418b witness census (run with ~/tools/revenv/bin/python — numpy lives
# there). Checks on planet-open.png / planet-tile.png:
#  1. tile fill pal[150] present with diamond geometry (sample grid points)
#  2. disc art: a cluster of non-black NON-fill pixels behind the grid
#  3. structure sprite: the home-CB tile carries non-fill art pixels
#  4. planet-tile.png carries WHITE outline pixels absent from planet-open
import sys
import numpy as np
from PIL import Image

OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/t418b_shots"
ok = True


def load(name):
    return np.array(Image.open(f"{OUT}/{name}.png").convert("RGB"))


open_im = load("planet-open")
tile_im = load("planet-tile")

# ---- 1. tile fill census: every valid-cell centre must carry the fill ----
B = [[0,0,0,0,4,4,5,0,0,0,0,0,0,0,0],
     [0,0,0,4,3,4,5,6,0,0,0,0,0,0,0],
     [0,0,3,2,3,3,4,5,7,0,0,0,0,0,0],
     [0,2,1,1,2,2,3,4,5,7,0,0,0,0,0],
     [1,0,0,0,1,1,2,3,4,5,7,0,0,0,0]]
C = [[0,0,0,0,2,3,2,0,0,0,0,0,0,0,0],
     [0,0,0,1,3,3,3,1,0,0,0,0,0,0,0],
     [0,0,1,4,4,5,4,4,1,0,0,0,0,0,0],
     [0,2,5,6,6,7,6,6,5,2,0,0,0,0,0],
     [3,6,7,8,8,9,8,8,7,6,3,0,0,0,0]]
# The shot is the seed-5 home planet; identify its size by which class's
# centres all carry the fill (sample the CORNER cells, structure-free).
fills = []
for s in range(5):
    pts = []
    for r in range(15):
        for c in range(B[s][r], B[s][r] + C[s][r]):
            pts.append((410 - 34 * r + 17 * c, 110 + 17 * r + 34 * c))
    cols = [open_im[y, x] for y, x in pts if 0 <= y < 480 and 0 <= x < 640]
    cols = np.array(cols)
    uniq, cnt = np.unique(cols, axis=0, return_counts=True)
    fills.append((s, len(pts), uniq[np.argmax(cnt)], cnt.max()))
for s, n, top, tc in fills:
    print(f"size {s}: {n} centres, modal {top} x{tc} ({100*tc/n:.0f}%)")
# the planet's size class = the one whose modal fill covers >=70% of centres
# (structures cover a few; rock cells differ)
size = max(fills, key=lambda f: f[3] / f[1])[0]
fill = fills[size][2].astype(int)
frac = fills[size][3] / fills[size][1]
print(f"planet size class = {size}, fill {fill}, centre-frac {frac:.2f}")
if frac < 0.6:
    print("FAIL tile fill census"); ok = False

# ---- 2. disc art behind the grid: non-black non-fill pixels --------------
reg = open_im[240:430, 180:560].astype(int)
d_fill = np.abs(reg - fill).sum(axis=2)
d_blk = reg.sum(axis=2)
mask = (d_fill > 60) & (d_blk > 90)
ys, xs = np.nonzero(mask)
print("non-fill bright px in grid window:", len(xs))
if len(xs) < 400:
    print("FAIL disc/structure art census (too few pixels)"); ok = False
else:
    print("disc art bbox x", xs.min() + 180, xs.max() + 180,
          "y", ys.min() + 240, ys.max() + 240)

# ---- 3. selection outline: white pixels appear only after the click ------
def white_count(im):
    w = (im[:, :, 0] > 240) & (im[:, :, 1] > 240) & (im[:, :, 2] > 240)
    # restrict to the grid window (text rows are y<200)
    return int(w[240:440, 150:600].sum())


w0, w1 = white_count(open_im), white_count(tile_im)
print("white px grid window: open", w0, "tile-selected", w1)
if w1 <= w0 + 40:  # the 4 diamond edges ~ >130 px
    print("FAIL selection outline census"); ok = False

print("VERDICT", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
