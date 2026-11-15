#!/usr/bin/env python3
# t390 witness 2: is 0opening.shp val-15/145 the vendor's LABEL GLYPHS?
# Sweep dx,dy shifts of the strip's {15,145} ink mask against the shot's
# white(44) mask inside band 0 (capture rows 240..269, x 159..477), and
# report row lengths of the un-clamped walk (does the stream overrun W=318?).
import struct
from collections import Counter

ROOT = "/home/hrethric/projects/ascendancy"
SHP = ROOT + "/extracted/ascend01/data/0opening.shp"
SHOT = ROOT + "/docs/assets/refcap/original-title-menu.png"


def load(path):
    d = open(path, "rb").read()
    n = struct.unpack("<I", d[4:8])[0]
    starts = [0x10 + struct.unpack("<I", d[8:12])[0]] + \
             [struct.unpack("<Q", d[0x10 + 8 * k:0x18 + 8 * k])[0] for k in range(n - 1)]
    return d, n, starts


def walk(d, off):
    """Unbounded walk: 30 rows, no clamp, report lengths."""
    p = off
    rows = []
    for _ in range(30):
        row = []
        while True:
            C = d[p]; p += 1
            if C == 0:
                break
            if C == 1:
                L = d[p]; p += 1; row.extend([None] * L)
            elif C & 1:
                k = C >> 1; row.extend(d[p:p + k]); p += k
            else:
                k = C >> 1; v = d[p]; p += 1; row.extend([v] * k)
        rows.append(row)
    return rows, p


def main():
    from PIL import Image
    shot = Image.open(SHOT)
    sp = shot.tobytes(); SW, SH = shot.size
    d, n, starts = load(SHP)
    rows, endp = walk(d, starts[0] + 8)
    lens = [len(r) for r in rows]
    print("k0 unclamped row lengths:", lens)
    print("stream end offset:", hex(endp), "vs start", hex(starts[0]))
    # ink mask of the strip
    ink = set()
    for sy, r in enumerate(rows):
        for sx, v in enumerate(r):
            if v in (15, 145):
                ink.add((sx, sy))
    # white mask of band 0 (capture rows 240..269, x 159..477)
    white = set()
    for cy in range(240, 270):
        for x in range(159, 478):
            if sp[cy * SW + x] == 44:
                white.add((x, cy))
    print("ink", len(ink), "white", len(white))
    best = []
    for dy in range(-10, 11):
        for dx in range(-40, 11):
            inter = sum(1 for (sx, sy) in ink
                        if (sx + 159 + dx, 240 + sy + dy) in white)
            best.append((inter, dx, dy))
    best.sort(reverse=True)
    print("top shifts (inter, dx, dy):", best[:8])
    # column extent of the shot white text in band 0
    xs = sorted(set(x for x, y in white))
    ys = sorted(set(y for x, y in white))
    print("white text cols", xs[0], "..", xs[-1], "rows", ys[0], "..", ys[-1])
    xis = sorted(set(sx for sx, sy in ink))
    yis = sorted(set(sy for sx, sy in ink))
    print("ink cols", xis[0], "..", xis[-1], "rows", yis[0], "..", yis[-1])


if __name__ == "__main__":
    main()
