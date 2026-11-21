#!/usr/bin/env python3
"""tA1 probe 2: WHERE does 17np k0 land on the vendor planet-view capture?
Probe 1's 0% match at assumed 1:1/screen-offset-40 alignment is either a
real negative or MY alignment error. Cross-correlate the decoded record
(chrome-class opaque px) against the whole refcap over x,y shifts, score
= fraction of record-opaque px matching the capture within tol 3.
Also test palette scale variants (floor vs round). Exit 0.
"""
import struct

import numpy as np
from PIL import Image

PAL = open('extracted/ascend01/data/game.pal', 'rb').read()
conv_r = np.array([[round(PAL[3 * i] * 255 / 63), round(PAL[3 * i + 1] * 255 / 63),
                    round(PAL[3 * i + 2] * 255 / 63)] for i in range(256)], dtype=int)
conv_f = np.array([[PAL[3 * i] * 4, PAL[3 * i + 1] * 4, PAL[3 * i + 2] * 4]
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


w, h, a = decode0('17np.shp')
op = a >= 0
print('record', w, h, 'opaque', int(op.sum()), f'({100 * op.mean():.0f}%)')

ref = np.asarray(Image.open(
    'docs/assets/refcap/original-planet-view.png').convert('RGB')).astype(int)
print('refcap', ref.shape[1], 'x', ref.shape[0])

best = (-1, 0, 0, None)
for scale_name, conv in (('round', conv_r), ('x4', conv_f)):
    rgb = np.where(op[:, :, None], conv[np.clip(a, 0, 255)], 0)
    for dy in range(0, 45, 2):
        for dx in range(-8, 45, 2):
            # record px (y,x) maps to ref (y+dy, x+dx)
            ry0, rx0 = max(0, dy), max(0, dx)
            ry1 = min(ref.shape[0], h + dy)
            rx1 = min(ref.shape[1], w + dx)
            rec_sl = rgb[ry0 - dy:ry1 - dy, rx0 - dx:rx1 - dx]
            ref_sl = ref[ry0:ry1, rx0:rx1]
            m = op[ry0 - dy:ry1 - dy, rx0 - dx:rx1 - dx]
            if m.sum() < 5000:
                continue
            dd = np.abs(rec_sl - ref_sl).sum(axis=2)
            frac = float(((dd <= 6) & m).sum()) / float(m.sum())
            if frac > best[0]:
                best = (frac, dx, dy, scale_name)
print(f'best match {100 * best[0]:.1f}% at offset dx={best[1]} dy={best[2]} scale={best[3]}')
