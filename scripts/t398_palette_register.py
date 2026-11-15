#!/usr/bin/env python3
# t398 palette-registration law: does each .shp record's index plane map into
# game.pal (6-bit DAC, DOSBox conv c=(v<<2)|(v>>4)) at the screenshot's
# registration shift? Method = t386/t391 conflict-count law, generalised:
# instead of scoring against the ramp, we LEARN the map index->shot-colour
# per record and report (a) conflicts within the record, (b) how many of the
# record's distinct shot colours lie INSIDE game.pal-converted.
# A record whose learned map is conflict-free and 100% inside game.pal is
# evidence the record is painted through game.pal (membership + geometry).
#
# Usage: t398_palette_register.py SHOT.png LIB.shp REC[:X0,Y0] [REC ...]
# The X0,Y0 (game coords) is an expected top-left; shifts -12..+12 around it
# are searched; best = fewest conflicts then most painted-tested.
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_shp_unifiedlaw as U
from PIL import Image

GP = open("extracted/ascend01/data/game.pal", "rb").read()
GSET = set(tuple(((GP[i] << 2) | (GP[i] >> 4)) for i in (3 * k, 3 * k + 1, 3 * k + 2))
           for k in range(256))


def plane_and_mask(d, starts, ends, k):
    # t391 S9 grammar (verbatim shape from scripts/t391_registration.py)
    rec = starts[k]
    d_off = rec if k == 0 else rec + 0x10
    s_off = rec + 8 if k == 0 else rec + 0x18
    w0, h = struct.unpack_from("<II", d, d_off)
    i = s_off
    vals = [-1] * (w0 * h)
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
                for q in range(min(n, max(0, w0 - p))):
                    vals[(r * w0) + p + q] = v
                p += n
    mask = [v >= 0 and v != 0xAA and v != 0x55 for v in vals]
    return vals, mask, w0, h


shot_path, lib_path = sys.argv[1], sys.argv[2]
im = Image.open(shot_path).convert("RGB")
W, H = im.size
ox, oy = (W - 640) // 2, (H - 480) // 2
px = im.load()

d, count, te, tsz, starts, ends = U.parse(lib_path)

rc = 0
for spec in sys.argv[3:]:
    parts = spec.split(":")
    rec = int(parts[0])
    ex, ey = (0, 0)
    if len(parts) > 1:
        ex, ey = (int(v) for v in parts[1].split(","))
    vals, mask, pw, ph = plane_and_mask(d, starts, ends, rec)
    if vals is None:
        print(f"rec {rec}: WALK FAILED")
        rc = 1
        continue
    best = None
    band = len(parts) > 2
    xlo, sy_lo, xhi, sy_hi = ex - 12, ey - 12, ex + 12, ey + 12
    if band:  # band mode: REC:X0,Y0:BANDX0,BANDY0,BANDX1,BANDY1 — sx,sy are
        # the record's ABSOLUTE game-coord top-left sweeping the band.
        bx0, by0, bx1, by1 = (int(v) for v in parts[2].split(","))
        xlo, sy_lo, xhi, sy_hi = bx0, by0, bx1 - pw, by1 - ph
    for sx in range(xlo, xhi + 1):
        for sy in range(sy_lo, sy_hi + 1):
            tx0, ty0 = (sx, sy) if band else (ex + sx, ey + sy)
            m = {}
            conf = tested = 0
            for y in range(ph):
                base = y * pw
                for x in range(pw):
                    if not mask[base + x]:
                        continue
                    X, Y = ox + tx0 + x, oy + ty0 + y
                    if not (0 <= X < W and 0 <= Y < H):
                        continue
                    c = px[X, Y]
                    idx = vals[base + x]
                    prev = m.get(idx)
                    if prev is None:
                        m[idx] = c
                    elif prev != c:
                        conf += 1
                    tested += 1
            if tested == 0:
                continue
            key = (conf, -tested)
            if best is None or key < best[0]:
                best = (key, sx, sy, m, tested)
    if best is None:
        print(f"rec {rec} ({pw}x{ph}): no painted px in shot at any shift")
        continue
    (key, sx, sy, m, tested) = best
    cols = set(m.values())
    inside = sum(1 for c in cols if c in GSET)
    print(f"rec {rec} ({pw}x{ph}) best_shift=({sx:+d},{sy:+d}) tested={tested} "
          f"conflicts={key[0]} distinct_colours={len(cols)} in_game.pal={inside} "
          f"({100*inside/max(1,len(cols)):.0f}% of colours)")
    if key[0] == 0 and inside < len(cols):
        out = sorted((c for c in cols if c not in GSET))
        print(f"   OUTSIDE: {out[:10]}")
