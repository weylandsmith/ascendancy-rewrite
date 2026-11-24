#!/usr/bin/env python3
"""tPL-V1f census DIAGNOSIS (not the verdict script): where are the class
edge pixels, is the +0.5 shared-edge probe landing on vertices, and which
size-1 centre misses the fill?"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
from tplv1_lattice_witness import load_rgb, conv, EDGE_RGB

SHOT = os.environ.get("SHOT", "/tmp/tplv1_shots_f1/planet-open.png")
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

w, h, px = load_rgb(SHOT)
def at(x, y):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < w and 0 <= y < h:
        b = (y * w + x) * 3
        return (px[b], px[b+1], px[b+2])
    return None

fill = conv(150)
print("shot", SHOT, w, h, "fill", fill)

# 1) class-1 (white) edge pixels: bounding box + distance to nearest diamond
#    edge of a size-1 cell (should be ~0 if they ARE the lattice outlines)
import math
cells1 = [(r, c) for r in range(15) for c in range(B[1][r], B[1][r]+C[1][r])]
def seg_d(px_, py_, x0, y0, x1, y1):
    dx, dy = x1-x0, y1-y0
    t = max(0.0, min(1.0, ((px_-x0)*dx + (py_-y0)*dy) / (dx*dx+dy*dy)))
    return math.hypot(px_-(x0+t*dx), py_-(y0+t*dy))
def cell_edge_d(cx, cy, x_, y):
    return min(seg_d(x_, y, cx-34, cy, cx, cy-17), seg_d(x_, y, cx, cy-17, cx+34, cy),
               seg_d(x_, y, cx+34, cy, cx, cy+17), seg_d(x_, y, cx, cy+17, cx-34, cy))
white = conv(12)
wpix = [(i % w, i // w) for i in range(w*h)
        if all(abs(px[3*i+k]-white[k]) <= 14 for k in range(3))]
print("white-ish px total:", len(wpix))
near0 = 0
for (x_, y) in wpix:
    d = min(cell_edge_d(410+34*(c-r), 127+17*(c+r), x_, y) for (r, c) in cells1)
    if d <= 2.0: near0 += 1
print(f"white px within 2px of a size-1 lattice edge: {near0}/{len(wpix)}")

# 2) shared-edge probe: old (17,+8) vs corrected (+8.5 -> 9) vs segment-any
print("\ncell                 old+8  y9   seg(-15..15@x+17)  fill@centre")
for (r, c) in cells1:
    cx, cy = 410+34*(c-r), 127+17*(c+r)
    old = at(cx+17, cy+8); y9 = at(cx+17, cy+9)
    seg = [at(cx+17, cy+8+t/2) for t in range(-30, 31)]  # y 8..23 half-steps... keep simple
    segok = any(p and not all(v < 12 for v in p) for p in
                [at(cx+17, cy+8+j) for j in range(0, 4)])
    p = at(cx, cy)
    fillhit = p and all(abs(p[k]-fill[k]) <= 14 for k in range(3))
    print(f"({r:2d},{c:2d}) c=({cx:3d},{cy:3d}) {str(old):>16} {str(y9):>16}  {segok}   {bool(fillhit)}  centre={p}")

# 3) what colour is the missing fill centre?
print("\nnon-fill centres listed above (fillhit False)")
