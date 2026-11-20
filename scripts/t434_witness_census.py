#!/usr/bin/env python3
"""t434 witness census: fleet row INK/SELECTION law on our own render.

Checks the t407 witness pair (t434b correction F1: ink lives at y62..83, NOT
the y56..76 window first assumed, and the selected row's ink is WHITE BY LAW,
so green must be censused on the POST-DESELECT shot):
  1. fleet-final.png (row deselected): NAME band (x159..268, y62..84) carries
     pal-ink green family (G>R+40 & G>B+40); LOCATION band (x389..560,
     y62..84) same; NO (0,200,220)-cyan pixels anywhere in the bands.
  2. fleet-rows.png (row 0 selected): row-0 name band carries WHITE pixels
     (R,G,B all >200) — the 0xf3 selected-override law.
Exit 0 iff both legs pass.
"""
import os
import sys
import numpy as np
from PIL import Image

DIR = os.path.dirname(sys.argv[1]) if len(sys.argv) > 1 else "/tmp/t434_shots"
SEL = os.path.join(DIR, "fleet-rows.png")    # row 0 SELECTED -> white law
UNSEL = os.path.join(DIR, "fleet-final.png")  # deselected -> race-ink green
a_sel = np.asarray(Image.open(SEL).convert("RGB")).astype(int)
a = np.asarray(Image.open(UNSEL).convert("RGB")).astype(int)
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
INK0, INK1 = 10, 32  # ink y-window within a row (row0 top 52 -> y62..84)
name_green = loc_green = cyan = 0
for r in range(4):
    y = rows_top + r * pitch
    if y + INK1 > a.shape[0]:
        break
    name_green += greenish(band(y + INK0, y + INK1, 159, 268))
    loc_green += greenish(band(y + INK0, y + INK1, 389, 560))
    for x0, x1 in ((159, 268), (389, 560)):
        cyan += cyanish(band(y + INK0, y + INK1, x0, x1))
print(f"name_green_px={name_green} loc_green_px={loc_green} cyan_px={cyan}")
# Green is only EXPECTED on rows with ships; the seed-5 sitting may hold one
# ship total. Leg 1 = "some green-family ink, zero cyan" across the page.
if name_green + loc_green < 30:
    print("FAIL  no green-family race ink on the deselected shot"); ok = False
if cyan > 0:
    print("FAIL  cyan location pixels remain (pre-t434 defect)"); ok = False
# selection leg: row 0 was selected on the fleet-rows.png shot
w0 = whiteish(a_sel[rows_top + INK0:rows_top + INK1, 159:268])
print(f"row0_white_px={w0}")
if w0 < 10:
    print("FAIL  selected row-0 name band has no WHITE (0xf3 law)"); ok = False
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
