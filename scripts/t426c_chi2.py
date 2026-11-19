#!/usr/bin/env python3
"""t426c probe 2: band gradient in ROUND palette space + chi-square replay.

Palette scale pitfall (F1 note): vendor rgb = round(v*255/63), so the
floor map *255//63 mislabels off-by-one px as OFF. This probe maps to the
nearest palette entry under round scale with tol<=1, then:
  A. top band per-row census, x7..465 (the port's band rect).
  A2. top band FULL width x466..639 rows 0..6 (does chrome gradient run
      over the sidebar top too?).
  B. control: left band per-column census rows 60..460 must be ~0 OFF.
  C. right strip x466..472 per-column census rows 60..460 (dist law?).
  D. run-length stats: top band h-run AND v-run vs left band (rotated-
     strip hypothesis: top band h-repeat == left band v-repeat).
  E. replay of the PORT chain (copy-left 5% / repeat-up 25% / fresh draw
     from vendor per-row counts) and chi-square of generated vs vendor
     per-row census; plus the same with the CURRENT law (flat kRight).
exit 0 always.
"""
import collections

import numpy as np
from PIL import Image

MAP = np.asarray(Image.open(
    "docs/assets/refcap/original-strategic-map.png").convert("RGB"))
PAL = open("extracted/ascend01/data/game.pal", "rb").read()
# round scale, plus tolerance buckets
conv = {}
for i in range(256):
    base = tuple(round(PAL[3 * i + j] * 255 / 63) for j in range(3))
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                k = (base[0] + dx, base[1] + dy, base[2] + dz)
                conv.setdefault(k, i)


def idx(px):
    return conv.get(tuple(int(v) for v in px), None)


def census(region):
    out = collections.Counter()
    for px in np.asarray(region).reshape(-1, 3):
        i = idx(px)
        out[i if i is not None else -1] += 1
    return out


def show(tag, reg, topn=12):
    c = census(reg)
    tot = sum(c.values())
    items = sorted(c.items(), key=lambda kv: -kv[1])[:topn]
    print(f"{tag:24s} n={tot:6d} " + " ".join(
        f"{'OFF' if k < 0 else k}:{n*100.0/tot:.1f}" for k, n in items))
    return c


print("== A. TOP band per-row census (round space), x7..465 ==")
rowc = {}
for y in range(0, 7):
    rowc[y] = show(f"row{y}", MAP[y + 40, 7:466], 14)

print("\n== A2. rows 0..6 x466..639 (over the sidebar) ==")
for y in range(0, 7):
    show(f"row{y} x466+", MAP[y + 40, 466:640])

print("\n== B. control left band cols x0..6 rows 60..460 (want OFF~0) ==")
for x in range(0, 7):
    show(f"col{x}", MAP[60:461, x:x + 1], 10)

print("\n== C. right strip x466..472 per-column rows 60..460 ==")
for x in range(466, 473):
    show(f"col{x}", MAP[60:461, x:x + 1], 10)

print("\n== D. run-length stats ==")


def runs2d(seq2d, axis):
    """axis=1 horizontal within rows, axis=0 vertical down cols."""
    r = collections.Counter()
    arr = np.asarray(seq2d)
    if axis == 0:
        arr = arr.T
    for line in arr:
        cur, n = line[0], 1
        for v in line[1:]:
            if v == cur:
                n += 1
            else:
                r[min(n, 6)] += 1
                cur, n = v, 1
        r[min(n, 6)] += 1
    tot = sum(r.values())
    return {k: r[k] / tot for k in range(1, 7)}


top = [[idx(p) for p in MAP[y + 40, 7:466]] for y in range(7)]
print("top h-run", {k: round(v, 3) for k, v in runs2d(top, 1).items()})
print("top v-run", {k: round(v, 3) for k, v in runs2d(top, 0).items()})
leftgrid = [[idx(MAP[y, x]) for x in range(7)] for y in range(60, 461)]
print("left h-run", {k: round(v, 3) for k, v in runs2d(leftgrid, 1).items()})
print("left v-run", {k: round(v, 3) for k, v in runs2d(leftgrid, 0).items()})

