#!/usr/bin/env python3
"""tPF11_panel_rect.py — right-panel mineral border rect + ramp x-extent
on work/screens/t252/research_open_game.png. Texture family = the
(57..123, 85..182, 90..198) teal/grey mottle; classify a px as TEXTURE if
min channel >= 40 and it's not green text (g much > r,b)."""
from PIL import Image
from collections import Counter

im = Image.open("work/screens/t252/research_open_game.png").convert("RGB")
px = im.load()
W, H = im.size

def tex(x, y):
    r, g, b = px[x, y]
    if g > r + 40 and g > b + 20:   # green text
        return False
    return min(r, g, b) >= 40

# ramp extent: rows 38..45, find x-runs where >=60% of the row is texture-ish
def rowfrac(y):
    n = sum(1 for x in range(W) if tex(x, y))
    return n / W

for y in range(36, 48):
    print(f"y{y}: texfrac {rowfrac(y):.3f}")

# per-row first/last texture x on ramp rows
for y in (39, 41, 43):
    xs = [x for x in range(W) if tex(x, y)]
    print(f"y{y}: tex x {min(xs)}..{max(xs)} (n={len(xs)})")

# panel: column profile of texture at x=478..486 over y
print("panel left border cols: first/last tex y per col")
for x in (477, 480, 484, 486):
    ys = [y for y in range(H) if tex(x, y)]
    if ys:
        # find the contiguous run covering y>300
        run = [y for y in ys if 30 < y < 470]
        print(f"  x{x}: n={len(run)} range {min(run)}..{max(run)}")

# panel border rows: texture runs on rows through the panel
for y in (38, 40, 434, 436, 438, 440, 442):
    xs = [x for x in range(460, W) if tex(x, y)]
    print(f"y{y} x460+: n={len(xs)} range {min(xs) if xs else '-'}..{max(xs) if xs else '-'}")

# panel interior left edge at mid-height: where does black start after border
y = 250
seq = [(x, px[x, y]) for x in range(474, 496)]
print("row250 x474..495:", seq)
