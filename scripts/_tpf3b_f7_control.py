#!/usr/bin/env python3
"""tPF-3b F7 control v2 — is the witness's 100% edge support VACUOUS?

WHY 100% IS NOT 28/2366-px luck: the witness's score() takes 8 INTEGER samples
per edge ((x1-x0)*t//7), and for the fitted lattice each edge's 8 samples
COLLAPSE onto a handful of distinct pixels (verified: hit=28 tot=28 for the 7
size-0 cells, oob=0). So the metric's power comes from the mask CONCENTRATING
on the lattice lines, not from raw density. This control measures both facts:

  leg1  the distinct-sample set for the fitted law-B geometry (power budget)
  leg2  real-mask score vs a DENSITY-MATCHED UNIFORM-SCATTERED mask
        (sampled uniformly over the field bbox, same pixel count as the real
        mask has inside that bbox) -> if scatter scores ~100% too, the metric
        is vacuous; if it scores ~0%, the real 100% is real signal.
  leg3  the INSET geometry's own sample set on the real mask (the competing
        hypothesis scored on the same pixels)
  leg4  TINY geometry (12x6) on the real mask
"""
import os, sys, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tplv1_lattice_witness as W

w, h, px = W.load_rgb(W.PNG)
ox, oy = W.ORIGIN
real = bytearray(w * h)
for i in range(w * h):
    r, g, b = px[3 * i], px[3 * i + 1], px[3 * i + 2]
    for c, rgb in W.EDGE_RGB.items():
        if abs(r - rgb[0]) <= W.TOL and abs(g - rgb[1]) <= W.TOL and abs(b - rgb[2]) <= W.TOL:
            if c != 0:
                real[i] = 1
            break

B, C = W.B, W.C
S, DX, DY = 0, -23, 48
cells = [(row, col) for row in range(15)
         for col in range(B[S][row], B[S][row] + C[S][row])]

def edges(a, b, dx, dy):
    """the witness's EXACT per-edge sample groups (score() breaks on the first
    hit within an edge, so the unit of scoring is an edge, not a pixel)."""
    out = []
    for (row, col) in cells:
        cx, cy = 410 + 34 * (col - row) + dx, 127 + 17 * (col + row) + dy
        for (x0, y0, x1, y1) in ((cx - a, cy, cx, cy - b), (cx, cy - b, cx + a, cy),
                                 (cx + a, cy, cx, cy + b), (cx, cy + b, cx - a, cy)):
            g = []
            for t in range(8):
                sx = ox + x0 + (x1 - x0) * t // 7
                sy = oy + y0 + (y1 - y0) * t // 7
                if 0 <= sx < w and 0 <= sy < h:
                    g.append((sx, sy))
            if g:
                out.append(g)
    return out

FULL_E, INSET_E, TINY_E = edges(34, 17, DX, DY), edges(32, 16, DX, DY), edges(6, 3, DX, DY)
FULL = {p for g in FULL_E for p in g}
INSET = {p for g in INSET_E for p in g}
TINY = {p for g in TINY_E for p in g}
print(f"leg1 distinct sample px: FULL {len(FULL)} INSET {len(INSET)} TINY {len(TINY)}")
print(f"     overlap FULL&INSET {len(FULL & INSET)}  FULL^INSET {len(FULL ^ INSET)}")
tot_real = sum(real[i // w + (i % w) * 0] for i in ())  # placeholder-free below
def score(E, mask):
    hit = sum(1 for g in E if any(mask[y * w + x] for (x, y) in g))
    return 100.0 * hit / len(E), hit

for nm, P in (("FULL", FULL_E), ("INSET", INSET_E), ("TINY", TINY_E)):
    pc, hit = score(P, real)
    print(f"leg1 {nm:5s} on real mask: {hit}/{len(P)} = {pc:.1f}%")

# --- leg2: density-matched uniform scatter over the field bbox ---
xs = [410 + 34 * (c - r) + DX for (r, c) in cells]
ys = [127 + 17 * (c + r) + DY for (r, c) in cells]
bx0, bx1 = ox + min(xs) - 34, ox + max(xs) + 34
by0, by1 = oy + min(ys) - 17, oy + max(ys) + 17
bx0, by0 = max(bx0, 0), max(by0, 0)
bx1, by1 = min(bx1, w - 1), min(by1, h - 1)
area = (bx1 - bx0 + 1) * (by1 - by0 + 1)
n_in = sum(1 for i in range(w * h) if real[i] and bx0 <= i % w <= bx1 and by0 <= i // w <= by1)
print(f"\nleg2 field bbox {bx0}..{bx1} x {by0}..{by1} area {area}  "
      f"real mask px inside {n_in} ({100*n_in/area:.1f}%)")
random.seed(20261125)
sc = []
for k in range(60):
    m = bytearray(w * h)
    flat = [by0 + (j // (bx1 - bx0 + 1)) * h + bx0 + j % (bx1 - bx0 + 1) for j in range(area)]
    for i in random.sample(flat, n_in):
        m[i] = 1
    sc.append(score(FULL_E, m)[0])
sc.sort()
print(f"leg2 density-matched SCATTER on FULL: min {sc[0]:.1f}% median "
      f"{sc[len(sc)//2]:.1f}% max {sc[-1]:.1f}%   vs REAL {score(FULL_E, real)[0]:.1f}%")
print(f"     => {'METRIC IS VACUOUS (scatter matches real)' if sc[len(sc)//2] > 70 else 'METRIC IS SHARP (real 100% is signal, scatter is not)'}")

# --- leg3/4 already printed in leg1; add the discriminative pair test ---
print(f"\nleg3/4 discriminative pixels (INSET hits FULL misses, and vice versa) "
      f"on the real mask:")
ionly = INSET - FULL
fonly = FULL - INSET
hi_ = sum(1 for (x, y) in ionly if real[y * w + x])
hf = sum(1 for (x, y) in fonly if real[y * w + x])
print(f"   INSET-only px {len(ionly)}: real hits {hi_}")
print(f"   FULL-only  px {len(fonly)}: real hits {hf}")
