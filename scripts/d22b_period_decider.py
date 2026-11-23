#!/usr/bin/env python3
"""D22b: is the New Game field period ~5.3s (user stopwatch, x5) or
~180s (loop's 2deg/s)? Decisive test: red/green composites of star
masks. If stars move ~3 px/s, red+green dots overlap (yellow). If they
move ~119 px/s (68 deg/s, 5.3 s circuit), red/green pairs separate by
~120 px. Also: lag-5 similarity should DIP below lag-1 if period ~5.3s.
"""
import glob, re
import numpy as np
from PIL import Image

files = sorted(glob.glob('/home/hrethric/projects/ascendancy/scratchpad/Screenshot_2026-11-22_23-*.png'))
imgs = [np.asarray(Image.open(f).convert('RGB'), dtype=np.int16) for f in files]
OFFY, SC = 14, 0.8
def field(a):
    # big field window coords (0,0)-(200,290) already content-scaled at 0.8
    return a[OFFY:OFFY+int(290*SC), 0:int(200*SC)]

def stars(a, thr=300):
    m = a.sum(axis=2) > thr
    return m

def sep_stats(m1, m2, name):
    ys1, xs1 = np.nonzero(m1); ys2, xs2 = np.nonzero(m2)
    pts1 = np.stack([xs1, ys1], 1).astype(float)
    pts2 = np.stack([xs2, ys2], 1).astype(float)
    if len(pts1) == 0 or len(pts2) == 0:
        print(name, "empty"); return
    # nearest-neighbour distance from each frame-1 star to frame-2 stars
    d = np.linalg.norm(pts1[:, None, :] - pts2[None, :, :], axis=2).min(axis=1)
    print(f"{name}: n1={len(pts1)} nn-dist median={np.median(d):.1f} p25={np.percentile(d,25):.1f} p75={np.percentile(d,75):.1f} frac<4px={np.mean(d<4):.2f}")

print("== lag 1 ==")
for i in (0, 5, 10):
    sep_stats(stars(field(imgs[i])), stars(field(imgs[i+1])), f"t{i}->t{i+1}")
print("== lag 2 ==")
for i in (0, 5):
    sep_stats(stars(field(imgs[i])), stars(field(imgs[i+2])), f"t{i}->t{i+2}")
print("== lag 5 (period-5.3 predicts RE-correlation: high frac<4px) ==")
for i in (0, 4, 8):
    sep_stats(stars(field(imgs[i])), stars(field(imgs[i+5])), f"t{i}->t{i+5}")

# red/green composite: frame0 red, frame1 green, lag1 and lag5
def comp(i, j, path):
    m1 = stars(field(imgs[i])); m2 = stars(field(imgs[j]))
    H, W = m1.shape
    out = np.zeros((H, W, 3), dtype=np.uint8)
    out[:, :, 0] = m1 * 255
    out[:, :, 1] = m2 * 255
    Image.fromarray(out).resize((W*3, H*3), Image.NEAREST).save(path)
comp(0, 1, '/home/hrethric/projects/ascendancy/scratchpad/d22b-lag1-composite.png')
comp(0, 5, '/home/hrethric/projects/ascendancy/scratchpad/d22b-lag5-composite.png')
print("composites written (red=earlier frame, green=later; 3x zoom)")
