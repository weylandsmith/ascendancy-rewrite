#!/usr/bin/env python3
# t426c WITNESS CENSUS — run on the map screenshot the plaque witness
# already takes (/tmp/t426_map.png cropped to 640x480 by the caller, or
# pass the crop path). Checks the GRADIENT LAW on OUR render:
#   1. top band rows 0..6 x7..465 mean-lum profile descends monotonically
#      in envelope (mean(row0) >= 1.3*mean(row3) >= ... pattern) and row7
#      is black;
#   2. row0 is bright-family (all px lum>55) and row6 dark-family (all
#      lum<70) — the per-row census, not a flat mix;
#   3. right-edge strip x466..472 rows 60..460 mean lum >= 95 at cols
#      467/468 (the idx58/173 ridge shows through our paint).
# Prints VERDICT PASS/FAIL. Law docs/re/_wip_t426.md F6.
import sys
import numpy as np
from PIL import Image

path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/t426c_map_crop.png"
img = np.asarray(Image.open(path).convert("RGB"))
assert img.shape[:2] >= (480, 640), img.shape


def lum(a):
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


fails = []
means = [float(lum(img[y, 7:466]).mean()) for y in range(7)]
print("top band row means:", " ".join(f"{m:.1f}" for m in means))
if not (means[0] >= 1.3 * means[3] and means[3] >= 1.5 * means[6]):
    fails.append("gradient envelope")
r0 = lum(img[0, 7:466])
r6 = lum(img[6, 7:466])
f0 = float((r0 > 55).mean())
f6 = float((r6 < 70).mean())
print(f"row0 lum>55 frac {f0:.3f}  row6 lum<70 frac {f6:.3f}")
if f0 < 0.95 or f6 < 0.90:
    fails.append("per-row families")
black7 = float((img[7, 7:466].sum(axis=-1) == 0).mean())
print(f"row7 black frac {black7:.3f}")
if black7 < 0.999:
    fails.append("field edge row7 not black")
strip = lum(img[60:460, 466:473]).mean(axis=0)
print("right strip col means:", " ".join(f"{m:.1f}" for m in strip))
if not (strip[1] >= 95 and strip[2] >= 95):
    fails.append("right-edge ridge")
print("VERDICT", "FAIL:" + ",".join(fails) if fails else "PASS")
sys.exit(1 if fails else 0)
