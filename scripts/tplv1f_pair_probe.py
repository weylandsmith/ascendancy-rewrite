#!/usr/bin/env python3
"""tPL-V1f probe 2: VALIDATE the corrected adjacency census before rewriting
tplv1_port_census.py. For every adjacent PAIR of valid size-1 cells probe:
  own-side inside  = shared-edge midpoint + 3px toward OWN centre
  nb-side inside   = midpoint + 3px toward NEIGHBOUR centre
  exact midpoint   = must carry own/nb class edge colour OR black (class 0)
Gap (old transposed law) would show BLACK on an inside probe."""
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
SIZE = 1
w, h, px = load_rgb(SHOT)
def at(x, y):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < w and 0 <= y < h:
        b = (y * w + x) * 3
        return (px[b], px[b+1], px[b+2])
    return None
fill = conv(150)
def is_fill(p): return p and all(abs(p[k]-fill[k]) <= 14 for k in range(3))
def is_black(p): return p and all(v < 12 for v in p)
valid = {(r, c) for r in range(15) for c in range(B[SIZE][r], B[SIZE][r]+C[SIZE][r])}
def centre(r, c): return (410 + 34*(c-r), 127 + 17*(c+r))

pairs = []
for (r, c) in sorted(valid):
    for (dr, dc) in ((0, 1), (-1, 0)):   # right-down edge, up-right edge
        n = (r+dr, c+dc)
        if n in valid:
            pairs.append(((r, c), n))
print(f"valid cells {len(valid)}, adjacent pairs {len(pairs)}")
bad = 0
for (a, n) in pairs:
    ax, ay = centre(*a); nx, ny = centre(*n)
    mx, my = (ax+nx)/2, (ay+ny)/2
    ux, uy = (ax-mx), (ay-my); un = (ux*ux+uy*uy) ** 0.5
    ox_, oy_ = mx + 3*ux/un, my + 3*uy/un
    vx, vy_ = mx - 3*ux/un, my - 3*uy/un
    po, pn, pm = at(ox_, oy_), at(vx, vy_), at(mx, my)
    okside = (is_fill(po) or not is_black(po)) and (is_fill(pn) or not is_black(pn))
    # midpoint: own/nb edge colour or black (class-0 law draws black edges)
    edgeok = is_black(pm) or any(
        all(abs(pm[k]-EDGE_RGB[cidx][k]) <= 14 for k in range(3))
        for cidx in (1, 2, 3, 4)) if pm else False
    flag = "OK " if (okside and edgeok) else "BAD"
    if flag == "BAD": bad += 1
    print(f"{flag} {a}->{n} mid=({mx:.0f},{my:.0f}) own={po} nb={pn} mid={pm}")
print("pairs BAD:", bad)
