#!/usr/bin/env python3
# t400 witness census (mechanical, our own render — R13-safe):
#  1) title-hover shot: the LOAD band (159,360-477,390) must contain the
#     hover fill (0,28,36) as its dominant colour; the OTHER bands keep
#     (0,0,8).
#  2) map shot: (a) left-margin + right-column texture bands are NON-FLAT
#     and >=90% of their pixels lie inside game.pal; (b) rail icon zone:
#     chromatic pixels exist at x 583..628 (the RIGHT-of-label placement)
#     on the Planets/Ships/Research rows; (c) species flag zone x521..553
#     y288..311 is non-flat; (d) the rail fill row census includes
#     (12,32,48).
import sys
from collections import Counter

from PIL import Image

GP = open("extracted/ascend01/data/game.pal", "rb").read()
GSET = set(tuple(((GP[3 * k + i]) << 2) | (GP[3 * k + i] >> 4) for i in range(3))
           for k in range(256))
HOVER = (0, 28, 36)
FILL = (0, 0, 8)

fails = []

def band(path, x0, y0, x1, y1):
    im = Image.open(path).convert("RGB")
    px = im.load()
    return Counter(px[x, y] for y in range(y0, y1 + 1) for x in range(x0, x1 + 1))

# 1) title hover
t = band("/tmp/t400_shots/title-hover.png", 159, 360, 477, 390)
if t.most_common(1)[0][0] != HOVER:
    fails.append(f"LOAD band not hovered: {t.most_common(3)}")
for y0 in (200, 240, 280, 320):  # other bands keep the plain fill
    o = band("/tmp/t400_shots/title-hover.png", 159, y0, 477, y0 + 30)
    if o.most_common(1)[0][0] != FILL:
        fails.append(f"band y{y0} not plain fill: {o.most_common(3)}")

# 2) map
m = Image.open("/tmp/t400_shots/map.png").convert("RGB")
pxm = m.load()
W, H = m.size
for name, (x0, x1) in (("left", (0, 6)), ("right", (466, 639))):
    c = Counter(pxm[x, y] for y in range(0, min(H, 480)) for x in range(x0, min(W, x1 + 1)))
    if len(c) < 6:
        fails.append(f"{name} band flat: {len(c)} colours")
    # The port's OWN cosmos frame line (kLane grey 120,120,120) crosses
    # x=6 / the band edges — geometry, not texture (t398 precedent: the
    # census names the port's own colours instead of failing on them).
    own = c.pop((120, 120, 120), 0)
    tot = sum(c.values())
    inside = sum(n for col, n in c.items() if col in GSET)
    frac = inside / max(1, tot)
    print(f"{name} band: {len(c)} colours, {100*frac:.1f}% in game.pal "
          f"(port frame px excluded: {own})")
    if frac < 0.90:
        fails.append(f"{name} band outside game.pal: {100*frac:.1f}%")
# rail icon zone chroma at the RIGHT placement (x 583..628 rows)
for label, y0 in (("Planets", 130), ("Ships", 169), ("Research", 208)):
    ch = 0
    for y in range(y0, y0 + 30):
        for x in range(583, 629):
            if x < W and y < H:
                c = pxm[x, y]
                if max(c) - min(c) >= 20:
                    ch += 1
    print(f"rail {label} icon-zone chroma: {ch}")
    if ch < 100:
        fails.append(f"rail {label} icon zone has no art chroma ({ch})")
# species flag zone non-flat
f = Counter(pxm[x, y] for y in range(288, 312) for x in range(521, 554) if x < W and y < H)
if len(f) < 4:
    fails.append(f"species flag zone flat: {f.most_common(3)}")
else:
    print(f"species flag zone: {len(f)} colours, top {f.most_common(2)}")
# rail fill present
rf = Counter(pxm[x, y] for y in range(130, 161) for x in range(474, 583) if x < W and y < H)
if rf.get((12, 32, 48), 0) < 500:
    fails.append(f"rail fill (12,32,48) missing: {rf.most_common(3)}")

print("VERDICT", "PASS" if not fails else "FAIL")
for f_ in fails:
    print("  -", f_)
sys.exit(1 if fails else 0)
