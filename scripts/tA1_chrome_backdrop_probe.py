#!/usr/bin/env python3
"""tA1 probe (assistant, 2026-11-21): is the vendor chrome a FULL-SCREEN
BACKDROP RECORD rather than a generated field?

Evidence chain that prompted it: the planet screen frame is pixel-perfect
because it blits 17np.shp k0 (639x479, ui.cpp:1613). Census found THREE
full-screen records image-wide: 10status k0, 17np k0, 2savegam k0,
4loadgam k0 (all 639x479). If the chrome bands in 10status k0 match the
vendor refcap chrome pixels, the 'Markov field ceiling' was a phantom:
the chrome IS shipped art, and 'do it everywhere' = blit the right
backdrop record per screen. Read-only; exit 0.
"""
import struct

import numpy as np
from PIL import Image

PAL = open('extracted/ascend01/data/game.pal', 'rb').read()
conv = np.array([[PAL[3 * i], PAL[3 * i + 1], PAL[3 * i + 2]]
                 for i in range(256)], dtype=int)


def decode0(lib):
    d = open('extracted/ascend01/data/' + lib, 'rb').read()
    magic, count, tsz = struct.unpack_from('<III', d, 0)
    rec = 0x10 + tsz
    w, h = struct.unpack_from('<II', d, rec)
    pos = rec + 8
    rows = []
    for _ in range(h):
        row = []
        while True:
            c = d[pos]
            pos += 1
            if c == 0:
                break
            if c == 1:
                row += [-1] * d[pos]
                pos += 1
            elif c & 1:
                n = c >> 1
                row += list(d[pos:pos + n])
                pos += n
            else:
                row += [d[pos]] * (c >> 1)
        rows.append((row + [-1] * w)[:w])
    return w, h, np.array(rows, dtype=int)


w1, h1, st = decode0('10status.shp')
w2, h2, nps = decode0('17np.shp')
print('10status k0', w1, h1, '| 17np k0', w2, h2)
both = (st >= 0) & (nps >= 0)
same = (st == nps) & both
tot = max(int(both.sum()), 1)
print(f'overlapping opaque px {int(both.sum())}; identical {int(same.sum())} '
      f'= {100 * same.sum() / tot:.1f}%')
o1, o2 = st >= 0, nps >= 0
print('opaque-only-10status', int((o1 & ~o2).sum()),
      '| opaque-only-17np', int((o2 & ~o1).sum()))

# vendor ground truth: refcap png = screen + 40 offset (t422 law)
for cap in ('original-planet-view', 'original-strategic-map'):
    ref = np.asarray(
        Image.open('docs/assets/refcap/' + cap + '.png').convert('RGB')
    ).astype(int)
    band = ref[80:120, 1:7]  # png rows 80..120 = screen rows 40..80, cols 1..6
    for name, a in (('10status', st), ('17np', nps)):
        rec_px = a[40:80, 1:7]
        m = rec_px >= 0
        if m.sum() == 0:
            print(f'{name} vs {cap}: no opaque px in band — HOLE there')
            continue
        rgb = conv[rec_px[m]]
        dd = np.abs(rgb - band[m]).sum(axis=1)
        print(f'{name} vs {cap} left band: match<=3 '
              f'{100 * (dd <= 3).mean():.1f}% over {int(m.sum())} px')
