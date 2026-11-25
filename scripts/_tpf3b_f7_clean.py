#!/usr/bin/env python3
"""tPF-3b F7 clean probe: is the FULL diamond boundary special at +-2 px?

Uses the witness's OWN scorer (any-hit-per-segment, 8 integer samples, TOL=12)
so the numbers are directly comparable to its published 100.0%. The lattice is
fixed at the witness's law-B fit (size class 0, dx=-23, dy=48) and ONLY the
perpendicular offset of the drawn geometry varies.

Perpendicular pitch of the tPL-V1 lattice = |det|/|edge| = 1156/38.0789 =
30.36 logical px, so offsets of 8/15 px are FAR from any lattice line and are
honest controls (the earlier (6,3)/(0,4) "controls" were along-edge or
near-edge and therefore meaningless).

Geometry variants (half-extents (a,b) of the diamond whose outline is scored):
  FULL   (34,17)  -> the tPL-V1 boundary
  INSET  (32,16)  -> the vendor's LEGAL branch (0x3bc5b: y+1, x-2, y-1, x+2)
  TINY   ( 6, 3)  -> the vendor's ILLEGAL branch (0x3bd4d: y+14, x-28, y-14, x+28)
For each variant, sweep the perpendicular offset o in -4..+4 px along the
outward normal. A variant whose lines lie ON the vendor's drawn lines peaks at
the offset where its own geometry coincides with them.
"""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tplv1_lattice_witness as W

w, h, px = W.load_rgb(W.PNG)
ox, oy = W.ORIGIN
mask = bytearray(w * h)
for i in range(w * h):
    r, g, b = px[3 * i], px[3 * i + 1], px[3 * i + 2]
    for c, rgb in W.EDGE_RGB.items():
        if abs(r - rgb[0]) <= W.TOL and abs(g - rgb[1]) <= W.TOL and abs(b - rgb[2]) <= W.TOL:
            if c != 0:
                mask[i] = 1 + c
            break

S, DX, DY = 0, -23, 48
B, C = W.B, W.C
cells = [(row, col) for row in range(15)
         for col in range(B[S][row], B[S][row] + C[S][row])]

# outward unit normals of the four diamond edges (a,b)=(34,17)
NORMS = [(2 * 34, 34) , ]
def edges(a, b):
    return ((-a, 0, 0, -b), (0, -b, a, 0), (a, 0, 0, b), (0, b, -a, 0))

def normals(a, b):
    out = []
    for (x0, y0, x1, y1) in edges(a, b):
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy)
        nx, ny = dy / L, -dx / L          # one side
        # OUTWARD = away from the centre (0,0): sign so that n . midpoint > 0
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        if nx * mx + ny * my < 0:
            nx, ny = -nx, -ny
        out.append((nx, ny))
    return out

def score(a, b, o):
    hit = tot = 0
    ns = normals(a, b)
    for k, (row, col) in enumerate(cells):
        cx, cy = 410 + 34 * (col - row) + DX, 127 + 17 * (col + row) + DY
        for ei, (x0, y0, x1, y1) in enumerate(edges(a, b)):
            nx, ny = ns[ei]
            oxo, oyo = nx * o, ny * o
            got = False
            for t in range(8):
                sx = ox + int(round(cx + x0 + (x1 - x0) * t / 7 + oxo))
                sy = oy + int(round(cy + y0 + (y1 - y0) * t / 7 + oyo))
                if 0 <= sx < w and 0 <= sy < h and mask[sy * w + sx]:
                    got = True
            tot += 1
            if got:
                hit += 1
    return 100.0 * hit / tot

print(f"lattice size{S} dx{DX} dy{DY} cells={len(cells)}  "
      f"(witness published 100.0% at FULL o=0)")
pitch = 1156 / math.hypot(34, 17)
print(f"perpendicular pitch = {pitch:.2f} px; inset offset = 2/sqrt5 = "
      f"{2/math.sqrt(5):.3f} px\n")
print(f"{'variant':10s} " + " ".join(f"{o:+d}" for o in range(-4, 5)))
for name, (a, b) in (("FULL", (34, 17)), ("INSET", (32, 16)), ("TINY", (6, 3))):
    row = [score(a, b, o) for o in range(-4, 5)]
    print(f"{name:10s} " + " ".join(f"{v:4.0f}" for v in row))

# far-offset controls (mid-gap): score FULL at the gap centre
print(f"\ncontrol FULL at o=+{pitch/2:.1f} (mid-gap, no lattice line there): "
      f"{score(34,17, 15):.0f}%  / o=-15: {score(34,17,-15):.0f}%")
print("control FULL at o=+8: {:.0f}%  o=-8: {:.0f}%".format(score(34,17,8), score(34,17,-8)))
