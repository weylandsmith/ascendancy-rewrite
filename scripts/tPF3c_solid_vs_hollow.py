#!/usr/bin/env python3
"""tPF-3c TPF3-B discriminator: solid-filled coloured tiny diamonds vs hollow
black tiny diamond in the 433 refcap right half.

Byte law (work/tPF3b_inset.asm): BOTH overlay branches reach the shared filler
0x62d15 at 0x3be39 with state block [0x48c33]+pen*0x100, and BOTH skip the
fill when pen == 0 (inset 0x3bd31 'test di,di / je 0x3be53'; tiny 0x3be2a
'test si,si / je'). So if the state block fill paints the class colour, the
prediction on any capture is: CLASS-0 (black) diamonds = outline only (hollow,
interior == tile field), NON-BLACK class diamonds = interior == class colour.

Probe: locate every compact class-colour blob (exact-conv TOL 12, cluster
diameter <= 40 ref px) for red 117 / green 146 / blue 255 / white 12, and for
BLACK do the same but restricted to blobs whose outline is closed (a black
hollow diamond has a field-coloured middle). Report per blob: bbox, class-family
fraction of the 0.5-scaled central diamond vs the dilated outside ring.
"""
import os
from collections import Counter, deque
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PNG = os.path.join(ROOT, "scratchpad/planet-screen-iter-433-v-original.png")
PAL = open(os.path.join(ROOT, "extracted/ascend01/data/game.pal"), "rb").read()

def conv(i):
    r, g, b = PAL[3 * i], PAL[3 * i + 1], PAL[3 * i + 2]
    return (int((r << 2) | (r >> 4)), int((g << 2) | (g >> 4)), int((b << 2) | (b >> 4)))

CLS = {"red": conv(117), "green": conv(146), "blue": conv(255), "white": conv(12)}
TOL, FTOL = 12, 30

def clusters(mask, maxdim=40):
    ys, xs = np.nonzero(mask)
    pts = set(zip(xs.tolist(), ys.tolist()))
    seen, out = set(), []
    for p0 in pts:
        if p0 in seen:
            continue
        comp, dq = set(), deque([p0])
        while dq:
            x, y = dq.popleft()
            if (x, y) in comp:
                continue
            comp.add((x, y)); seen.add((x, y))
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nb = (x + dx, y + dy)
                    if nb in pts and nb not in comp:
                        dq.append(nb)
        a = np.array(sorted(comp))
        w, h = a[:, 0].max() - a[:, 0].min() + 1, a[:, 1].max() - a[:, 1].min() + 1
        if w <= maxdim and h <= maxdim:
            out.append(comp)
    return out

def main():
    im = np.asarray(Image.open(PNG).convert("RGB")).astype(np.int16)
    H, W, _ = im.shape
    for name, c in CLS.items():
        d = np.abs(im - np.array(c, dtype=np.int16)).max(axis=2)
        cl = clusters(d <= TOL)
        if not cl:
            print(f"{name}: no compact blobs"); continue
        print(f"== {name} conv={c}: {len(cl)} compact blob(s)")
        for comp in sorted(cl, key=len, reverse=True)[:8]:
            a = np.array(sorted(comp))
            x0, y0 = a[:, 0].min(), a[:, 1].min()
            x1, y1 = a[:, 0].max(), a[:, 1].max()
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            rx, ry = max(1.5, (x1 - x0 + 1) * 0.25), max(1.5, (y1 - y0 + 1) * 0.25)
            nin = nclass = nout = oclass = 0
            for yy in range(int(cy - ry), int(cy + ry) + 1):
                for xx in range(int(cx - rx), int(cx + rx) + 1):
                    if abs(xx - cx) / rx + abs(yy - cy) / ry <= 1.0 and 0 <= xx < W and 0 <= yy < H:
                        nin += 1
                        if np.abs(im[yy, xx] - np.array(c, dtype=np.int16)).max() <= FTOL:
                            nclass += 1
            for yy in range(y0 - 8, y1 + 9):
                for xx in range(x0 - 8, x1 + 9):
                    if not (0 <= xx < W and 0 <= yy < H):
                        continue
                    if x0 - 3 <= xx <= x1 + 3 and y0 - 3 <= yy <= y1 + 3:
                        continue
                    nout += 1
                    if np.abs(im[yy, xx] - np.array(c, dtype=np.int16)).max() <= FTOL:
                        oclass += 1
            print(f"   bbox=({x0},{y0})-({x1},{y1}) n={len(comp)} "
                  f"centre-class {nclass}/{nin} outside-class {oclass}/{nout}")

if __name__ == "__main__":
    main()
