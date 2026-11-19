#!/usr/bin/env python3
"""t426 probe 1: the vendor map BORDER around COSMOSWnd.

Authority: docs/assets/refcap/original-strategic-map.png, png = screen + 40
(t425c law), palette-pure (palette.md S3). COSMOSWnd rect (windows.txt ln200):
7,7..465,472. In png coords the window is 7,47..465,512 (bottom CLIPPED at
row 479). This probe prints exact RGB runs along:
  TOP    : png rows 38..52 (screen -2..12) across x 60..420 (mid-field, away
           from the right-column widgets)
  LEFT   : png cols 0..14 (screen -0..10) down rows 60..460
  RIGHT  : png cols 460..486 (screen 420..446) at rows 100, 200, 300, 400
  CORNER : png 0..20 x 38..58 (upper-left corner block, doubles as F2 lead)
Bottom border only exists in scratchpad/galaxymap-original.png (identity map):
rows 468..481 at x 60..420 -- printed separately, flagged non-pure.
Read-only census; exit 0.
"""
import collections

import numpy as np
from PIL import Image

REF = np.asarray(Image.open(
    "docs/assets/refcap/original-strategic-map.png").convert("RGB"))
SCR = np.asarray(Image.open(
    "scratchpad/galaxymap-original.png").convert("RGB"))
PAL = open("extracted/ascend01/data/game.pal", "rb").read()
conv = [(PAL[3*i] * 255 // 63, PAL[3*i+1] * 255 // 63, PAL[3*i+2] * 255 // 63)
        for i in range(256)]
cmap = {c: i for i, c in enumerate(conv)}


def runs(seq):
    out = []
    for px in seq:
        t = tuple(int(v) for v in px)
        idx = cmap.get(t, None)
        lab = f"{idx}" if idx is not None else f"OFF{t}"
        if out and out[-1][0] == lab:
            out[-1][1] += 1
        else:
            out.append([lab, 1])
    return " ".join(f"{l}x{n}" for l, n in out)


print("== TOP rows (png y, screen y = png-40), x 60..420 ==")
for y in range(38, 53):
    print(f"y{y:3d}(s{y-40:3d}): {runs(REF[y, 60:421])}")

print("\n== LEFT cols (png x = screen x), rows 60..460 ==")
for x in range(0, 15):
    col = collections.Counter(tuple(int(v) for v in p) for p in REF[60:461, x])
    top = col.most_common(4)
    print(f"x{x:2d}: " + " | ".join(
        f"{cmap.get(c,'OFF'+str(c))}:{n*100//401}%" for c, n in top))

print("\n== RIGHT transition, cols 460..487 (screen 420..447) ==")
for y in (100, 200, 300, 400):
    print(f"y{y}: {runs(REF[y, 460:488])}")

print("\n== CORNER block png x0..24 y38..62 (ASCII, '.'=black) ==")
for y in range(38, 63):
    line = ""
    for x in range(0, 25):
        c = tuple(int(v) for v in REF[y, x])
        lum = 0.2126*c[0] + 0.7152*c[1] + 0.0722*c[2]
        line += "#" if lum > 140 else ("+" if lum > 60 else ("-" if lum > 15 else "."))
    print(f"y{y:3d}(s{y-40:3d}): {line}")

print("\n== SCRATCHPAD bottom rows 466..480 x 60..420 (identity, NON-PURE) ==")
for y in range(466, min(481, SCR.shape[0])):
    print(f"y{y:3d}: {runs(SCR[y, 60:421])[:220]}")
print("\nscratchpad shape", SCR.shape, "ref shape", REF.shape)
