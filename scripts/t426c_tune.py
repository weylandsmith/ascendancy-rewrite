#!/usr/bin/env python3
"""t426c probe 3: chain-parameter tuning for the per-row top-band law.
Replay the port Markov chain over x7..465 y0..6 with per-row fresh draws =
vendor counts; score chi-square vs vendor per-row census + h-run match.
exit 0 always."""
import collections

import numpy as np
from PIL import Image

MAP = np.asarray(Image.open(
    "docs/assets/refcap/original-strategic-map.png").convert("RGB"))
SCR = np.asarray(Image.open(
    "scratchpad/galaxymap-original.png").convert("RGB"))
PAL = open("extracted/ascend01/data/game.pal", "rb").read()
conv = {}
for i in range(256):
    base = tuple(round(PAL[3 * i + j] * 255 / 63) for j in range(3))
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                conv.setdefault((base[0] + dx, base[1] + dy, base[2] + dz), i)


def idx(px):
    return conv.get(tuple(int(v) for v in px), None)


def census(region):
    out = collections.Counter()
    for px in np.asarray(region).reshape(-1, 3):
        i = idx(px)
        out[i if i is not None else -1] += 1
    return out


def splitmix(x, y):
    z = ((x & 0xFFFFFFFF) << 32) ^ (y & 0xFFFFFFFF) ^ 0x9E3779B97F4A7C15
    z &= (1 << 64) - 1
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & ((1 << 64) - 1)
    z = ((z ^ (z >> 27)) * 0x94D045BB41F336) & ((1 << 64) - 1)
    return z ^ (z >> 31)


def draw_from(counts, r2):
    tot = sum(counts.values())
    d = r2 % tot
    acc = 0
    for k, n in counts.items():
        acc += n
        if d < acc:
            return k
    return max(counts, key=counts.get)


def replay2(pl, pu, table_fn, x0, x1, y0, y1):
    grid = {}
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            xx, yy = x, y
            while True:
                z = splitmix(xx, yy)
                r = z % 1000000
                if r < pl * 10000 and xx > x0 - 8:
                    xx -= 1
                    continue
                if r < pu * 10000 and yy > y0 - 8:
                    yy -= 1
                    continue
                grid[(x, y)] = draw_from(table_fn(xx, yy), z >> 20)
                break
    return grid


def runs2d(arr, axis):
    if axis == 0:
        arr = [list(l) for l in zip(*arr)]
    r = collections.Counter()
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
    return {k: round(r[k] / tot, 3) for k in range(1, 7)}


def chi2(gen, ven):
    out = {}
    for y, v in ven.items():
        g = collections.Counter(k for (gx, gy), k in gen.items() if gy == y)
        n = sum(g.values())
        s = 0.0
        vt = sum(v.values())
        for k in set(g) | set(v):
            if k < 0:
                continue
            e = v.get(k, 0) / vt * n
            o = g.get(k, 0)
            if e > 0:
                s += (o - e) ** 2 / e
        out[y] = round(s, 1)
    return out


rowc = {y: census(MAP[y + 40, 7:466]) for y in range(7)}
rowtable = [{k: n for k, n in rowc[y].items() if k >= 0} for y in range(7)]

print("== TOP band chain tuning (x7..465 y0..6) ==")
for (pl, pu) in [(5, 25), (25, 25), (35, 25), (25, 30), (45, 25), (55, 25)]:
    g = replay2(pl, pu, lambda x, y: rowtable[min(max(y, 0), 6)], 7, 465, 0, 6)
    h = runs2d([[g[(x, y)] for x in range(7, 466)] for y in range(7)], 1)
    v = runs2d([[idx(MAP[y + 40, x]) for x in range(7, 466)]
                for y in range(7)], 1)
    print(f"pl={pl} pu={pu} chi2={chi2(g, rowc)} hrun={h} vendor={v}")

# BOTTOM band from the scratchpad (identity rows; non-pure pixels count OFF
# and are EXCLUDED from chi2; test the mirror orientation: does the band
# repeat ALONG rows (h) and step DOWN rows 473->479 brightening?)
print("\n== BOTTOM band scratchpad per-row census rows 473..480 x60..420 ==")
botc = {y: census(SCR[y, 60:421]) for y in range(473, 481)}
for y in range(473, 481):
    c = botc[y]
    tot = sum(c.values())
    items = sorted(((k, n) for k, n in c.items() if k >= 0),
                   key=lambda kv: -kv[1])[:8]
    off = c.get(-1, 0)
    print(f"row{y} OFF:{off*100.0/tot:.1f} " + " ".join(
        f"{k}:{n*100.0/tot:.1f}" for k, n in items))
btab = [{k: n for k, n in botc[y].items() if k >= 0} for y in range(473, 481)]


def btab_fn(x, y):
    return btab[min(max(y - 473, 0), 7)]


print("\n== BOTTOM band replay chi2 (scratchpad counts as truth) ==")
for (pl, pu) in [(5, 25), (25, 30)]:
    g = replay2(pl, pu, btab_fn, 60, 420, 473, 480)
    h = runs2d([[g[(x, y)] for x in range(60, 421)] for y in range(473, 481)], 1)
    v = runs2d([[idx(SCR[y, x]) for x in range(60, 421)]
                for y in range(473, 481)], 1)
    print(f"pl={pl} pu={pu} chi2={chi2(g, botc)} hrun={h} vendor={v}")
