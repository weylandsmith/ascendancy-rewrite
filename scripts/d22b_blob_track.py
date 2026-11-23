#!/usr/bin/env python3
"""D22b take 2: track STAR BLOBS (not raw bright pixels) between
consecutive 1 s shots, chrome excluded. If median blob displacement
~3 px/s -> loop's 2deg/s. If ~119 px/s -> user's 5.3 s circuit.
"""
import glob
import numpy as np
from PIL import Image
class _Lab:
    """tiny union-find connected components (numpy masks are small here)"""
    def label(self, m):
        h, w = m.shape
        parent = {}
        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]; a = parent[a]
            return a
        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb: parent[rb] = ra
        ys, xs = np.nonzero(m)
        idx = {}
        for y, x in zip(ys, xs):
            key = (y, x); parent[key] = key; idx[key] = True
            for dy, dx in ((-1,0),(0,-1),(-1,-1),(-1,1)):
                n = (y+dy, x+dx)
                if n in idx: union(key, n)
        groups = {}
        for k in idx:
            groups.setdefault(find(k), []).append(k)
        return list(groups.values())

files = sorted(glob.glob('/home/hrethric/projects/ascendancy/scratchpad/Screenshot_2026-11-22_23-*.png'))
imgs = [np.asarray(Image.open(f).convert('RGB'), dtype=np.int16) for f in files]
OFFY = 14
def field(a):
    return a[OFFY:OFFY+int(290*0.8), int(35*0.8):int(200*0.8)]  # skip left chrome band

def blobs(a, _lab=_Lab()):
    lum = a.sum(axis=2)
    m = lum > 330
    out = []
    for comp in _lab.label(m):
        if 1 <= len(comp) <= 12:   # star-sized; big comps are text/chrome
            ys = [p[0] for p in comp]; xs = [p[1] for p in comp]
            out.append((float(np.mean(xs)), float(np.mean(ys)), lum[max(ys), max(xs)]))
    return np.array(out) if out else np.zeros((0, 3))

print("blob tracking, consecutive 1s frames:")
for i in range(len(files)-1):
    b1, b2 = blobs(field(imgs[i])), blobs(field(imgs[i+1]))
    if len(b1) == 0 or len(b2) == 0: continue
    d = np.linalg.norm(b1[:, None, :2] - b2[None, :, :2], axis=2)
    nn = d.min(axis=1)
    moved = b1[nn > 2.0]
    print(f" t{i}->{i+1}: n1={len(b1)} n2={len(b2)} median_nn={np.median(nn):.1f}px "
          f"frac<2px={np.mean(nn<2):.2f} moved_blobs={len(moved)}")

print("\nblob lag-5 (period ~5.3s => stars return => median_nn small AND same blobs):")
for i in (0, 4, 8):
    b1, b2 = blobs(field(imgs[i])), blobs(field(imgs[i+5]))
    d = np.linalg.norm(b1[:, None, :2] - b2[None, :, :2], axis=2)
    nn = d.min(axis=1)
    print(f" t{i}->t{i+5}: n1={len(b1)} median_nn={np.median(nn):.1f}px frac<2px={np.mean(nn<2):.2f}")
