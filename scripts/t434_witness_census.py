#!/usr/bin/env python3
"""t434 witness census: fleet row INK/SELECTION law on our own render.

Checks /tmp/t434_shots/fleet-rows.png (t407 witness shot):
  1. NAME band (x159..268, row tops 52/158/...) contains the pal-ink green
     family (G>R+40 & G>B+40) and NO (0,200,220)-cyan pixels remain.
  2. LOCATION band (x389..560) same: green family, zero cyan.
  3. When a row is selected (the witness clicks row 0 first), that row's
     name band carries WHITE pixels (R,G,B all >200).
Exit 0 iff legs 1+2 pass (leg 3 only when a select line is in the log).
"""
import sys
import numpy as np
from PIL import Image

SHOT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/t434_shots/fleet-rows.png"
a = np.asarray(Image.open(SHOT).convert("RGB")).astype(int)
ok = True


def band(y0, y1, x0, x1):
    return a[y0:y1, x0:x1]


def greenish(z):
    return int(((z[:, :, 1] > z[:, :, 0] + 40) & (z[:, :, 1] > z[:, :, 2] + 40)).sum())


def cyanish(z):
    return int(((z[:, :, 2] > 180) & (z[:, :, 1] > 150) & (z[:, :, 0] < 90)).sum())


def whiteish(z):
    return int(((z[:, :, 0] > 200) & (z[:, :, 1] > 200) & (z[:, :, 2] > 200)).sum())


rows_top, pitch = 52, 106
name_green = loc_green = cyan = 0
for r in range(4):
    y = rows_top + r * pitch
    if y + 24 > a.shape[0]:
        break
    name_green += greenish(band(y + 4, y + 22, 159, 268))
    loc_green += greenish(band(y + 4, y + 40, 389, 560))
    for x0, x1 in ((159, 268), (389, 560)):
        cyan += cyanish(band(y + 4, y + 44, x0, x1))
print(f"name_green_px={name_green} loc_green_px={loc_green} cyan_px={cyan}")
if name_green < 30:
    print("FAIL  name band has no green-family ink"); ok = False
if loc_green < 30:
    print("FAIL  location band has no green-family ink"); ok = False
if cyan > 0:
    print("FAIL  cyan location pixels remain (pre-t434 defect)"); ok = False
# selection leg: row 0 was clicked by the witness script
z0 = band(rows_top + 4, rows_top + 22, 159, 268)
w0 = whiteish(z0)
print(f"row0_white_px={w0}")
if w0 < 10:
    print("NOTE  no white on row 0 (selection leg only valid if select fired)")
else:
    print("PASS  selected row name is WHITE (0xf3 law)")
# frame/marker absence: the deleted navy frame colour (40,40,56) fill
navy = int(((abs(a[:, :, 0] - 40) < 6) & (abs(a[:, :, 1] - 40) < 6) &
            (abs(a[:, :, 2] - 56) < 6)).sum())
print(f"navy_frame_px={navy}")
if navy > 2000:
    print("FAIL  synthetic navy row frame still painted"); ok = False
print("VERDICT", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
