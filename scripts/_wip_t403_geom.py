#!/usr/bin/env python3
"""t403 scratch: column/row bright runs to choose crop boxes by MEASUREMENT."""
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def runs(path, box, axis, thresh=40):
    im = Image.open(os.path.join(ROOT, path)).convert("RGB")
    x0, y0, x1, y1 = box or (0, 0, im.width, im.height)
    px = im.load()
    hist = [h for h in im.resize((120, 90)).getcolors(1 << 20) if h]
    bg = max(hist, key=lambda t: t[0])[1]
    out = []
    if axis == "col":
        for x in range(x0, x1):
            hits = sum(1 for y in range(y0, y1)
                       if sum(abs(a - b) for a, b in zip(px[x, y], bg)) > thresh)
            out.append((x, hits))
    else:
        for y in range(y0, y1):
            hits = sum(1 for x in range(x0, x1)
                       if sum(abs(a - b) for a, b in zip(px[x, y], bg)) > thresh)
            out.append((y, hits))
    # compress into runs of hits>0
    seg = []
    start = None
    for k, h in out:
        if h > 0 and start is None:
            start = k
        elif h == 0 and start is not None:
            seg.append((start, k - 1))
            start = None
    if start is not None:
        seg.append((start, out[-1][0]))
    print(path, box or "FULL", axis, "->", seg[:30])


if __name__ == "__main__":
    p = sys.argv[1]
    axis = sys.argv[2]
    box = None
    if len(sys.argv) > 3:
        box = tuple(int(v) for v in sys.argv[3].split(","))
    runs(p, box, axis)
