#!/usr/bin/env python3
"""tPF11_panel_edges.py — exact research right-panel border band extents."""
from PIL import Image
im = Image.open("work/screens/t252/research_open_game.png").convert("RGB")
px = im.load()

def tex(x, y):
    r, g, b = px[x, y]
    if g > r + 40 and g > b + 20:
        return False
    return min(r, g, b) >= 40

# left border vertical extent at x=477..481 (skip ramp rows 38..45 and
# perimeter): find contiguous texture run in y46..472
for x in (477, 478, 480, 482, 484, 485):
    ys = [y for y in range(30, 473) if tex(x, y)]
    runs, start = [], None
    for y in range(30, 473):
        if tex(x, y) and start is None: start = y
        if not tex(x, y) and start is not None:
            runs.append((start, y - 1)); start = None
    if start is not None: runs.append((start, 472))
    print(f"x{x}: runs {runs}")
# bottom border horizontal extent at y=434..440
for y in (433, 434, 435, 437, 439, 440, 441):
    xs = [x for x in range(460, 640) if tex(x, y)]
    runs, start = [], None
    for x in range(460, 640):
        if tex(x, y) and start is None: start = x
        if not tex(x, y) and start is not None:
            runs.append((start, x - 1)); start = None
    if start is not None: runs.append((start, 639))
    print(f"y{y}: runs {runs}")
# gap between tree field right edge and panel left: rows y100..430 col 470..478
col = {x: sum(1 for y in range(100, 431) if tex(x, y)) for x in range(468, 486)}
print("texture counts x468..485 in y100..430:", col)
