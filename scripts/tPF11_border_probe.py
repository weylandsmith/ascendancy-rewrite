#!/usr/bin/env python3
"""tPF11_border_probe.py — characterise the vendor research-screen chrome.

Sample colour runs on work/screens/t252/research_open_game.png:
 (1) outermost screen border rows/cols (is there a full-screen mineral frame?)
 (2) the tree-field edge around the RESWIN rect 7,46-476,472
 (3) the right info-panel left edge near x=484
Compare the same lines on the galaxy-map original (scratchpad/
galaxymap-original.png) to test the SHARED-CHROME hypothesis.
"""
import sys, os
from collections import Counter
from PIL import Image

def col(im, x, y0, y1):
    px = im.load()
    return [px[x, y] for y in range(y0, y1)]

def row(im, y, x0, x1):
    px = im.load()
    return [px[x, y] for x in range(x0, x1)]

def prof(name, samples):
    print(f"--- {name}")
    for label, s in samples:
        c = Counter(s)
        print(f"  {label}: {c.most_common(6)}")

def main():
    for path in ["work/screens/t252/research_open_game.png",
                 "scratchpad/galaxymap-original.png"]:
        if not os.path.exists(path):
            print(f"MISSING {path}"); continue
        im = Image.open(path).convert("RGB")
        print(f"== {path} {im.size}")
        W, H = im.size
        prof("outer frame", [
            ("row0 x0..W", row(im, 0, 0, W)),
            (f"row3 x0..W", row(im, 3, 0, W)),
            (f"col0 y0..H", col(im, 0, 0, H)),
            (f"col3 y0..H", col(im, 3, 0, H)),
            (f"row{H-3} x0..W", row(im, H-3, 0, W)),
            (f"col{W-3} y0..H", col(im, W-3, 0, H)),
        ])
        prof("tree-field edge (RESWIN 7,46-476,472)", [
            ("row 44 x8..470 (just above RESWIN)", row(im, 44, 8, 470)),
            ("row 46 x8..470", row(im, 46, 8, 470)),
            ("row 48 x8..470", row(im, 48, 8, 470)),
            ("col 5 y50..470", col(im, 5, 50, 470)),
            ("col 7 y50..470", col(im, 7, 50, 470)),
            ("col 9 y50..470", col(im, 9, 50, 470)),
        ])
        if "research" in path:
            prof("right panel edge", [
                ("row 200 x478..500", row(im, 200, 478, 500)),
                ("row 200 x628..640", row(im, 200, 628, 640)),
            ])

if __name__ == "__main__":
    main()
