#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# t424b witness census: OUR race-intro render graded MECHANICALLY against the
# measured vendor law (docs/re/_wip_t424b.md F1/F2). Run with
# ~/tools/revenv/bin/python scripts/t424b_witness_census.py [shot.png]
import sys
import numpy as np
from PIL import Image

path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/t424b_shots/t424b-raceintro.png"
im = np.asarray(Image.open(path).convert("RGB")).astype(int)
if im.shape[:2] != (480, 640):
    print(f"FAIL frame size {im.shape[:2]} != (480,640)"); sys.exit(1)

fails = 0
def chk(name, ok, detail=""):
    global fails
    print(("PASS " if ok else "FAIL ") + name + (" " + detail if detail else ""))
    if not fails and not ok: fails = 1

DARK = [(0,0,0),(12,12,16),(12,12,12),(12,28,48)]
def dmin(px):  # squared distance to nearest dark family colour
    return np.minimum.reduce([((px - c) ** 2).sum(-1) for c in DARK])

# F1 boundary law: margins chrome-class, interior dark-class dominated.
# (Interior checks use the RIGHT WELL + BODY well — the left band holds the
# lgrace portrait ART, which is legitimately not dark-family.)
inter = im[50:240, 316:626]
dm = dmin(inter)
share = float((dm <= 800).mean())
chk("right well dark-family share >= 0.85", share >= 0.85, f"share={share:.3f}")
body = im[265:458, 12:626]
dm2 = dmin(body)
share2 = float((dm2 <= 800).mean())
chk("body well dark-family share >= 0.85", share2 >= 0.85, f"share={share2:.3f}")
marg = np.concatenate([im[60:240, 0:7].reshape(-1,3), im[60:240, 634:640].reshape(-1,3)])
dark_share_marg = float((np.minimum.reduce([((marg-c)**2).sum(-1) for c in DARK]) <= 800).mean())
chk("side margins NOT dark (chrome page)", dark_share_marg <= 0.25, f"dark={dark_share_marg:.3f}")

# F2 census shares among dark pixels (approximate bands; chain-correlated)
dk = body.reshape(-1,3)[dm2.reshape(-1) <= 800]
tot = len(dk)
for col, lo, hi, nm in [((0,0,0),0.25,0.55,'idx0'), ((12,12,16),0.15,0.45,'idx200'),
                        ((12,12,12),0.10,0.40,'idx1'), ((12,28,48),0.01,0.15,'idx196')]:
    s = float((dk == np.array(col)).all(-1).mean())
    chk(f"body dark census {nm} in [{lo},{hi}]", lo <= s <= hi, f"s={s:.3f}")

# grain: CORRELATION test (not a lag-profile test — the vendor shot is
# 1.6266x-scaled and its lag profile cannot be graded against an unscaled
# render; named seam _wip_t424b F2). Chain law => same-colour adjacency rate
# > iid expectation 0.315 (iid sim through the same shot pipeline measures
# 0.30-0.33; the 5/25 chain measures ~0.35 unscaled).
dk4 = np.argmin(np.stack([((body - c) ** 2).sum(-1) for c in DARK]), axis=0)
darkpx = dm2 <= 800
same = float((dk4[:, :-1] == dk4[:, 1:])[darkpx[:, :-1] & darkpx[:, 1:]].mean())
chk("grain correlated (same-colour adjacency > 0.33)", same > 0.33, f"rate={same:.3f}")

print("VERDICT", "PASS" if fails == 0 else "FAIL")
sys.exit(fails)
