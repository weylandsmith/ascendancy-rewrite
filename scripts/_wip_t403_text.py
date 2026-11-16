#!/usr/bin/env python3
"""t403 scratch: locate TEXT bands by counting saturated-green ink pixels
(the port draws its list/label text green through game.pal), so crop boxes are
measured rather than guessed (t397 pitfall: crop-by-guess caught nothing).
"""
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(path, box=None, axis="row"):
    im = Image.open(os.path.join(ROOT, path)).convert("RGB")
    x0, y0, x1, y1 = box or (0, 0, im.width, im.height)
    px = im.load()
    prof = []
    if axis == "row":
        rng = range(y0, y1)
        line = lambda k: sum(1 for x in range(x0, x1)
                             if px[x, k][1] > 90 and px[x, k][1] > px[x, k][0] + 40
                             and px[x, k][1] > px[x, k][2] + 20)
    else:
        rng = range(x0, x1)
        line = lambda k: sum(1 for y in range(y0, y1)
                             if px[k, y][1] > 90 and px[k, y][1] > px[k, y][0] + 40
                             and px[k, y][1] > px[k, y][2] + 20)
    for k in rng:
        prof.append((k, line(k)))
    seg, start = [], None
    for k, h in prof:
        if h > 2 and start is None:
            start = k
        elif h <= 2 and start is not None:
            if k - start >= 4:
                seg.append((start, k - 1))
            start = None
    if start is not None:
        seg.append((start, prof[-1][0]))
    print(path, box or "FULL", axis, "green-ink bands:", seg)


if __name__ == "__main__":
    box = tuple(int(v) for v in sys.argv[3].split(",")) if len(sys.argv) > 3 else None
    main(sys.argv[1], box, sys.argv[2])
