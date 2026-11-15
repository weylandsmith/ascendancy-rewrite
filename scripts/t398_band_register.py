#!/usr/bin/env python3
# t398 band registration, numpy-vectorised (same law as t398_palette_register
# .band mode, ~1000x faster): find where a .shp record sits in a screenshot by
# minimising index->colour CONFLICTS over the painted pixels, then report how
# many learned colours lie inside game.pal (DOSBox conv (v<<2)|(v>>4)).
#
# Usage: t398_band_register.py SHOT.png LIB.shp REC:BX0,BY0,BX1,BY1 [...]
import os
import struct
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_shp_unifiedlaw as U
from PIL import Image

GP = open("extracted/ascend01/data/game.pal", "rb").read()
GSET = set(tuple(((GP[i] << 2) | (GP[i] >> 4)) for i in (3 * k, 3 * k + 1, 3 * k + 2))
           for k in range(256))


def plane_and_mask(d, starts, ends, k):
    rec = starts[k]
    d_off = rec if k == 0 else rec + 0x10
    s_off = rec + 8 if k == 0 else rec + 0x18
    w0, h = struct.unpack_from("<II", d, d_off)
    i = s_off
    vals = np.full(w0 * h, -1, dtype=np.int16)
    for r in range(h):
        p = 0
        while True:
            if i >= len(d):
                return None, None, 0, 0
            C = d[i]; i += 1
            if C == 0:
                break
            if C == 1:
                i += 1
            elif C & 1:
                n = C >> 1
                p += n
                i += n
            else:
                n = C >> 1
                v = d[i]
                i += 1
                q = min(n, max(0, w0 - p))
                if q > 0:
                    vals[r * w0 + p: r * w0 + p + q] = v
                p += n
    mask = (vals >= 0) & (vals != 0xAA) & (vals != 0x55)
    return vals, mask, w0, h


shot_path, lib_path = sys.argv[1], sys.argv[2]
im = Image.open(shot_path).convert("RGB")
W, H = im.size
ox, oy = (W - 640) // 2, (H - 480) // 2
shot = np.zeros((480, 640, 3), dtype=np.uint16)
a = np.asarray(im, dtype=np.uint16)
shot[:, :] = a[oy:oy + 480, ox:ox + 640]

d, count, te, tsz, starts, ends = U.parse(lib_path)

for spec in sys.argv[3:]:
    rs, band = spec.split(":")
    rec = int(rs)
    bx0, by0, bx1, by1 = (int(v) for v in band.split(","))
    vals, mask, pw, ph = plane_and_mask(d, starts, ends, rec)
    if vals is None:
        print(f"rec {rec}: WALK FAILED")
        continue
    pxs, pys = np.nonzero(mask.reshape(ph, pw))
    if pxs.size == 0:
        print(f"rec {rec} ({pw}x{ph}): no painted px")
        continue
    v = vals[pxs * pw + pys].astype(np.uint16)
    n_idx = len(np.unique(v))
    best = None
    for sy in range(by0, by1 - ph + 1):
        for sx in range(bx0, bx1 - pw + 1):
            X = sx + pys
            Y = sy + pxs
            okm = (X >= 0) & (X < 640) & (Y >= 0) & (Y < 480)
            if okm.sum() < 0.8 * pxs.size:
                continue
            cs = shot[Y[okm], X[okm]]            # (n,3)
            # conflicts: per index, pixels whose colour != first pixel's colour
            order = np.argsort(v, kind="stable")
            vv = v[order]
            cc = cs[order]
            first = np.concatenate([[True], vv[1:] != vv[:-1]])
            grpstart = np.nonzero(first)[0]
            # a group has a conflict if any colour differs from group head
            headc = cc[grpstart]
            # broadcast compare per group
            ends_idx = np.append(grpstart[1:], len(vv))
            conf = 0
            for gi, gs in enumerate(grpstart):
                g = cc[gs:ends_idx[gi]]
                conf += int(np.count_nonzero(np.any(g != headc[gi], axis=1)))
            # SELECTION LAW: fewest conflicts, then RICHEST learned map (a
            # placement on flat background has 1 colour and is VACUOUS).
            key = (conf, -len(grpstart))
            if best is None or key < best[0]:
                best = (key, sx, sy, grpstart, headc, vv, okm.sum())
    if best is None:
        print(f"rec {rec} ({pw}x{ph}): no fully-visible placement in band")
        continue
    (conf, sx, sy, grpstart, headc, vv, nvis) = best
    cols = {tuple(int(x) for x in c) for c in headc}
    inside = sum(1 for c in cols if c in GSET)
    vac = "" if (n_idx >= 2 and len(cols) >= 2) else "  [VACUOUS: flat]"
    print(f"rec {rec} ({pw}x{ph}) at ({sx},{sy}) vis={nvis} painted_idx={n_idx} "
          f"conflicts={conf} distinct={len(cols)} in_game.pal={inside} "
          f"({100*inside/max(1,len(cols)):.0f}%){vac}")
    if conf == 0:
        outc = sorted(c for c in cols if c not in GSET)
        if outc:
            print(f"   COLOURS OUTSIDE game.pal: {outc[:12]}")
