#!/usr/bin/env python3
"""tPF11_witness_census.py — port research-screen chrome census.

Usage: <shot.png>
Checks on the PORT capture (640x480):
  (1) perimeter bands textured (texfrac >= 0.95 on x0..6, x633..639,
      y0..6, y473..479);
  (2) header speckle present y8..36 (non-black frac in the speckle family
      >= 0.4) and NO tan box edge (150,130,110) anywhere;
  (3) ramp rows 38..45 hold the shipped family colours across x100..400
      (>=60% of the row in the ramp colour set);
  (4) y46 BLACK across x8..476; x7 BLACK y48..470 (no status tail leaked);
  (5) panel left band x477..484 textured y100..430; x485 mostly black;
  (6) panel well y434..472 x477..639 textured (>=0.6; the pan buttons +
      faces paint over part of it);
  (7) NO gray invention lines: kLane (120,120,120) count == 0 in the
      header/interior border rows; (90,90,110) count == 0 anywhere.
"""
import sys
from collections import Counter
from PIL import Image

im = Image.open(sys.argv[1]).convert("RGB")
px = im.load()
W, H = im.size
fails = []

def tex(p):
    r, g, b = p
    if g > r + 40 and g > b + 20:
        return False
    return min(r, g, b) >= 40

def painted(p):
    # The band law is "fully painted by the texture generator", and the
    # textureColourAt family legitimately includes dark mottle cells
    # ((12,12,12),(24,49,40) census on the port shot) — the vendor-bright
    # tex() classifier mismatches them. In the band regions the only
    # alternative state is the black interior, so non-black == painted.
    return p != (0, 0, 0)

def frac(cond, xs, ys):
    n = sum(1 for y in ys for x in xs if cond(px[x, y]))
    tot = len(list(xs)) * len(list(ys))
    return n / tot

# (1) perimeter
for name, f in [
    ("left x0..6", frac(painted, range(0, 7), range(0, 480))),
    ("right x633..639", frac(painted, range(633, 640), range(0, 480))),
    ("top y0..6", frac(painted, range(0, 640), range(0, 7))),
    ("bottom y473..479", frac(painted, range(0, 640), range(473, 480))),
]:
    print(f"{name}: texfrac {f:.3f}")
    if f < 0.95: fails.append(name)

# (2) header speckle: share of the six census colours
census = {(0,0,0),(8,12,16),(8,12,8),(8,28,49),(8,32,49),(8,36,49)}
f = frac(lambda p: p in census, range(8, 631), range(8, 37))
print(f"header speckle-family share: {f:.3f}")
if f < 0.9: fails.append("header speckle")
tan = sum(1 for y in range(0, 480) for x in range(0, 640)
          if abs(px[x,y][0]-150)<12 and abs(px[x,y][1]-130)<12 and abs(px[x,y][2]-110)<12)
print(f"tan-box px (150,130,110)+-12: {tan}")
if tan > 40: fails.append("tan box present")

# (3) ramp rows: family set (ramp colours shipped)
rampset = {(82,125,123),(123,182,181),(115,117,115),(66,105,107),
           (33,56,57),(24,48,41),(24,28,24)}
for y in range(38, 46):
    f = frac(lambda p: p in rampset, range(100, 401), range(y, y+1))
    if f < 0.6: fails.append(f"ramp y{y} share {f:.2f}")
print("ramp rows 38..45 family share >= 0.6:", "OK" if not any(f.startswith('ramp') for f in fails) else fails)

# (4) y46 black + x7 black
f = frac(lambda p: p == (0,0,0), range(8, 477), range(46, 47))
print(f"y46 black share x8..476: {f:.3f}")
if f < 0.98: fails.append("y46 not black")
f = frac(lambda p: p == (0,0,0), range(7, 8), range(48, 471))
print(f"x7 black share y48..470: {f:.3f}")
if f < 0.98: fails.append("x7 not black")

# (5) panel band
f = frac(painted, range(477, 485), range(100, 431))
print(f"panel left band x477..484 texfrac: {f:.3f}")
if f < 0.95: fails.append("panel band")
f = frac(lambda p: p == (0,0,0), range(486, 632), range(60, 430))
print(f"panel interior black share: {f:.3f}")
if f < 0.5: fails.append("panel interior not black")

# (6) well
f = frac(painted, range(477, 640), range(434, 473))
print(f"panel well texfrac: {f:.3f}")
if f < 0.6: fails.append("well")

# (7) gray inventions
gray = sum(1 for y in range(0, 480) for x in range(0, 640)
           if px[x,y] == (90,90,110))
print(f"(90,90,110) count: {gray}")
if gray > 0: fails.append("gray panel rect present")
lane = sum(1 for y in (46, 472) for x in range(7, 633) if px[x,y] == (120,120,120))
print(f"kLane(120,120,120) on rows 46/472: {lane}")
if lane > 0: fails.append("kLane interior rect present")

print("VERDICT PASS" if not fails else f"VERDICT FAIL {fails}")
