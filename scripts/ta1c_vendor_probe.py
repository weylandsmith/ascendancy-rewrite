#!/usr/bin/env python3
"""tA1-CONT probe: vendor drawn-dims witnesses (newgame + planets-list).
Run with ~/tools/revenv/bin/python."""
import sys
from PIL import Image
import numpy as np

NGSRC = sys.argv[1] if len(sys.argv) > 1 else 'scratchpad/newgame-original.png'
PLSRC = sys.argv[2] if len(sys.argv) > 2 else 'work/r1/loop/vendor-planetslist-t3-640.png'

NG = np.array(Image.open(NGSRC).convert('RGB'))
if NG.shape[0] > 480:  # 643x481 browser shot -> game rect (+1,+1)
    NG = NG[1:481, 1:641]
PL = np.array(Image.open(PLSRC).convert('RGB'))
if PL.shape[:2] != (480, 640):
    PL = PL[100:580, 80:720]

def bbox_of(mask, x0, y0):
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    return (x0 + int(xs.min()), y0 + int(ys.min()), x0 + int(xs.max()),
            y0 + int(ys.max()), int(mask.sum()))

def dims(bb):
    return None if bb is None else (bb[2] - bb[0] + 1, bb[3] - bb[1] + 1)

def chroma(g):
    return g.max(axis=2) - g.min(axis=2)

print("== NEWGAME vendor (640x480 mapped)")
for cy in (107, 215, 323):
    reg = NG[cy - 55:cy + 56, 559 - 56:559 + 56]
    gr = reg.max(axis=2) - reg.min(axis=2)
    grey = (gr < 25) & (reg.max(axis=2) >= 35) & (reg.max(axis=2) <= 186)
    ch = chroma(reg) > 35
    bb = bbox_of(ch, 559 - 56, cy - 55)
    print(f"row y{cy}: ring-grey px {int(grey.sum())}, portrait chroma bbox {bb} dims {dims(bb)}")

reg = NG[97 - 56:97 + 56, 409 - 56:409 + 56]
green = ((np.abs(reg[:, :, 1].astype(int) - 142) <= 45) &
         (reg[:, :, 0].astype(int) < 90) &
         (reg[:, :, 2].astype(int) > 30) & (reg[:, :, 2].astype(int) < 130))
bb = bbox_of(green, 409 - 56, 97 - 56)
print("DESC green ring bbox:", bb, "dims", dims(bb))

reg = NG[97 - 52:97 + 53, 409 - 52:409 + 53]
bb = bbox_of(chroma(reg) > 35, 409 - 52, 97 - 52)
print("DESC portrait chroma bbox:", bb, "dims", dims(bb))

reg = NG[218 - 24:218 + 25, 401 - 24:401 + 25]
bb = bbox_of(chroma(reg) > 30, 401 - 24, 218 - 24)
print("DESC planet chroma bbox:", bb, "dims", dims(bb))

print("== PLANETS-LIST vendor t3 (640x480)")
reg = PL[121 - 70:121 + 70, 80 - 72:80 + 72]
warm = ((reg[:, :, 0].astype(int) > reg[:, :, 1].astype(int) + 25) &
        (reg[:, :, 1].astype(int) >= reg[:, :, 2].astype(int) - 10))
bb = bbox_of(warm, 80 - 72, 121 - 70)
print("sun warm bbox:", bb, "dims", dims(bb))

reg = PL[110 - 28:110 + 29, 215 - 28:215 + 29]
bb = bbox_of(chroma(reg) > 30, 215 - 28, 110 - 28)
print("planet chroma bbox:", bb, "dims", dims(bb))
