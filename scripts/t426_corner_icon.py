#!/usr/bin/env python3
"""t426 probe 2: the UPPER-LEFT object inside the black cosmos field.

The pure refcap (png = screen + 40) has a bright rounded object at screen
rows ~10..40, cols ~10..40 INSIDE COSMOSWnd (which is pure black elsewhere).
User verbatim (2026-11-17): "the galaxy map is supposed to show the player
icon in the upper left, not the upper right".

Prints: (a) exact extent of non-black pixels in screen rows 0..80 x cols 0..80;
(b) luminance ASCII of the object; (c) colour histogram in CONVERTED pal
(round(v*255/63) — the vendor scale, NOT the floor used by probe 1);
(d) best exact match of the object against EVERY 1starmap.shp record
(decoded through the project RLE grammar, stream@rec+0x18 t425b law) over
scales {1,2} x offsets -3..+3, score = exact-equal fraction on non-skip px.
Read-only; exit 0.
"""
import struct

import numpy as np
from PIL import Image

LIB = "extracted/ascend01/data/1starmap.shp"
PAL = open("extracted/ascend01/data/game.pal", "rb").read()
conv = [(round(PAL[3*i]*255/63), round(PAL[3*i+1]*255/63), round(PAL[3*i+2]*255/63))
        for i in range(256)]

ref = np.asarray(Image.open(
    "docs/assets/refcap/original-strategic-map.png").convert("RGB")).astype(int)
# object zone INSIDE the window (chrome bands excluded): screen rows 8..44,
# cols 8..44 -> png y+40
zone = ref[48:93, 8:45]
nz = zone.sum(axis=2) > 0
ys, xs = np.nonzero(nz)
print(f"non-black zone extent rows {ys.min()}..{ys.max()} cols {xs.min()}..{xs.max()} (screen coords)")

sub = zone[ys.min():ys.max()+1, xs.min():xs.max()+1]
print(f"object bbox {sub.shape[1]}x{sub.shape[0]} at screen ({xs.min()},{ys.min()})")

import collections
hist = collections.Counter(map(tuple, sub.reshape(-1, 3)))
def near(c):
    for i, cc in enumerate(conv):
        if abs(cc[0]-c[0]) <= 1 and abs(cc[1]-c[1]) <= 1 and abs(cc[2]-c[2]) <= 1:
            return i
    return None
print("colour histogram (pal idx or OFF):")
for c, n in hist.most_common(14):
    i = near(c)
    print(f"  {'idx'+str(i) if i is not None else 'OFF'}: {c} x{n}")

print("luminance ASCII ('.'=black '#'>150 '+'>60 '-' else):")
L = 0.2126*sub[:,:,0] + 0.7152*sub[:,:,1] + 0.0722*sub[:,:,2]
for r in range(sub.shape[0]):
    print("".join("." if v <= 15 else ("-" if v <= 60 else ("+" if v <= 150 else "#")) for v in L[r]))

# ---- shp records ----
d = open(LIB, "rb").read()
magic, count, tsz = struct.unpack_from("<III", d, 0)
starts = [0x10 + tsz] + list(struct.unpack_from("<%dQ" % (count-1), d, 0x10))

def decode(rec):
    off = rec if k == 0 else rec + 0x10
    s = rec + 8 if k == 0 else rec + 0x18
    w, h = struct.unpack_from("<II", d, off)
    # MEMORY GUARD (2026-11-18: this script's unbounded h from a bogus
    # record offset ballooned to the cgroup cap and got OOM-killed):
    # plausible records are 10..90 px; refuse anything else BEFORE
    # building rows, and never walk past the file end.
    if not (0 < w <= 512 and 0 < h <= 512) or s >= len(d):
        raise ValueError(f"implausible dims {w}x{h} @ {rec:#x}")
    pos, rows = s, min(h, 512)
    for _ in range(rows):
        row = []
        while True:
            if pos >= len(d):
                raise ValueError("ran off end of file")
            c = d[pos]; pos += 1
            if c == 0:
                break
            if c == 1:
                row += [-1]*d[pos]; pos += 1
            elif c & 1:
                n = c >> 1; row += list(d[pos:pos+n]); pos += n
            else:
                row += [d[pos]]*(c >> 1); pos += 1
        rows.append((row + [-1]*w)[:w])
    return w, h, rows

best = []
for k in range(count):
    try:
        w, h, rows = decode(starts[k])
    except Exception:
        continue
    if not (10 <= w <= 90 and 10 <= h <= 90):
        continue
    arr = np.array([[conv[i] if i >= 0 else (0, 0, 0) for i in row] for row in rows], dtype=int)
    opaque = np.array([[i >= 0 for i in row] for row in rows])
    for sc in (1, 2):
        W, H = w*sc, h*sc
        a = np.repeat(np.repeat(arr, sc, 1), sc, 0) if sc > 1 else arr
        o = np.repeat(np.repeat(opaque, sc, 1), sc, 0) if sc > 1 else opaque
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                y0 = ys.min()+dy; x0 = xs.min()+dx
                if y0 < 0 or x0 < 0 or y0+H > zone.shape[0] or x0+W > zone.shape[1]:
                    continue
                patch = zone[y0:y0+H, x0:x0+W]
                eq = ((np.abs(patch-a).sum(axis=2) <= 3) & o).sum()
                tot = o.sum()
                if tot == 0:
                    continue
                frac = eq/tot
                best.append((frac, k, sc, dx, dy, f"{W}x{H}"))
best.sort(reverse=True)
print("\ntop record matches (exact-equal fraction on opaque px):")
for b in best[:12]:
    print(f"  k{b[1]} scale{b[2]} d({b[3]},{b[4]}) {b[5]} -> {b[0]*100:.1f}%")
