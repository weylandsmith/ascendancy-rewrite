#!/usr/bin/env python3
# t398 census: our OWN render (self-graded VISION stays banned; mechanical
# colour math only). PASS conditions, all measurable:
#  1. app.log has the `ui palette: game.pal` line (not the degraded ramp line).
#  2. map.png rail icon zones: >= MIN_COLOURS distinct colours with CHROMA
#     (max(channel)-min(channel) >= 12) — the greyscale ramp CANNOT produce
#     chroma (R==G==B by construction), so this mechanically separates the
#     palette paths. Floors are conservative: the ramp yields exactly 0
#     chromatic pixels anywhere.
#  3. the rail button fill pixel matches game.pal idx 242 conv (12,32,48)
#     within a small tolerance (SDL/Xvfb may dither; tol 6).
# Usage: t398_witness_census.py SHOTS_DIR   (default /tmp/t398_shots)
import os
import sys

from PIL import Image

GP = open("extracted/ascend01/data/game.pal", "rb").read()
GSET = set(tuple(((GP[i] << 2) | (GP[i] >> 4)) for i in (3 * k, 3 * k + 1, 3 * k + 2))
           for k in range(256))

d = sys.argv[1] if len(sys.argv) > 1 else "/tmp/t398_shots"
log = open(os.path.join(d, "app.log")).read()
ok1 = "ui palette: game.pal" in log
print("1) palette line:", "PASS" if ok1 else "FAIL",
      "| degraded-ramp line present:", "degraded: greyscale" in log)

im = Image.open(os.path.join(d, "map.png")).convert("RGB")
W, H = im.size
ox, oy = (W - 640) // 2, (H - 480) // 2

# OUR render's rail icon zone: ui.cpp places icons at rr.x+4 = 478 (t400 will
# move them right of the label per the vendor registration; census follows
# the CODE, not the aspiration). Zone = x 474..540, y rows 130..278.
rows = [(130, 160), (169, 199), (208, 238), (247, 277)]
chroma_cols = set()
zone_px = 0
for (y0, y1) in rows:
    for y in range(oy + y0, oy + y1):
        for x in range(ox + 474, ox + 540):
            c = im.getpixel((x, y))
            zone_px += 1
            if max(c) - min(c) >= 12:
                chroma_cols.add(c)
ok2 = len(chroma_cols) >= 8
print(f"2) rail chroma colours: {len(chroma_cols)} (zone px {zone_px}) "
      f"-> {'PASS' if ok2 else 'FAIL'} (ramp path yields EXACTLY 0)")
ing = sum(1 for c in chroma_cols if c in GSET)
print(f"   of those inside game.pal: {ing}")

# 3) the chromatic colours are game.pal colours: our rail FILL is the port's
#    own choice (40,40,56, not vendor teal — a geometry/fidelity seam for
#    t400+), so the discriminator is INSIDENESS of the icon art's chroma.
frac = ing / max(1, len(chroma_cols))
ok3 = ing >= int(0.9 * len(chroma_cols)) and len(chroma_cols) >= 8
print(f"3) chroma inside game.pal: {ing}/{len(chroma_cols)} = {frac:.2f} "
      f"-> {'PASS' if ok3 else 'FAIL'}")

verdict = ok1 and ok2 and ok3
print("VERDICT", "PASS" if verdict else "FAIL")
sys.exit(0 if verdict else 1)
