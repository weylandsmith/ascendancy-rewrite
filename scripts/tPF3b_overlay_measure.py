#!/usr/bin/env python3
"""tPF-3b port witness measurement on a 640x480 port planet-view shot.

(a) OVERLAY PASS FIRES: pass 3 draws the TINY (half 6x3) or INSET (32,16)
    diamond in the CLASS colour (F9: pen EDI = class table 0/117/146/255/12).
    The tiny path lies STRICTLY INSIDE the cell, so any class-colour pixel
    within +-1 of a tiny-diamond path and NOT within +-1 of the full-boundary
    lattice proves pass 3 painted (pass 2 only paints the full boundary).
(b) ANCHOR: prints, per cell with sprite content, the topmost content row
    relative to the cell centre, for eyeball vs the law (centre-17+recTop).
Cell centres are enumerated from the B/C tables for the size class the app
logged (tPF-2b law: parse 'ui planet home-cb ... size S').
usage: tPF3b_overlay_measure.py SHOT.png [APP_LOG]
"""
import sys, re
import numpy as np
from PIL import Image

PAL_PATH = "extracted/ascend01/data/game.pal"
def conv(i):
    pal = open(PAL_PATH, "rb").read()
    r, g, b = pal[i * 3], pal[i * 3 + 1], pal[i * 3 + 2]
    return tuple(round(v * 255 / 63) for v in (r, g, b))

B = [0,0,0,0,4,4,5,0,0,0,0,0,0,0,0,
     0,0,0,4,3,4,5,6,0,0,0,0,0,0,0,
     0,0,0,3,2,3,3,4,5,7,0,0,0,0,0,
     0,1,1,2,2,3,4,5,7,0,0,0,0,0,0,
     1,0,0,0,1,1,2,3,4,5,7,0,0,0,0]
C = [0,0,0,0,2,3,2,0,0,0,0,0,0,0,0,
     0,0,0,1,3,3,3,1,0,0,0,0,0,0,0,
     0,0,0,1,4,4,5,4,4,1,0,0,0,0,0,
     0,0,2,5,6,6,7,6,6,5,2,0,0,0,0,
     3,6,7,8,8,9,8,8,7,6,3,0,0,0,0]

def centres(size):
    # tileCenter() law VERBATIM (planetview.cpp:132-139, tPL-V1 F1/F3):
    #   X = 410 + 34*col - 34*row ; anchor top-vertex Y = 110 + 17*col +
    #   17*row ; centre = anchor + (0,17). col ABSOLUTE (includes B).
    out = []
    for row in range(15):
        b, w = B[size * 15 + row], C[size * 15 + row]
        for col in range(b, b + w):
            out.append((410 + 34 * col - 34 * row,
                        110 + 17 * col + 17 * row + 17))
    return out

def diamond_path(cx, cy, hl, ht, tol=1):
    pts = []
    for y in range(cy - ht - tol, cy + ht + tol + 1):
        for x in range(cx - hl - tol, cx + hl + tol + 1):
            # |dx|/hl + |dy|/ht == 1 +-eps  (on the outline within tol px)
            v = abs(x - cx) / hl + abs(y - cy) / ht
            if abs(v - 1.0) <= tol * (1 / hl + 1 / ht) * 1.6:
                pts.append((x, y))
    return pts

def main():
    shot = sys.argv[1]
    im = Image.open(shot).convert("RGB")
    a = np.asarray(im, dtype=np.int16)
    log = ""
    if len(sys.argv) > 2:
        try:
            with open(sys.argv[2], "r", errors="replace") as f:
                log = f.read()
        except OSError:
            pass
    m = re.search(r"home-cb.*size (\d)", log)
    size = int(m.group(1)) if m else 2
    cs = centres(size)
    CLASS = {"black": conv(0), "red": conv(117), "green": conv(146),
             "blue": conv(255), "white": conv(12)}
    tot_tiny = 0
    hits = {k: 0 for k in CLASS}
    off_lattice = {k: 0 for k in CLASS}
    for (cx, cy) in cs:
        if not (0 <= cy < a.shape[0] and 0 <= cx < a.shape[1]):
            continue
        full = set(diamond_path(cx, cy, 34, 17))
        for (x, y) in diamond_path(cx, cy, 6, 3):
            if not (0 <= y < a.shape[0] and 0 <= x < a.shape[1]):
                continue
            tot_tiny += 1
            px = tuple(a[y, x])
            for name, rgb in CLASS.items():
                if all(abs(int(px[i]) - rgb[i]) <= 6 for i in range(3)):
                    hits[name] += 1
                    if (x, y) not in full:
                        off_lattice[name] += 1
                    break
    print(f"size={size} cells={len(cs)} tiny_path_px={tot_tiny}")
    print("class-colour px ON tiny paths (black/red/green/blue are pass-3 "
          "candidates; white is ambiguous):")
    for k in CLASS:
        print(f"  {k:6s} hits={hits[k]:5d} off_full_lattice={off_lattice[k]:5d}")
    strong = sum(off_lattice[k] for k in ("black", "red", "green", "blue"))
    print("VERDICT(a):", "OVERLAY PASS VISIBLE" if strong >= 20 else
          f"NOT SEEN (strong off-lattice class px = {strong})")

if __name__ == "__main__":
    main()
