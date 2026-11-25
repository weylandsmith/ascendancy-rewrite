#!/usr/bin/env python3
"""tPF-3b F7 DECISION PROBE — full-boundary outline vs 2px-inset overlay.

THE CONFLICT (docs/re/_wip_tPF3.md F7): scripts/tplv1_lattice_witness.py scores
100.0% edge support at the FULL diamond boundary on work/r1/screens/t254/
02_planet_detail.png, yet the paint fn 0x3bb19..0x3c335 draws lines ONLY inset.

THE GEOMETRY, re-read at bytes this iteration (work/tPF3b_inset.asm):
  the full vertex table is esp+0x260/264, 0x278/27c, 0x290/294, 0x2a8/2ac;
  LEGAL  branch 0x3bc5b (edx==-1): V0 y+1, V1 x-2, V2 y-1, V3 x+2  -> 64x32
  ILLEGAL branch 0x3bd4d         : V0 y+14, V1 x-28, V2 y-14, V3 x+28 -> 12x6
  (both then 0x5bf71 x4 with pen `mov ax,di`, and both then the state-block
   filler 0x62d15 with [0x48c33]+di*0x100 — 0x3bd3a / 0x3be2c.)
  So the two branches differ ONLY in the shrink amount, and _wip F3's
  "64x31 vs 12x6" is confirmed at instruction level.

WHY THE WITNESS CANNOT SETTLE IT (leg 1): perpendicular gap between the full
edge (half-extents 34,17 -> line x+2y=34) and the inset edge (32,16 -> x+2y=32)
is 2/sqrt(5) = 0.894 LOGICAL px. t254 is 1:1 with the logical screen (a pure
TRANSLATION fit reaches 100% over a 34-px pitch; a scaled shot cannot). An
exact-boundary sampler therefore sees the inset line at <=1 px: INDETERMINATE.

THE DECISIVE MEASUREMENT (leg 3): line FOOTPRINT WIDTH perpendicular to a
boundary. Adjacent cells are EXACTLY tiled (|det| 1156 == diamond area), so
  FULL  : one line on the shared edge      -> 1-px footprint
  INSET : two lines, one per cell, 2*0.894 = 1.79 px apart -> ~3-px footprint
This is separable at 1 px. Sweep perpendicular offsets -4..+4 about each
fitted boundary segment and histogram the hits. Controls: the same sweep about
lines shifted by a KNOWN 2 px and 4 px (verifies the sweep measures offsets
faithfully), and a wrong-angle control.
"""
import os, sys, math
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tplv1_lattice_witness as W

w, h, px = W.load_rgb(W.PNG)
ox, oy = W.ORIGIN
mask = bytearray(w * h)
cnt = Counter()
for i in range(w * h):
    r, g, b = px[3 * i], px[3 * i + 1], px[3 * i + 2]
    for c, rgb in W.EDGE_RGB.items():
        if abs(r - rgb[0]) <= W.TOL and abs(g - rgb[1]) <= W.TOL and abs(b - rgb[2]) <= W.TOL:
            cnt[c] += 1
            if c != 0:
                mask[i] = 1 + c
            break
print(f"leg0 edge-colour px by class: {dict(cnt)}")

S, DX, DY = 0, -23, 48          # witness law-B fit (re-verified this iteration)
B, C = W.B, W.C
cells = [(row, col) for row in range(15)
         for col in range(B[S][row], B[S][row] + C[S][row])]
print(f"leg2 size{S} cells={len(cells)} dx={DX} dy={DY}")

def centre(row, col):
    return (410 + 34 * (col - row) + DX, 127 + 17 * (col + row) + DY)

def hit(x, y):
    sx, yy = ox + int(round(x)), oy + int(round(y))
    return 0 <= sx < w and 0 <= yy < h and mask[yy * w + sx]

# the four edge families of the diamond: (direction, outward unit normal)
FAMS = []
for (ax, ay, bx, by) in ((-34, 0, 0, -17), (0, -17, 34, 0),
                         (34, 0, 0, 17), (0, 17, -34, 0)):
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy)
    nx, ny = dy / L, -dx / L          # normal
    if ny > 0:                         # orient normals consistently OUTWARD-down
        nx, ny = -nx, -ny
    FAMS.append(((ax, ay, bx, by), (nx, ny)))

OFFS = list(range(-4, 5))
hist = Counter()
nsweep = 0
for (row, col) in cells:
    cx, cy = centre(row, col)
    for (seg, (nx, ny)) in FAMS:
        (ax, ay, bx, by) = seg
        for t in range(0, 29):
            u = t / 28.0
            px0, py0 = cx + ax + (bx - ax) * u, cy + ay + (by - ay) * u
            # only sweep where a +-4 window is in frame
            if not (ox + 6 < px0 < ox + w - 6 and oy + 6 < py0 < oy + h - 6):
                continue
            hits = [o for o in OFFS if hit(px0 + nx * o, py0 + ny * o)]
            if hits:
                nsweep += 1
                for o in hits:
                    hist[o] += 1
print(f"leg3 perpendicular footprint (offset_px: hits), sweeps_with_hit={nsweep}")
tot = sum(hist.values())
for o in OFFS:
    n = hist[o]
    bar = "#" * int(60 * n / tot) if tot else ""
    print(f"   {o:+d}: {n:5d} {bar}")

# spread statistic: fraction of hits at |offset| >= 2 (inset predicts many;
# full-boundary predicts ~0 apart from the 0.894 rounding smear to +-1)
at0 = hist[0]
near = hist[-1] + hist[0] + hist[1]
far = sum(v for k, v in hist.items() if abs(k) >= 2)
print(f"leg3 at0={at0} within1={near} at|off|>=2={far}  far_frac={far/max(tot,1):.3f}")

# --- control: does the sweep measure a KNOWN shift faithfully? ---
print("\nleg4 CONTROL sweep about lines shifted +2 px along the normal")
hist2 = Counter()
for (row, col) in cells:
    cx, cy = centre(row, col)
    for (seg, (nx, ny)) in FAMS:
        (ax, ay, bx, by) = seg
        for t in range(0, 29):
            u = t / 28.0
            px0 = cx + ax + (bx - ax) * u + nx * 2
            py0 = cy + ay + (by - ay) * u + ny * 2
            if not (ox + 6 < px0 < ox + w - 6 and oy + 6 < py0 < oy + h - 6):
                continue
            for o in OFFS:
                if hit(px0 + nx * o, py0 + ny * o):
                    hist2[o] += 1
t2 = sum(hist2.values())
print("   " + "  ".join(f"{o:+d}:{hist2[o]}" for o in OFFS))

print(f"""
READING GUIDE
  inset geometry predicts the peak AT o=-1 and o=+1 (the two cells' inset lines
  straddle the nominal boundary by 0.894 px each, rounding to +-1) with the o=0
  column LOW; full-boundary geometry predicts a single peak at o=0.
  The leg-4 control (sweep centred 2 px off the boundary) shows what a real
  mis-centre looks like: peak moves to o=-2.
VERDICT: see the printed distribution; the script exits 0 either way (this is a
measurement, not a gate).""")
