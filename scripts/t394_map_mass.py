#!/usr/bin/env python3
# t394 map-chrome census (mechanical, PASS/FAIL):
#  1. TURNCOUNT panel region has GREEN oval pixels (vendor-green law)
#  2. each of the five oval x-centres carries green ink
#  3. the OLD string dump is GONE: sidebar band y 90..120 (between
#     NEXTTURNCONT bottom 82 and Planets top 130) is dark (no white glyph ink)
#  4. spin/zoom cluster rects carry NON-FLAT art (>=2 distinct colours each)
#  5. race strip: all 7 slots each dominated by a distinct colour family
import sys
from collections import Counter
from PIL import Image

SHOT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/t394_shots/map.png"
im = Image.open(SHOT).convert("RGB")
px = im.load()
fails = []

def region(x0, y0, x1, y1):
    c = Counter()
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            c[px[x, y]] += 1
    return c

def is_green(c):
    r, g, b = c
    return g > 90 and g > r + 40 and g > b + 20

# 1+2 green ovals
green_total = 0
for i, cx in enumerate((491, 522, 553, 584, 584 + 31)):
    g = sum(v for c, v in region(cx - 9, 10, cx + 9, 39).items() if is_green(c))
    green_total += g
    if g < 30:
        fails.append(f"oval{i} green mass {g} < 30")
if green_total < 300:
    fails.append(f"panel green total {green_total} < 300")

# 3 no white-glyph string dump in the removed-dump band
band = region(474, 90, 632, 120)
white = sum(v for c, v in band.items() if min(c) > 150)
if white > 40:
    fails.append(f"string-dump band white px {white} > 40 (dump not removed?)")

# 4 cluster art non-flat (rects from windows.txt)
CLUSTERS = [(495, 364, 509, 394), (479, 364, 494, 394), (518, 364, 548, 379),
            (518, 380, 548, 394), (557, 380, 587, 394), (557, 364, 587, 379),
            (596, 364, 626, 394), (479, 403, 509, 433), (518, 403, 548, 433),
            (557, 403, 587, 433), (596, 403, 626, 433)]
for i, r in enumerate(CLUSTERS):
    cols = region(*r)
    if len(cols) < 2:
        fails.append(f"cluster{i} {r} flat ({len(cols)} colour)")

# 5 seven race slots, distinct dominant colours
doms = []
for i in range(7):
    x0 = 479 + 22 * i
    cols = region(x0 + 3, 452, x0 + 13, 462)
    dom = cols.most_common(1)[0][0]
    doms.append(dom)
if len(set(doms)) < 6:   # 7 searched CVD-safe colours; allow 1 WM blend
    fails.append(f"race slots not distinct: {doms}")

print("doms:", doms)
print("band white:", white, " green total:", green_total)
if fails:
    print("CENSUS FAIL");
    [print(" -", f) for f in fails]
    sys.exit(1)
print("CENSUS PASS")
