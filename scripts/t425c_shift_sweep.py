#!/usr/bin/env python3
"""t425c probe 4: is the refcap-vs-face mismatch a spatial shift or a colour
remap? For each toggle face (k15..k18) and each race face member, sweep
dx,dy in -3..3 and report best exact-match rate; then, for the best offset,
print the index->refcap-colour correspondence table (a remap shows up as a
consistent 1:1 index mapping; a wrong-glyph shows up as noise).
Read-only. Exit 0.
"""
import collections
import struct

LIB = "extracted/ascend01/data/1starmap.shp"
PAL = "extracted/ascend01/data/game.pal"
REFCAP = "docs/assets/refcap/original-strategic-map.png"


def load(path):
    d = open(path, "rb").read()
    magic, count, tsz = struct.unpack_from("<III", d, 0)
    starts = [0x10 + tsz] + list(struct.unpack_from("<%dQ" % (count - 1), d, 0x10))
    return d, count, starts


def decode(d, rec, k):
    off = rec if k == 0 else rec + 0x10
    s = rec + 8 if k == 0 else rec + 0x18
    w, h = struct.unpack_from("<II", d, off)
    pos, rows = s, []
    for _ in range(h):
        row = []
        while True:
            c = d[pos]; pos += 1
            if c == 0:
                break
            if c == 1:
                row += [-1] * d[pos]; pos += 1
            elif c & 1:
                n = c >> 1
                row += list(d[pos:pos + n]); pos += n
            else:
                row += [d[pos]] * (c >> 1); pos += 1
        rows.append(row[:w])
    return w, h, rows


def main():
    from PIL import Image
    import numpy as np
    d, count, starts = load(LIB)
    pal = open(PAL, "rb").read()
    raw = [(pal[i], pal[i + 1], pal[i + 2]) for i in range(0, 768, 3)]
    conv = [tuple((c << 2) | (c >> 4) for c in t) for t in raw]
    c2i = collections.defaultdict(list)
    for i, c in enumerate(conv):
        c2i[c].append(i)
    A = np.asarray(Image.open(REFCAP).convert("RGB")).astype(int)

    targets = [("TOGLANES", 15, 479, 403), ("TOGEMPIRE", 16, 518, 403),
               ("TOGSHIPS", 17, 557, 403), ("TOGCOLONIES", 18, 596, 403),
               ("STRIDE k19", 19, 474, 442),
               ("slot1 +0", 20, 479, 449), ("slot1 +2", 22, 479, 449),
               ("slot3 +2", 27, 523, 449), ("slot5 +2", 32, 567, 449)]
    for name, k, x0, y0 in targets:
        w, h, rows = decode(d, starts[k], k)
        best = (-1, 0, 0)
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                eq = tot = 0
                for y in range(h):
                    for x in range(w):
                        v = rows[y][x]
                        if v < 0:
                            continue
                        yy, xx = y0 + y + dy, x0 + x + dx
                        if not (0 <= yy < A.shape[0] and 0 <= xx < A.shape[1]):
                            continue
                        tot += 1
                        if tuple(int(t) for t in A[yy][xx]) == conv[v]:
                            eq += 1
                if tot and eq / tot > best[0]:
                    best = (eq / tot, dx, dy)
        rate, dx, dy = best
        # correspondence table at the best offset
        corr = collections.defaultdict(collections.Counter)
        for y in range(h):
            for x in range(w):
                v = rows[y][x]
                if v < 0:
                    continue
                yy, xx = y0 + y + dy, x0 + x + dx
                corr[v][tuple(int(t) for t in A[yy][xx])] += 1
        consistent = sum(1 for v, c in corr.items() if c.most_common(1)[0][1] / sum(c.values()) > 0.9)
        print(f"{name:14s} k{k:<3d} {w}x{h} best_eq={rate*100:5.1f}% at dx{dx:+d} dy{dy:+d} "
              f"idx={len(corr)} consistent_idx(>90%)={consistent}")
        if rate > 0.2:
            for v, c in sorted(corr.items(), key=lambda kv: -sum(kv[1].values()))[:5]:
                tot = sum(c.values())
                top = c.most_common(2)
                print(f"    idx{v:3d} conv{conv[v]} n={tot:4d} -> "
                      + " ".join(f"{cc}{c2i.get(cc, ['-'])}x{n}" for cc, n in top))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
