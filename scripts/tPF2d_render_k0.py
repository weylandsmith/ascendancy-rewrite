#!/usr/bin/env python3
# tPF-2d step 3 evidence: render help.shp k0 (verbatim codec law, shp.md S9)
# and crop the refcap popup at the PLSQUARE logical rect. Scratch tool.
import sys, struct, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from r1_shp_decode_law import parse
from PIL import Image

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
d, count, te, starts, spans = parse("extracted/ascend01/data/help.shp")
w0, h0 = struct.unpack_from("<II", d, starts[0])
W, H = w0 + 1, h0 + 1
pal = open("extracted/ascend01/data/game.pal", "rb").read()
idx = bytearray(W * H)
i = starts[0] + 8
for r in range(H):
    x = 0
    while i < starts[0] + spans[0]:
        c = d[i]; i += 1
        if c == 0: break
        if c == 1:
            x += d[i]; i += 1; continue
        n = c >> 1
        if c & 1:
            for k in range(n):
                if x < W: idx[r * W + x] = d[i + k]
                x += 1
            i += n
        else:
            v = d[i]; i += 1
            for xx in range(x, min(x + n, W)): idx[r * W + xx] = v
            x += n
img = Image.new("P", (W, H))
img.putdata(list(idx))
img.putpalette(list(pal[:768]))
img.convert("RGB").save("work/r1/tPF2d_help_k0.png")
# colour census of the k0 border band vs interior
rgb = img.convert("RGB").load()
from collections import Counter
border = Counter(rgb[x, y] for x in range(W) for y in (0, 1, H-1, H-2))
border += Counter(rgb[x, y] for y in range(H) for x in (0, 1, W-1, W-2))
inner = Counter(rgb[x, y] for y in range(20, H-20, 4) for x in range(20, W-20, 4))
print("k0 border top colours:", border.most_common(5))
print("k0 interior top colours:", inner.most_common(5))
im = Image.open("scratchpad/original-planet-screen-click-on-square-adjacent-to-structure.png").convert("RGB")
s = 512 / 640
crop = im.crop((int(152*s), int(120*s), int(488*s), int(376*s)))
crop.save("work/r1/tPF2d_refcap_popup_crop.png")
cp = crop.load()
cb = Counter(cp[x, y] for x in range(crop.width) for y in (0, 1, 2, crop.height-3, crop.height-2, crop.height-1))
print("refcap crop border top colours:", cb.most_common(6))
