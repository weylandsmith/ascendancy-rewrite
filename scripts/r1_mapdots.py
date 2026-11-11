#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""Map-dot finder: bright celestial dots in the strategic-map region.

Strategic-map law: map area is root coords x in [40, 470], y in [40, 460]
(right sidebar starts ~x 470). Star/planet dots are bright (white/yellow/red/
blue) on the black void. Returns the N brightest cluster centers sorted, for
click planning. Usage: r1_mapdots.py shot.png [-n 12]"""
import sys
from PIL import Image


def main():
    path = sys.argv[1]
    n = int(sys.argv[sys.argv.index("-n") + 1]) if "-n" in sys.argv else 12
    im = Image.open(path).convert("RGB")
    px = im.load()
    W, H = im.size
    pts = []
    for y in range(40, min(460, H)):
        for x in range(40, min(470, W)):
            r, g, b = px[x, y]
            s = r + g + b
            if s > 330 and not (r < 90 and g < 90 and b < 90):
                pts.append((s, x, y))
    # cluster 3x3
    used = set()
    clusters = []
    pts.sort(reverse=True)
    for s, x, y in pts:
        if any(abs(x - cx) <= 2 and abs(y - cy) <= 2 for _, cx, cy in clusters):
            continue
        clusters.append((s, x, y))
    # prefer isolated bright dots (void around) = celestial markers
    out = []
    for s, x, y in clusters:
        ring = sum(1 for dy in range(-6, 7) for dx in range(-6, 7)
                   if (dx or dy) and px[max(0,x+dx), max(0,y+dy)][0]
                   + px[max(0,x+dx), max(0,y+dy)][1]
                   + px[max(0,x+dx), max(0,y+dy)][2] > 200)
        out.append((s, ring, x, y))
    out.sort(key=lambda t: (-t[0], t[1]))
    for s, ring, x, y in out[:n]:
        print(f"dot ({x},{y}) lum {s} neighbors-bright {ring}")


if __name__ == "__main__":
    main()
