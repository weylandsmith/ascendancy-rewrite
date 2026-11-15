#!/usr/bin/env python3
# t391 registration law (t386 method, applied to the campaign backdrops):
# map .shp index -> screenshot colour over the record area at shift (0,0).
# Our blitShape paints index i as grey lum = 40 + i*185//255 where WRITTEN,
# alpha-0 where skipped (destination shows through). S9 GRAMMAR (imported
# law shape from r1_shp_unifiedlaw.rowwalk_free, extended to emit values):
#   C==0 end-row; C==1 skip 1 byte; C odd >1: n=C>>1 SKIP n bytes (no paint);
#   C even: n=C>>1, paint n px of value d[i], i+=1. p advances by n in both
#   classes (UNCLAMPED per rowwalk_free); painted px = min(n, W-p) prefix.
# Mask law (blitShape): written px opaque UNLESS value == 0xAA/0x55 prefill
# collision (then falsely transparent — replicate, don't idealise).
#
# Usage: t391_registration.py SHOT.png LIB.shp [rec=0]
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_shp_unifiedlaw as U
from PIL import Image


def plane_and_mask(d, starts, ends, k):
    rec = starts[k]
    d_off = rec if k == 0 else rec + 0x10
    s_off = rec + 8 if k == 0 else rec + 0x18
    w0, h = struct.unpack_from("<II", d, d_off)
    i = s_off
    vals = [-1] * (w0 * h)  # -1 = never written
    for r in range(h):
        p = 0
        while True:
            if i >= len(d):
                return None, None, 0, 0
            C = d[i]; i += 1
            if C == 0:
                break
            if C == 1:
                i += 1  # stream skip only; p does NOT advance (rowwalk_free law)
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
rec = int(sys.argv[3]) if len(sys.argv) > 3 else 0
im = Image.open(shot_path).convert("RGB")
W, H = im.size
ox, oy = (W - 640) // 2, (H - 480) // 2
px = im.load()

d, count, te, tsz, starts, ends = U.parse(lib_path)
vals, mask, pw, ph = plane_and_mask(d, starts, ends, rec)
if vals is None:
    print("WALK FAILED")
    sys.exit(2)
npaint = sum(mask)
print(f"lib={os.path.basename(lib_path)} rec={rec} plane={pw}x{ph} "
      f"opaque_px={npaint}")


def score_at(sx, sy):
    m = {}
    conf = tested = grey_outside_ramp = transparent_hit = 0
    for y in range(ph):
        for x in range(pw):
            idx = vals[y * pw + x]
            X, Y = ox + x + sx, oy + y + sy
            if not (0 <= X < 640 and 0 <= Y < 480):
                continue
            c = px[X, Y]
            if not mask[y * pw + x]:
                continue
            lum = 40 + (idx * 185) // 255
            if c != (lum, lum, lum):
                grey_outside_ramp += 1
                continue
            tested += 1
            prev = m.get(idx)
            if prev is None:
                m[idx] = c
            elif prev != c:
                conf += 1
    return conf, tested, grey_outside_ramp


best = None
for (sx, sy) in [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (7, 7)]:
    conf, tested, offramp = score_at(sx, sy)
    print(f"shift ({sx:+d},{sy:+d}): ramp-matching px={tested} "
          f"off-ramp={offramp} map-conflicts={conf}")
    if (sx, sy) == (0, 0):
        best = (conf, tested)
print("LAW: PASS requires shift(0,0) conflicts==0 and tested >= 90% opaque")
ok = best[0] == 0 and best[1] >= 0.9 * npaint
print("VERDICT", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
