#!/usr/bin/env python3
"""tNGS4 offline rate analysis on run tngs4-20261123-010308 frames.
Peak census + consecutive matching + angular fit + lag curve."""
import glob
import sys
import numpy as np
from PIL import Image

RUN = sys.argv[1] if len(sys.argv) > 1 else \
    "work/r1/tngs4-20261123-010308"
FR = sorted(glob.glob(f"{RUN}/caps/frames/f*.png"))
print("frames", len(FR))


def lum(im, box):
    a = np.asarray(im.crop(box), dtype=np.float64)
    return 0.299 * a[:, :, 0] + 0.587 * a[:, :, 1] + 0.114 * a[:, :, 2]


def peaks(arr, lum_min=120.0):
    h, w = arr.shape
    p = np.pad(arr, 1, constant_values=0.0)
    mx = p[1:-1, 1:-1].copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            np.maximum(mx, p[1 + dy:1 + dy + h, 1 + dx:1 + dx + w], out=mx)
    m = (arr >= mx) & (arr > lum_min)
    ys, xs = np.nonzero(m)
    return np.stack([xs, ys], axis=1).astype(float)


ims = [Image.open(f) for f in FR]
A = [lum(im, (17, 12, 324, 320)) for im in ims]
pk = [peaks(a) for a in A]
print("peaks per frame:", [len(p) for p in pk[:12]])

# consecutive matching at several tolerances
rows = []
for i in range(len(pk) - 1):
    pa, pb = pk[i], pk[i + 1]
    if len(pa) == 0 or len(pb) == 0:
        continue
    d2 = ((pa[:, None, 0] - pb[None, :, 0]) ** 2 +
          (pa[:, None, 1] - pb[None, :, 1]) ** 2)
    j = np.argmin(d2, axis=1)
    dmin = np.sqrt(d2[np.arange(len(pa)), j])
    sel = dmin <= 6.0
    n = int(sel.sum())
    med = float(np.median(dmin[sel])) if n else None
    # angular about centre
    dth = None
    if n:
        cy, cx = A[0].shape[0] / 2.0, A[0].shape[1] / 2.0
        q = pb[j[sel]]
        p0 = pa[sel]
        v1 = p0 - np.array([cx, cy])
        v2 = q - np.array([cx, cy])
        r = np.hypot(v1[:, 0], v1[:, 1])
        ok = r >= 40.0
        if ok.sum() >= 2:
            cross = v1[ok, 0] * v2[ok, 1] - v1[ok, 1] * v2[ok, 0]
            dot = v1[ok, 0] * v2[ok, 0] + v1[ok, 1] * v2[ok, 1]
            th = np.degrees(np.arctan2(cross, dot))
            dth = (float(np.median(th)), float(np.median(np.abs(th))),
                   int(ok.sum()))
    rows.append((i + 1, len(pa), len(pb), n, med, dth))
    print(f"step {rows[-1][0]:2d}: {len(pa)}/{len(pb)} n={n} "
          f"disp_med={med} dth={dth}")

ns = np.array([r[3] for r in rows])
dms = np.array([r[4] for r in rows if r[4] is not None])
print("\nmatched/steps: median n =", np.median(ns),
      " disp median =", np.median(dms) if len(dms) else None)

# lag curve on changed-px (>30/chan law)
RAW = [np.asarray(im.crop((17, 12, 324, 320)), dtype=np.int16) for im in ims]
def changed(a, b):
    return int(((np.abs(a - b) > 30).any(axis=2)).sum())

print("\nlag curve (changed px vs f_i):")
for lag in (1, 2, 3, 4, 5, 8):
    vals = [changed(RAW[i], RAW[i + lag]) for i in range(0, len(RAW) - lag, 2)]
    print(f"  lag {lag}: median {int(np.median(vals))}")

# rotation-correlation on the peak clouds: for pair (0, k) find best theta
def rot_score(pa, pb, theta_deg, tol=4.0):
    t = np.radians(theta_deg)
    cy, cx = A[0].shape[0] / 2.0, A[0].shape[1] / 2.0
    v = pa - np.array([cx, cy])
    rx = v[:, 0] * np.cos(t) - v[:, 1] * np.sin(t)
    ry = v[:, 0] * np.sin(t) + v[:, 1] * np.cos(t)
    r = np.stack([rx + cx, ry + cy], axis=1)
    d2 = ((r[:, None, 0] - pb[None, :, 0]) ** 2 +
          (r[:, None, 1] - pb[None, :, 1]) ** 2)
    return int((d2.min(axis=1) <= tol * tol).sum())

print("\nrotation-correlation f1 vs f6 (5 s apart, expect 10 deg @ 2deg/s):")
for th in range(-14, 15, 2):
    print(f"  theta {th:+3d}: {rot_score(pk[0], pk[5], th)}")
