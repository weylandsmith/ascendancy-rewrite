#!/usr/bin/env python3
# t417: register 10status k0 (decoded index plane) against the t3 VENDOR
# capture of the status screen, through game.pal (post-t398 colour law).
# Answers: does the vendor paint k0 at shift 0? Which regions match?
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
import r1_shp_unifiedlaw as U

LIB = sys.argv[1] if len(sys.argv) > 1 else "extracted/ascend01/data/10status.shp"
SHOT = sys.argv[2] if len(sys.argv) > 2 else "/tmp/t417_t3_game640.png"

d, count, te, tsz, starts, ends = U.parse(LIB)
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "t391_registration.py")).read()
ns = {"__file__": __file__}
exec(src.split("shot_path, lib_path")[0], ns)
vals, mask, w0, h = ns["plane_and_mask"](d, starts, ends, 0)
plane = np.array(vals, dtype=np.int32).reshape(h, w0)
written = plane >= 0
print(f"plane {w0}x{h} written {int(written.sum())}")

pal_raw = open("extracted/ascend01/data/game.pal", "rb").read()
assert len(pal_raw) == 768, len(pal_raw)
lut = np.zeros((256, 3), dtype=np.int32)
for j in range(256):
    for c in range(3):
        v = pal_raw[j * 3 + c]
        lut[j, c] = (v << 2) | (v >> 4)

shot = np.array(Image.open(SHOT).convert("RGB")).astype(np.int32)
print("shot", shot.shape)

H, W = shot.shape[:2]
mh, mw = min(H, h), min(W, w0)
sub = plane[:mh, :mw]
wmask = sub >= 0
rgb = lut[sub[wmask].clip(0, 255)]
sp = shot[:mh, :mw][wmask]
diff = np.abs(rgb - sp).sum(axis=1)
print(f"shift(0,0): written px {int(wmask.sum())}, exact {int((diff==0).sum())} "
      f"({(diff==0).mean():.3f}), <=30 {(diff<=30).mean():.3f}, mean|d| {diff.mean():.1f}")

ok = np.zeros((mh, mw))
ok[wmask] = (diff <= 30)
def zone(y0, y1, x0, x1, name):
    w = wmask[y0:y1, x0:x1]
    if w.sum() == 0:
        print(name, "no written px")
        return
    print(name, f"written {int(w.sum())} matchfrac {ok[y0:y1,x0:x1][w].mean():.3f}")
zone(0, 40, 0, 639, "header y0-40")
zone(40, 116, 0, 639, "tablehdr y40-116")
zone(116, 470, 0, 619, "rows zone")
zone(48, 476, 619, 639, "scroll col")
zone(250, 470, 480, 619, "right panel (TOTEM/MOBY in k0)")

iz = plane[120:460, 10:610]
import collections
c = collections.Counter(iz[iz >= 0].tolist())
print("interior written idx top", c.most_common(6))
for idx, _ in c.most_common(3):
    print("idx", idx, "rgb", lut[idx])
sp2 = shot[120:460, 10:610]
c2 = collections.Counter(map(tuple, sp2.reshape(-1, 3)))
print("interior shot top colours", c2.most_common(4))
