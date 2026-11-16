#!/usr/bin/env python3
# t411 measurement pass: vendor original vs rewrite map shots.
#  1. bevel/frame census around COSMOSWnd 7,7-465,472 (vendor) and ours
#  2. digit-face style census in TURNCOUNT 474,7-632,43 (vendor) vs ours
#  3. rail texture: structured-dither vs random-static (autocorr)
#  4. star pip size distribution in the vendor starfield
from PIL import Image
import numpy as np

V = np.asarray(Image.open('scratchpad/galaxymap-original.png').convert('RGB'))
O = np.asarray(Image.open('work/r1/loop/walk/map_view.png').convert('RGB'))
print('vendor', V.shape, 'ours', O.shape)

def px(a, x, y): return tuple(int(v) for v in a[y, x])

print('\n== 1. bevel census: horizontal scan across left edge y=240 (vendor) ==')
for x in range(0, 30): print(' x', x, px(V, x, 240))
print('-- top edge x=240 (vendor) --')
for y in range(0, 20): print(' y', y, px(V, 240, y))
print('-- right edge of cosmos y=240 x=455..480 (vendor) --')
for x in range(455, 481): print(' x', x, px(V, x, 240))
print('-- bottom edge x=240 y=460..481 (vendor) --')
for y in range(460, min(481, V.shape[0])): print(' y', y, px(V, 240, y))

print('\n== ours: same scans ==')
for x in range(0, 20): print(' x', x, px(O, x, 240))
for y in range(0, 14): print(' y', y, px(O, 240, y))
for x in range(455, 481): print(' x', x, px(O, x, 240))

print('\n== 2. TURNCOUNT digit style (vendor rows y7..43, slots x 482/513/544/575/606) ==')
def style(a, x0, y0=7, y1=44, name=''):
    band = a[y0:y1, x0:x0+31].reshape(-1,3)
    # classify: green-ish (g>90 and g>r+30 and g>b+30), dark (all<40), other
    g = (band[:,1].astype(int) > 90) & (band[:,1].astype(int) > band[:,0].astype(int)+30) & (band[:,1].astype(int) > band[:,2].astype(int)+30)
    dk = (band.max(axis=1).astype(int) < 40)
    print(f' {name} x{x0}: green {g.mean()*100:.1f}% dark {dk.mean()*100:.1f}% n={len(band)}')
for xs in (482, 513, 544, 575, 606):
    style(V, xs, name='vendor')
for xs in (482, 513, 544, 575, 606):
    style(O, xs, name='ours  ')
# vendor digit colour histogram inside a slot
band = V[7:44, 482:513].reshape(-1,3)
u, c = np.unique(band, axis=0, return_counts=True)
top = np.argsort(-c)[:8]
print(' vendor slot top colours:', [(tuple(int(v) for v in u[i]), int(c[i])) for i in top])
band = O[7:44, 482:513].reshape(-1,3)
u, c = np.unique(band, axis=0, return_counts=True)
top = np.argsort(-c)[:8]
print(' ours   slot top colours:', [(tuple(int(v) for v in u[i]), int(c[i])) for i in top])

print('\n== 3. rail texture autocorr (sidebar x 474..632, y 340..360 band) ==')
def tex(a, name):
    b = a[340:360, 474:632].astype(float)
    h = b.mean(axis=2)
    # lag-1 horizontal neighbour difference vs random expectation
    d1 = np.abs(np.diff(h, axis=1)).mean()
    d0 = np.abs(h - h.mean()).mean()
    print(f' {name}: mean|dx| {d1:.2f} vs mean|dev| {d0:.2f} ratio {d1/max(d0,1e-9):.2f} (random->~1.4, smooth->low)')
    print(f'   colour count {len(np.unique(a[340:360,474:632].reshape(-1,3),axis=0))}')
tex(V, 'vendor')
tex(O, 'ours  ')

print('\n== 4. vendor star pip sizes: blob census in cosmos (non-black comps) ==')
def blobs(a, name):
    cos = a[8:471, 8:465]
    m = cos.max(axis=2).astype(int) > 60
    seen = np.zeros_like(m)
    from collections import deque
    sizes = []
    ys, xs = np.nonzero(m)
    for y, x in zip(ys, xs):
        if seen[y, x]: continue
        q = deque([(y,x)]); seen[y,x] = True; n = 0
        while q:
            cy, cx = q.popleft(); n += 1
            for dy in (-1,0,1):
                for dx in (-1,0,1):
                    ny, nx = cy+dy, cx+dx
                    if 0<=ny<m.shape[0] and 0<=nx<m.shape[1] and m[ny,nx] and not seen[ny,nx]:
                        seen[ny,nx]=True; q.append((ny,nx))
        if n <= 400: sizes.append(n)
    sizes.sort()
    import statistics
    print(f' {name}: {len(sizes)} blobs, sizes min {sizes[0]} med {statistics.median(sizes)} p90 {sizes[int(len(sizes)*0.9)]} max {sizes[-1]}')
    hist = {}
    for s in sizes: hist[min(s,20)] = hist.get(min(s,20),0)+1
    print('  size hist (cap20):', dict(sorted(hist.items())))
blobs(V, 'vendor')
blobs(O, 'ours  ')
