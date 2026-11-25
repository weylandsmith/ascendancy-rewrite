#!/usr/bin/env python3
"""tPF-3c TPF3-B: interior census of class-colour overlay outlines in the 433
refcap — the NON-teal discriminator for the fill no-op claim.

F6 measured the teal field (20,495 px EXACTLY conv(150)) and concluded the
polygon filler 0x62d15 (state block [0x48c33]+pen*0x100) is a NO-OP at the
captured state. The assignment demands the claim hold for a NON-teal cell:
red(117)/green(146)/blue(255) class lines exist in the 433 refcap (tPF3c_
fill_census: green 128 / blue 101 / red 19 exact-conv px). If the fill painted
its class colour, a blob of class-family px would sit INSIDE the outlined
diamond; a no-op leaves the interior the same colour as the surrounding field.

Method: exact-conv mask per class (TOL 12), connected-component cluster the
LINE px (8-neighbour, min 8 px), then for each cluster census the interior:
the pixels strictly inside the cluster's bounding diamond shrunk to 70%
(keeps 1px lines out). Report interior colour histogram vs the field colour
immediately OUTSIDE the cluster bbox dilated 6px. NO-OP: interior histogram ==
outside histogram (modulo line px). FILL: interior carries class-family px the
outside lacks.
"""
import os, sys
from collections import Counter, deque
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PNG = os.path.join(ROOT, "scratchpad/planet-screen-iter-433-v-original.png")
PAL = open(os.path.join(ROOT, "extracted/ascend01/data/game.pal"), "rb").read()

def conv(i):
    r, g, b = PAL[3 * i], PAL[3 * i + 1], PAL[3 * i + 2]
    return (int((r << 2) | (r >> 4)), int((g << 2) | (g >> 4)), int((b << 2) | (b >> 4)))

CLS = {"red": conv(117), "green": conv(146), "blue": conv(255)}
TEAL = conv(150)
TOL = 12

def q(c):
    return (c[0] // 8 * 8, c[1] // 8 * 8, c[2] // 8 * 8)

def main():
    im = np.asarray(Image.open(PNG).convert("RGB")).astype(np.int16)
    H, W, _ = im.shape
    for name, c in CLS.items():
        d = np.abs(im - np.array(c, dtype=np.int16)).max(axis=2)
        m = d <= TOL
        n = int(m.sum())
        print(f"== {name} conv={c} exact px={n}")
        if n == 0:
            continue
        ys, xs = np.nonzero(m)
        pts = set(zip(xs.tolist(), ys.tolist()))
        seen = set()
        clusters = []
        for p0 in pts:
            if p0 in seen:
                continue
            comp = set()
            dq = deque([p0])
            while dq:
                x, y = dq.popleft()
                if (x, y) in comp:
                    continue
                comp.add((x, y))
                seen.add((x, y))
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        nb = (x + dx, y + dy)
                        if nb in pts and nb not in comp:
                            dq.append(nb)
            clusters.append(comp)
        clusters.sort(key=len, reverse=True)
        for ci, comp in enumerate(clusters[:6]):
            a = np.array(sorted(comp))
            x0, y0 = a[:, 0].min(), a[:, 1].min()
            x1, y1 = a[:, 0].max(), a[:, 1].max()
            wpx, hpx = x1 - x0 + 1, y1 - y0 + 1
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            # interior: inside 0.65-scaled diamond of the cluster bbox
            ins = []
            rx, ry = max(2, wpx * 0.325), max(2, hpx * 0.325)
            for yy in range(int(cy - ry), int(cy + ry) + 1):
                for xx in range(int(cx - rx), int(cx + rx) + 1):
                    if not (0 <= xx < W and 0 <= yy < H):
                        continue
                    if abs(xx - cx) / rx + abs(yy - cy) / ry <= 1.0:
                        ins.append((xx, yy))
            # outside ring: bbox dilated 6px minus bbox dilated 2px
            out = []
            for yy in range(y0 - 6, y1 + 7):
                for xx in range(x0 - 6, x1 + 7):
                    if not (0 <= xx < W and 0 <= yy < H):
                        continue
                    if x0 - 2 <= xx <= x1 + 2 and y0 - 2 <= yy <= y1 + 2:
                        continue
                    out.append((xx, yy))
            def hist(pxs):
                cc = Counter()
                classfam = 0
                for (xx, yy) in pxs:
                    p = im[yy, xx]
                    cc[q(tuple(int(v) for v in p))] += 1
                    if abs(p - np.array(c, dtype=np.int16)).max() <= 30:
                        classfam += 1
                return cc, classfam
            hi, cf_in = hist(ins)
            ho, cf_out = hist(out)
            print(f"  cluster{ci}: n={len(comp)} bbox=({x0},{y0})-({x1},{y1}) "
                  f"size={wpx}x{hpx}")
            print(f"    interior n={len(ins)} classfam30={cf_in} top=" +
                  str(hi.most_common(4)))
            print(f"    outside  n={len(out)} classfam30={cf_out} top=" +
                  str(ho.most_common(4)))

if __name__ == "__main__":
    main()
