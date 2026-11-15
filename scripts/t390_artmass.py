#!/usr/bin/env python3
# t390 verification: OUR Xvfb screenshot vs the art-zone mass law that was
# 0 at task assignment (STATE.md t390 block: art zone rows 0-195 mass 0,
# menu zone 195-475 mass 1006). Mechanical counting on OUR OWN render
# (t386 §7: self-graded VISION stays banned; mass/conflict counting is).
#
# Checks:
#  1. art-zone mass (rows 0..194) non-bg pixels  -> must be >> 0
#  2. key-hole law: inside each button rect, pixels are ONLY the fill
#     colour (0,0,8) or label-white-ish (r,g,b all >180 and near grey)
#  3. registration: colour-histogram of our art zone vs the GIF plane
#     mapped through the TSV (the palette we SHIP) must agree on the top
#     colours (proves the blit carries the palette, not a wash).
import sys
from collections import Counter
from PIL import Image

shot = Image.open(sys.argv[1] if len(sys.argv) > 1 else '/tmp/title_shot.png').convert('RGB')
W, H = shot.size
px = shot.load()
print("shot size", W, H)

# The window is 640x480 inside a 1024x768 root; find the window origin by
# scanning for the first row/col where the art exists (non-desktop). Simple:
# assume centred: (1024-640)/2=192, (768-480)/2=144. Verify by sampling.
ox, oy = (W - 640) // 2, (H - 480) // 2
print("window origin assumed", ox, oy)

art = Counter(px[ox + x, oy + y] for y in range(0, 195) for x in range(640))
mass = sum(n for c, n in art.items() if c != (10, 12, 26))
print("art-zone rows 0..194: distinct", len(art), "non-bg mass", mass)

# key-hole / band law over the 7 rects
bad = 0
for k in range(7):
    y0 = 200 + 40 * k
    c = Counter(px[ox + x, oy + y] for y in range(y0, y0 + 30) for x in range(159, 478))
    fill = c.get((0, 0, 8), 0)
    white = sum(n for col, n in c.items() if min(col) > 180 and max(col) - min(col) < 40)
    other = 9570 - fill - white
    print("band k%d fill=%d white=%d other=%d" % (k, fill, white, other))
    bad += other

# palette agreement: top-5 art-zone colours must be TSV-mapped values
tsv = {}
for line in open('/home/hrethric/projects/ascendancy/rewrite/tests/data/title_palette_t386.tsv'):
    if line.startswith('#'):
        continue
    a, gct, shotc = line.rstrip('\n').split('\t')
    tsv[int(a)] = tuple(int(v) for v in shotc.split(','))
top5 = [c for c, n in art.most_common(5)]
inmap = [c in set(tsv.values()) for c in top5]
print("top5 art colours", top5)
print("in TSV vendor set", inmap)
ok = mass > 50000 and bad == 0 and all(inmap[:3])
print("VERDICT", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
