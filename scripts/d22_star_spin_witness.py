#!/usr/bin/env python3
"""D22 starfield rotation witness (assistant, 2026-11-22).

User ruling: BOTH New Game starfields spin continuously, period ~5 s,
mouse position irrelevant. Evidence: 15 Athens refcap shots
scratchpad/Screenshot_2026-11-22_23-*.png at ~1 s spacing (window
512x398 incl titlebar => content offset y ~14, scale 0.8).

Method: per-region changed-pixel counts between consecutive shots and
between shots ~5 s apart. Regions (content coords, x0,y0,x1,y1):
  big field  : whole left star area  (0,0)-(200,290)
  begin field: Begin-panel circle    (415,325)-(455,365)
  control    : text strip, should be STATIC (170,300)-(330,320)
"""
import glob, re
import numpy as np
from PIL import Image

files = sorted(glob.glob('/home/hrethric/projects/ascendancy/scratchpad/Screenshot_2026-11-22_23-*.png'))
ts = [int(re.search(r'23-(\d\d)-(\d\d)', f).group(1)) * 60 + int(re.search(r'23-(\d\d)-(\d\d)', f).group(2)) for f in files]
imgs = [np.asarray(Image.open(f).convert('RGB'), dtype=np.int16) for f in files]
print(f"{len(files)} shots, t={ts[0]%60}..{ts[-1]%60}s, shape={imgs[0].shape}")

def region(a, r, offy=14, sc=0.8):
    x0, y0, x1, y1 = [int(v * sc) for v in r]
    return a[offy + y0:offy + y1, x0:x1]

REG = {
    'big':   (0, 0, 200, 290),
    'begin': (415, 325, 455, 365),
    'ctrl':  (170, 300, 330, 320),
}

def changed(a, b, r):
    ra, rb = region(a, r), region(b, r)
    if ra.shape != rb.shape:
        return -1
    d = np.abs(ra - rb).sum(axis=2)
    return int((d > 30).sum())

print("\nconsecutive-pair changed pixels (dt, big, begin, ctrl):")
for i in range(len(files) - 1):
    dt = ts[i+1] - ts[i]
    row = [changed(imgs[i], imgs[i+1], r) for r in REG.values()]
    print(f"  {ts[i]%60:>2}->{ts[i+1]%60:<2} dt={dt}  big={row[0]:>5}  begin={row[1]:>5}  ctrl={row[2]:>4}")

print("\nlag ~5 s changed pixels (period test: low count at lag 5 => 5 s circuit):")
for lag in (4, 5, 6):
    out = []
    for i in range(len(files) - lag):
        dt = ts[i+lag] - ts[i]
        if abs(dt - 5) <= 1:
            out.append((ts[i]%60, dt, *[changed(imgs[i], imgs[i+lag], r) for r in REG.values()]))
    for o in out:
        print(f"  t={o[0]:>2} dt={o[1]}  big={o[2]:>5}  begin={o[3]:>5}  ctrl={o[4]:>4}")
