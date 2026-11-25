#!/usr/bin/env python3
"""tPF-3b F7 DECISIVE PIXEL MEASUREMENT — signed distance of every edge-colour
pixel to the nearest FULL lattice boundary.

The earlier perpendicular-sweep attempt was NOT trustworthy: it sampled only 8
points per 38-px edge and the +-offset offsets rounded inconsistently along the
edge, producing a jagged profile (peaks at o=0 AND o=+3). This version uses
EVERY edge-colour pixel and exact line algebra — no sampling.

LATTICE (tPL-V1 law B, witness fit size class 0, dx=-23, dy=48, png origin
(80,100) per t428 F9):  centre = (410+34*(col-row), 127+17*(col+row)).

The two edge families are parallel-line sets (derived below, verified against
the fitted cell geometry in-code):
  family U: x + 2y = const,  const step 68 logical px  -> pitch 68/sqrt5 = 30.37
  family V: -x + 2y = const, const step 68
Perpendicular distance to a family line = |delta| / sqrt(5).

PREDICTIONS for the pixels the paint fn draws (work/tPF3b_inset.asm):
  FULL boundary line (hyp b)  -> distance peak at 0.00, width ~1 px
  INSET line  (0x3bc5b, hyp a/c) -> the two neighbours' inset lines sit
      2/sqrt5 = 0.894 px EITHER SIDE of the shared boundary -> a DOUBLEt at
      -0.894 / +0.894 with a DIP at 0
  TINY line   (0x3bd4d)       -> 12.52 px inside from the boundary
"""
import os, sys, math
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tplv1_lattice_witness as W

w, h, px = W.load_rgb(W.PNG)
ox, oy = W.ORIGIN
S, DX, DY = 0, -23, 48
B, C = W.B, W.C
cells = [(row, col) for row in range(15)
         for col in range(B[S][row], B[S][row] + C[S][row])]

def centre(row, col):
    return (410 + 34 * (col - row) + DX, 127 + 17 * (col + row) + DY)

# --- derive the family constants from the fitted lattice (no hand algebra) ---
uvals, vvals = set(), set()
for (row, col) in cells:
    cx, cy = centre(row, col)
    for (ax, ay, bx, by) in ((-34, 0, 0, -17), (0, -17, 34, 0),
                             (34, 0, 0, 17), (0, 17, -34, 0)):
        x0, y0 = cx + ax, cy + ay
        u = x0 + 2 * y0
        v = -x0 + 2 * y0
        # classify by which family this edge belongs to (families differ in
        # which of u/v is CONSTANT along the edge)
        u1, v1 = (cx + bx) + 2 * (cy + by), -(cx + bx) + 2 * (cy + by)
        if abs(u1 - u) < 1e-9:
            vvals.add(round(v))
        else:
            uvals.add(round(u))
us = sorted(uvals); vs = sorted(vvals)
print(f"family U constants (n={len(us)}): {us}")
print(f"family V constants (n={len(vs)}): {vs}")
def step(a):
    d = [a[i+1]-a[i] for i in range(len(a)-1)]
    return Counter(d).most_common(1)[0] if d else None
print(f"U step {step(us)}  V step {step(vs)}  (expect 68; pitch = 68/sqrt5 = "
      f"{68/math.sqrt(5):.2f} px)")

def nearest_dist(x, y):
    """signed perpendicular distance to the nearest full-boundary line, and
    which family; plus the distance to the nearest INSET line (boundary shifted
    2 units of u/v toward the owning cell => +-0.894 px from the boundary)."""
    u = x + 2 * y
    v = -x + 2 * y
    best = None
    for val, fam in ((u, us), (v, vs)):
        ds = [val - c for c in fam]
        d = min(ds, key=abs)
        # also the neighbouring lattice line on the other side of the pixel
        perp = abs(d) / math.sqrt(5)
        if best is None or perp < best[0]:
            best = (perp, d, fam is us and 'U' or 'V')
    return best

# --- collect edge-colour pixels inside the fitted field bbox ---
xs_all = [centre(r, c)[0] for (r, c) in cells]
ys_all = [centre(r, c)[1] for (r, c) in cells]
pad = 40
xlo, xhi = min(xs_all) - pad, max(xs_all) + pad
ylo, yhi = min(ys_all) - pad, max(ys_all) + pad
print(f"field bbox logical x{xlo:.0f}..{xhi:.0f} y{ylo:.0f}..{yhi:.0f}")

hist = Counter()
percls = {}
n = 0
for yy in range(h):
    ly = yy - oy
    base = yy * w * 3
    for xx in range(w):
        i = base + xx * 3
        r, g, b = px[i], px[i+1], px[i+2]
        hitc = None
        for c, rgb in W.EDGE_RGB.items():
            if abs(r-rgb[0]) <= W.TOL and abs(g-rgb[1]) <= W.TOL and abs(b-rgb[2]) <= W.TOL:
                hitc = c
                break
        if hitc is None or hitc == 0:
            continue                       # black is starfield-indistinguishable
        lx2 = xx - ox
        if not (xlo <= lx2 <= xhi and ylo <= ly <= yhi):
            continue
        n += 1
        perp, d, fam = nearest_dist(lx2, ly)
        hist[round(perp * 4) / 4] += 1     # 0.25 px bins
        percls.setdefault(hitc, Counter())[round(perp * 4) / 4] += 1
print(f"\nedge-colour px in field (non-black): {n}")
mx = max(hist.values()) if hist else 1
print("perpendicular distance to nearest FULL boundary (bin px: count):")
for k in sorted(hist):
    if k > 4.0:
        break
    print(f"   {k:4.2f}: {hist[k]:5d} {'#' * int(56 * hist[k] / mx)}")
band0 = sum(v for k, v in hist.items() if k < 0.5)
band1 = sum(v for k, v in hist.items() if 0.5 <= k < 1.3)
band2 = sum(v for k, v in hist.items() if 1.3 <= k < 2.5)
band3 = sum(v for k, v in hist.items() if 2.5 <= k <= 4.0)
print(f"\nband <0.50 px {band0} | 0.50..1.30 (inset prediction 0.894) {band1} | "
      f"1.30..2.50 {band2} | 2.50..4.00 {band3}")
print(f"fraction exactly-on-boundary (<0.5px) = {band0/max(n,1):.3f}; "
      f"inset-band fraction = {band1/max(n,1):.3f}")

print("\nPER-CLASS band summary (class pal idx: n, <0.5px on-boundary, 0.5-1.3 inset band, >1.3):")
for c, hh in sorted(percls.items()):
    tc = sum(hh.values())
    b0 = sum(v for k, v in hh.items() if k < 0.5)
    b1 = sum(v for k, v in hh.items() if 0.5 <= k < 1.3)
    b2 = tc - b0 - b1
    print(f"   pal{c:>3} n={tc:5d}  on-boundary {b0:5d} ({100*b0/max(tc,1):5.1f}%)  "
          f"inset-band {b1:5d} ({100*b1/max(tc,1):5.1f}%)  far {b2:5d} ({100*b2/max(tc,1):5.1f}%)")
for c, hh in sorted(percls.items()):
    if sum(hh.values()) < 50: continue
    m = max(hh.values())
    print(f"   pal{c} profile: " + " ".join(f"{k:.2f}:{hh[k]*56//m}" for k in sorted(hh) if k <= 3.0))
