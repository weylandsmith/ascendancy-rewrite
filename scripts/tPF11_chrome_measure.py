#!/usr/bin/env python3
"""tPF11_chrome_measure.py — MEASURE the vendor research-screen chrome
regions on work/screens/t252/research_open_game.png (640x480):
  A. perimeter bands (x0..6 / x633..639 / y0..6 / y472..479) — texfrac
  B. header band y8..36 speckle census (compare kSpeckle* weights)
  C. divider ramp rows y38..46 (compare statusRampColourAt)
  D. tree field edge: is x7 a solid line? per-row colour at x7
  E. right panel: scan for its rect edges (bright border runs)
  F. bottom band under the tree field (y472..479) and between field/panel
"""
from PIL import Image
from collections import Counter

P = "work/screens/t252/research_open_game.png"
im = Image.open(P).convert("RGB")
px = im.load()
W, H = im.size

def row(y, x0, x1):
    return [px[x, y] for x in range(x0, x1)]

def col(x, y0, y1):
    return [px[x, y] for y in range(y0, y1)]

def c(s):
    return Counter(s).most_common(8)

print("A. perimeter texture bands")
for name, s in [
    ("left x0..6 full", [px[x, y] for y in range(H) for x in range(0, 7)]),
    ("right x633..639 full", [px[x, y] for y in range(H) for x in range(633, 640)]),
    ("top y0..6 full", [px[x, y] for y in range(7) for x in range(W)]),
    ("bottom y473..479", [px[x, y] for y in range(473, 480) for x in range(W)]),
]:
    n = len(s)
    darkvar = sum(1 for v in s if v != (0, 0, 0))
    print(f"  {name}: nonzero {darkvar}/{n} = {darkvar/n:.3f} top={c(s)[:5]}")

print("B. header band y8..36 x8..630 speckle census")
s = [px[x, y] for y in range(8, 37) for x in range(8, 631)]
n = len(s)
for v, k in Counter(s).most_common(10):
    print(f"    {v}: {k} ({100*k/n:.1f}%)")

print("C. divider ramp rows y37..47 full width x8..630")
for y in range(37, 48):
    print(f"  y{y}: {c(row(y, 8, 631))[:4]}")

print("D. tree-field left edge x7 column census y48..470")
print("   ", c(col(7, 48, 471))[:5])
print("  x6:", c(col(6, 48, 471))[:5])
print("E. right panel: horizontal scan rows y=60,200,440 x470..640 transitions")
for y in (60, 200, 440):
    rr = row(y, 470, 640)
    trans = []
    for i in range(1, len(rr)):
        if rr[i] != rr[i-1]:
            trans.append((470+i, rr[i-1], rr[i]))
    print(f"  y{y}: {trans[:12]}")
print("E2. vertical scan col x=558 y36..60 + y430..472 transitions")
for (y0, y1) in ((36, 64), (425, 472)):
    cc = col(558, y0, y1)
    trans = []
    for i in range(1, len(cc)):
        if cc[i] != cc[i-1]:
            trans.append((y0+i, cc[i-1], cc[i]))
    print(f"  x558 y{y0}..{y1}: {trans[:12]}")
print("F. panel bg census inside x490..620 y60..440 (dark classes)")
s = [px[x, y] for y in range(60, 441) for x in range(490, 621)]
print("   ", Counter(s).most_common(6))