print("\n== E. port-chain replay + chi-square ==")


def splitmix(x, y):
    z = ((x & 0xFFFFFFFF) << 32) ^ (y & 0xFFFFFFFF) ^ 0x9E3779B97F4A7C15
    z &= (1 << 64) - 1
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & ((1 << 64) - 1)
    z = ((z ^ (z >> 27)) * 0x94D045BB41F336) & ((1 << 64) - 1)
    return z ^ (z >> 31)


# vendor left-band per-column colour counts (F7 in index space, rgb via PAL)
GREY = {i: i for i in range(256)}


def rgb_of(i):
    return tuple(round(PAL[3 * i + j] * 255 / 63) for j in range(3))


# Replay the chain over the band rect x 7..465, y 0..6 with per-row fresh
# draws = vendor counts; anchor outside the band falls back to row table of
# the nearest row (mirrors C++ kLeft fallback we will ship).
def replay(pl, pu, table_fn, w=459, h=7, seed_off=0):
    grid = {}
    for y in range(h):
        for x in range(7, 7 + w):
            xx, yy = x, y
            for _ in range(60):
                r = splitmix(xx + seed_off, yy) % 1000000
                if r < pl * 10000 and xx > 0:
                    xx -= 1
                    continue
                if r < pu * 10000 and yy > 0:
                    yy -= 1
                    continue
                break
            key = table_fn(xx, yy)
            grid[(x, y)] = key
    return grid


def draw_from(counts, r2):
    tot = sum(counts.values())
    d = r2 % tot
    acc = 0
    for k, n in counts.items():
        acc += n
        if d < acc:
            return k
    return max(counts, key=counts.get)


def replay2(pl, pu, table_fn, w=459, h=7):
    grid = {}
    for y in range(h):
        for x in range(7, 7 + w):
            xx, yy = x, y
            while True:
                z = splitmix(xx, yy)
                r = z % 1000000
                if r < pl * 10000 and xx > 0:
                    xx -= 1
                    continue
                if r < pu * 10000 and yy > 0:
                    yy -= 1
                    continue
                cnts = table_fn(xx, yy)
                grid[(x, y)] = draw_from(cnts, z >> 20)
                break
    return grid


def chi2(gen, ven):
    out = {}
    keys = set(ven) | set(gen)
    for y in range(7):
        g = collections.Counter(k for (gx, gy), k in gen.items() if gy == y)
        v = ven[y]
        n = sum(g.values())
        s = 0.0
        for k in set(g) | set(v):
            e = v.get(k, 0) / sum(v.values()) * n
            o = g.get(k, 0)
            if e > 0:
                s += (o - e) ** 2 / e
        out[y] = round(s, 1)
    return out


# per-row vendor-count tables (colours as palette idx)
rowtable = [{k: n for k, n in rowc[y].items() if k >= 0} for y in range(7)]
flat = {k: n for y in range(7) for k, n in rowc[y].items() if k >= 0}
# current-law table = kRight (chrome-set colours of the right zone)
kright = {55: 7587, 6: 3514, 56: 3093, 176: 2018, 57: 1997, 58: 1483,
          48: 1163, 49: 1095, 2: 968, 53: 928}

g_flat = replay2(5, 25, lambda x, y: kright)
print("chi2 CURRENT law (flat kRight, chain 5/25):", chi2(g_flat, rowc))
g_new = replay2(5, 25, lambda x, y: rowtable[min(max(y, 0), 6)])
print("chi2 NEW per-row table, chain 5/25:", chi2(g_new, rowc))
g_rot = replay2(25, 30, lambda x, y: rowtable[min(max(y, 0), 6)])
print("chi2 NEW per-row table, chain along-band 25/30:", chi2(g_rot, rowc))
for tag, g in (("flat", g_flat), ("rowtab-5-25", g_new), ("rowtab-25-30", g_rot)):
    print(f"h-run {tag}:", {k: round(v, 3) for k, v in runs2d(
        [[g[(x, y)] for x in range(7, 466)] for y in range(7)], 1).items()})
