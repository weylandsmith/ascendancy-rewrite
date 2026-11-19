#!/usr/bin/env python3
"""t426 probe 3: identify the upper-left PLAYER PLAQUE (screen 10,10..24,34).

Facts this probe builds on:
- pure refcap original-strategic-map.png is png = screen + 40 (t425c law);
  the plaque occupies png rows 50..74, cols 10..24 (screen 10..34 x 10..24).
- (probe 2b mislabel: its ASCII rows are png rows, plaque at there 50..74.)
- palette scale round(v*255/63) (vendor), NOT floor.

Prints: (a) exact palette-label grid of the plaque;
        (b) best exact match of the plaque INTERIOR glyph (rows 52..72 x
            12..22, border excluded) and of the whole 15x25 block against
            every record of every .shp lib in extracted/ascend01/data
            decoded with the project RLE grammar (stream@rec+0x18, header
            w/h @rec; dims guarded <=512 per the 2026-11-18 OOM lesson).
Read-only; exit 0.
"""
import collections
import glob
import struct
import os

import numpy as np
from PIL import Image

PALB = open("extracted/ascend01/data/game.pal", "rb").read()
conv = [(round(PALB[3*i]*255/63), round(PALB[3*i+1]*255/63),
         round(PALB[3*i+2]*255/63)) for i in range(256)]
cmap = {c: i for i, c in enumerate(conv)}

ref = np.asarray(Image.open(
    "docs/assets/refcap/original-strategic-map.png").convert("RGB")).astype(int)
plaque = ref[50:75, 10:25]  # 25 rows x 15 cols


def lab(c):
    t = tuple(int(v) for v in c)
    i = cmap.get(t)
    if i is not None:
        return "%3d" % i
    # +-1 tolerance
    for j, cc in enumerate(conv):
        if all(abs(cc[k]-t[k]) <= 1 for k in range(3)):
            return "%3d~" % j
    return "OFF"


print("== plaque palette grid (png rows 50..74, cols 10..24) ==")
for r in range(plaque.shape[0]):
    print("%3d %s" % (50+r, " ".join(lab(plaque[r, c]) for c in range(15))))

hist = collections.Counter(map(tuple, plaque.reshape(-1, 3)))
print("\nhistogram:", {lab(c): n for c, n in hist.most_common(8)})


def decode_all(path):
    d = open(path, "rb").read()
    if len(d) < 16:
        return []
    magic, count, tsz = struct.unpack_from("<III", d, 0)
    if not (0 < count < 4096):
        return []
    starts = [0x10 + tsz] + list(struct.unpack_from("<%dQ" % (count-1), d, 0x10))
    out = []
    for k, rec in enumerate(starts):
        if rec + 16 > len(d):
            continue
        try:
            w, h = struct.unpack_from("<II", d, rec)
            s = rec + 0x18
            if not (0 < w <= 512 and 0 < h <= 512) or s >= len(d):
                continue
            pos, rows = s, h
            got = True
            for _ in range(h):
                row = []
                while True:
                    if pos >= len(d) or len(row) > w + 8:
                        got = False
                        break
                    c = d[pos]
                    pos += 1
                    if c == 0:
                        break
                    if c == 1:
                        if pos >= len(d):
                            got = False
                            break
                        row += [-1]*d[pos]
                        pos += 1
                    elif c & 1:
                        n = c >> 1
                        row += list(d[pos:pos+n])
                        pos += n
                    else:
                        row += [d[pos]]*(c >> 1)
                        pos += 1
                if not got:
                    break
                rows_ = None
                out_row = (row + [-1]*w)[:w]
                if not hasattr(decode_all, "_"):
                    pass
                rows = out_row
                break  # only first row validated cheaply below
        except Exception:
            continue
        out.append((k, rec, w, h))
    return out


def decode_full(d, rec):
    w, h = struct.unpack_from("<II", d, rec)
    if not (0 < w <= 512 and 0 < h <= 512):
        raise ValueError("dims")
    pos, s = rec + 0x18, rec + 0x18
    rows = []
    for _ in range(h):
        row = []
        while True:
            if pos >= len(d):
                raise ValueError("eof")
            c = d[pos]
            pos += 1
            if c == 0:
                break
            if c == 1:
                if pos >= len(d):
                    raise ValueError("eof")
                row += [-1]*d[pos]
                pos += 1
            elif c & 1:
                n = c >> 1
                if pos+n > len(d):
                    raise ValueError("eof")
                row += list(d[pos:pos+n])
                pos += n
            else:
                row += [d[pos]]*(c >> 1)
                pos += 1
        rows.append((row + [-1]*w)[:w])
    return w, h, rows


target = plaque
th, tw = target.shape[0], target.shape[1]
best = []
for path in sorted(glob.glob("extracted/ascend01/data/*.shp")):
    d = open(path, "rb").read()
    try:
        magic, count, tsz = struct.unpack_from("<III", d, 0)
    except Exception:
        continue
    if not (0 < count < 4096):
        continue
    starts = [0x10 + tsz] + list(struct.unpack_from("<%dQ" % (count-1), d, 0x10))
    for k, rec in enumerate(starts):
        if rec + 16 > len(d) or rec <= 0:
            continue
        try:
            w, h, rows = decode_full(d, rec)
        except Exception:
            continue
        if not (10 <= w <= 40 and 15 <= h <= 40):
            continue
        arr = np.array([[conv[i] if 0 <= i < 256 else (0, 0, 0) for i in row]
                        for row in rows], dtype=int)
        opaque = np.array([[i >= 0 for i in row] for row in rows])
        if opaque.sum() < 0.5 * w * h:
            continue
        for dy in range(-6, 7):
            for dx in range(-6, 7):
                y0, x0 = 50+dy-0, 10+dx  # place record top-left at png (50+dy,10+dx)
                yy0, xx0 = y0-50, x0-10
                # overlap window inside plaque array
                ry0, rx0 = max(0, yy0), max(0, xx0)
                ry1, rx1 = min(th, yy0+h), min(tw, xx0+w)
                if ry1-ry0 < 10 or rx1-rx0 < 8:
                    continue
                ay0, ax0 = ry0-yy0, rx0-xx0
                patch = target[ry0:ry1, rx0:rx1]
                a = arr[ay0:ay0+(ry1-ry0), ax0:ax0+(rx1-rx0)]
                o = opaque[ay0:ay0+(ry1-ry0), ax0:ax0+(rx1-rx0)]
                eq = int(((np.abs(patch-a).sum(axis=2) <= 3) & o).sum())
                tot = int(o.sum())
                if tot < 40:
                    continue
                best.append((eq/tot, os.path.basename(path), k, dx, dy,
                             f"{w}x{h}"))
best.sort(key=lambda t: -t[0])
print("\n== top matches (exact-equal on opaque px, plaque window) ==")
seen = set()
for b in best:
    key = (b[1], b[2])
    if key in seen:
        continue
    seen.add(key)
    print(f"  {b[0]*100:5.1f}%  {b[1]} k{b[2]} {b[5]} d({b[3]},{b[4]})")
    if len(seen) >= 12:
        break
