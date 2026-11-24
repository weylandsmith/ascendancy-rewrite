#!/usr/bin/env python3
"""tPL-V1 port census: OUR render must show the corrected lattice.

Checks on /tmp/tplv1_shots/planet-open.png (640x480, screen coords 1:1):
 1. EDGE COLOUR: the class-coloured edge pixels (game.pal-conv idx 12 white
    / 117 red / 146 green / 255 blue / 0 black-in-fill-excluded) form a
    census > 0 in the field band, and the t418b INVENTED outline colour
    (24,24,32) is ABSENT (it was the old painter's signature).
 2. ADJACENCY: for every valid cell of the fitted size class, the shared-
    edge midpoint probe (centre + (17,8)) carries EITHER the fill or an
    edge colour (never starfield black) — under the old transposed law a
    measurable fraction of those points sat in gaps.
 3. FILL: tile centres carry the uniform pal[150] fill conv colour.
Exit 0 iff all pass.
"""
import os, sys, zlib, struct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from tplv1_lattice_witness import load_rgb, conv, EDGE_RGB  # noqa: E402

SHOT = os.environ.get("SHOT", "/tmp/tplv1_shots/planet-open.png")
OLD_OUTLINE = (24, 24, 32)

B = [[0,0,0,0,4,4,5,0,0,0,0,0,0,0,0],
     [0,0,0,4,3,4,5,6,0,0,0,0,0,0,0],
     [0,0,3,2,3,3,4,5,7,0,0,0,0,0,0],
     [0,2,1,1,2,2,3,4,5,7,0,0,0,0,0],
     [1,0,0,0,1,1,2,3,4,5,7,0,0,0,0]]
C = [[0,0,0,0,2,3,2,0,0,0,0,0,0,0,0],
     [0,0,0,1,3,3,3,1,0,0,0,0,0,0,0],
     [0,0,1,4,4,5,4,4,1,0,0,0,0,0,0],
     [0,2,5,6,6,7,6,6,5,2,0,0,0,0,0],
     [3,6,7,8,8,9,8,8,7,6,3,0,0,0,0]]


def main():
    if not os.path.exists(SHOT):
        print("missing shot", SHOT)
        return 1
    w, h, px = load_rgb(SHOT)

    def at(x, y):
        if 0 <= x < w and 0 <= y < h:
            b = (y * w + x) * 3
            return (px[b], px[b + 1], px[b + 2])
        return None

    ok = True
    # 1) old invented outline colour must be GONE; class colours PRESENT
    old = sum(1 for i in range(w * h)
              if px[3 * i:3 * i + 3] == bytes(OLD_OUTLINE))
    edge_counts = {c: 0 for c in (1, 2, 3, 4)}
    for i in range(w * h):
        p = (px[3 * i], px[3 * i + 1], px[3 * i + 2])
        for c in edge_counts:
            if all(abs(p[k] - EDGE_RGB[c][k]) <= 14 for k in range(3)):
                edge_counts[c] += 1
    print("old (24,24,32) outline px:", old, "(must be 0)")
    print("class edge px:", edge_counts)
    if old:
        print("FAIL old outline present"); ok = False
    if edge_counts[1] < 200:
        print("FAIL white class edges missing"); ok = False

    # fit size class + offset: the port paints tile (0,0) at (410,127)
    # (tileCenter law), so NO offset fit is needed — assert directly.
    fill = conv(150)
    print("expected fill conv(150):", fill)
    for size in range(5):
        pts, hitc, edgec, blackc = 0, 0, 0, 0
        for r in range(15):
            for c in range(B[size][r], B[size][r] + C[size][r]):
                cx, cy = 410 + 34 * (c - r), 127 + 17 * (c + r)
                p = at(cx, cy)
                if p is None:
                    continue
                pts += 1
                if all(abs(p[k] - fill[k]) <= 14 for k in range(3)):
                    hitc += 1
                m = at(cx + 17, cy + 8)  # shared-edge midpoint
                if m is None:
                    continue
                if all(m[k] < 12 for k in range(3)):
                    blackc += 1
                else:
                    edgec += 1
        if pts:
            print(f"size {size}: centres {pts} fill-hit {hitc} "
                  f"edge-mid non-black {edgec}/{pts} black {blackc}")
    # the seed-5 planet is size 1 (11 cells) — check that row explicitly
    pts = hitc = edgec = 0
    for r in range(15):
        for c in range(B[1][r], B[1][r] + C[1][r]):
            cx, cy = 410 + 34 * (c - r), 127 + 17 * (c + r)
            p = at(cx, cy)
            if p and all(abs(p[k] - fill[k]) <= 14 for k in range(3)):
                hitc += 1
            pts += 1
            m = at(cx + 17, cy + 8)
            if m and not all(m[k] < 12 for k in range(3)):
                edgec += 1
    print(f"size1: fill centres {hitc}/{pts}, edge-mid non-black {edgec}/{pts}")
    if hitc < int(0.9 * pts):
        print("FAIL fill census"); ok = False
    if edgec < pts:  # exact tiling: NO midpoint may be starfield black
        print("FAIL gap detected at shared-edge midpoints"); ok = False
    print("VERDICT", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
