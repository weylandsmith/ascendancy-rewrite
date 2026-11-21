#!/usr/bin/env python3
"""tA2-CONT band census probe: mean-lum + family mass on OUR 1:1 render and
the vendor browser crop, for the four chrome-band regions. Used to set the
t441_screen_diff band thresholds (windows cited from _wip_tA2 F3/F5)."""
import sys
import numpy as np
from PIL import Image

def load640(p):
    im = np.array(Image.open(p).convert("RGB"))
    if im.shape[:2] == (480, 640):
        return im
    if im.shape[0] == 481 and im.shape[1] == 643:
        return im[1:481, 1:641]
    raise SystemExit(f"{p}: {im.shape} not 640x480/643x481")

BANDS = {
    "topbar-rows0-6":  ("row", list(range(0, 7)), 7, 493),
    "recess-row7":     ("row", [7], 7, 493),
    "ridge-row373":    ("row", [373], 7, 493),
    "ridge-row374":    ("row", [374], 7, 493),
    "panel-top-row381": ("row", [381], 7, 493),
}
FAMS = {
    "ridge-row373": [(61,61,61),(53,78,78),(48,71,73)],
    "ridge-row374": [(97,97,97),(85,125,125),(77,113,117)],
    "recess-row7":  [(24,24,24),(10,10,10),(21,42,35)],
    "panel-top-row381": [(12,24,34),(12,24,36),(18,31,40)],
}

def report(tag, im):
    for name, (kind, rows, lo, hi) in BANDS.items():
        px = im[rows[0]:rows[-1]+1, lo:hi+1].reshape(-1,3).astype(int)
        lum = px.mean(axis=1)
        line = f"{tag} {name:<17} n={len(px):<5} mean={lum.mean():6.1f}"
        if name in FAMS:
            tot = 0
            for f in FAMS[name]:
                d = np.abs(px - np.array(f)).sum(axis=1)
                tot += int((d <= 30).sum())  # <=10/channel
            line += f" fam3frac={tot/len(px):.3f}"
        print(line)

ours = load640(sys.argv[1])
vendor = load640(sys.argv[2])
report("OURS  ", ours)
report("VENDOR", vendor)
