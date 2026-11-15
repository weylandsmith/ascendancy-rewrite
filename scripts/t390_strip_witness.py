#!/usr/bin/env python3
# t390 witness: does 0opening.shp state-N row-RLE, drawn with ONE colour,
# reproduce the vendor title screen's menu bands?
#
# Instruments:
#  A. strip value census (distinct values, counts)
#  B. positional test: strip-15 pixels vs shot-index-44 (white) pixels in the
#     same band -> is the strip the TEXT or the BACKGROUND?
#  C. band-flatness law: every capture pixel inside a button rect is in the
#     flat fill colour or the text colour (measured, per band)
# Run under the VENV python (t327 INTERPRETER LAW: system 3.13 has no PIL).
import struct
import sys
from collections import Counter

ROOT = "/home/hrethric/projects/ascendancy"
SHP = ROOT + "/extracted/ascend01/data/0opening.shp"
SHOT = ROOT + "/docs/assets/refcap/original-title-menu.png"
# windows.txt button column law (boot.cpp kTitleButtons): x 159..477, h 30,
# pitch 40, first at logical y=200. Capture chrome offset +40 (refcap.md S1).
X0, Y0_LOGICAL, W, H, PITCH, N = 159, 200, 319, 30, 40, 7


def load_dir(path):
    d = open(path, "rb").read()
    n = struct.unpack("<I", d[4:8])[0]
    tsz = struct.unpack("<I", d[8:12])[0]
    starts = [0x10 + tsz] + [struct.unpack("<Q", d[0x10 + 8 * k:0x18 + 8 * k])[0]
                             for k in range(n - 1)]
    return d, n, starts


def walk(d, off, W_, H):
    """Row-RLE per docs/re/shp.md S9; writes CLAMP to W (vendor blit law)."""
    p = off
    rows = []
    for _ in range(H):
        row = []
        while True:
            C = d[p]
            p += 1
            if C == 0:
                break
            if C == 1:
                L = d[p]
                p += 1
                row.extend([None] * L)
            elif C & 1:
                k = C >> 1
                row.extend(d[p:p + k])
                p += k
            else:
                k = C >> 1
                v = d[p]
                p += 1
                row.extend([v] * k)
        rows.append(row[:W_])
    return rows


def main():
    from PIL import Image
    shot = Image.open(SHOT)
    sp = shot.tobytes()
    SW, SH = shot.size
    spal = shot.getpalette()

    d, n, starts = load_dir(SHP)
    print("A. strip census (%d records)" % n)
    all_rows = []
    for k in range(n):
        off = starts[k]
        if k == 0:
            W_, Hh = struct.unpack("<II", d[off:off + 8])
            stream = off + 8
        else:
            W_, Hh = struct.unpack("<II", d[off + 0x10:off + 0x18])
            stream = off + 0x18
        rows = walk(d, stream, W_, Hh)
        all_rows.append(rows)
        flat = [v for r in rows for v in r if v is not None]
        print("   k%d %dx%d distinct=%s" % (k, W_, Hh,
              dict(Counter(flat).most_common())))

    print("B. positional: strip value 15 vs shot white index 44 (per band)")
    for k in range(N):
        rows = all_rows[k]
        y0 = Y0_LOGICAL + PITCH * k + 40
        strip15 = set()
        strip145 = set()
        for sy in range(min(H, len(rows))):
            for sx in range(min(W, len(rows[sy]))):
                v = rows[sy][sx]
                if v == 15:
                    strip15.add((sx, sy))
                elif v == 145:
                    strip145.add((sx, sy))
        white = set()
        fill = set()
        for cy in range(y0, min(y0 + H, SH)):
            for x in range(X0, X0 + W):
                idx = sp[cy * SW + x]
                if idx == 44:
                    white.add((x - X0, cy - y0))
                else:
                    fill.add((x - X0, cy - y0))
        i15 = len(strip15.intersection(white))
        i145 = len(strip145.intersection(white))
        print("   k%d strip15=%4d strip145=%4d shot_white=%4d "
              "15∩white=%4d 145∩white=%4d" %
              (k, len(strip15), len(strip145), len(white), i15, i145))

    print("C. band closure law: pixels inside each button rect")
    for k in range(N):
        y0 = Y0_LOGICAL + PITCH * k + 40
        c = Counter(sp[cy * SW + x] for cy in range(y0, min(y0 + H, SH))
                    for x in range(X0, X0 + W))
        print("   k%d capture rows %d..%d palette: %s" %
              (k, y0, min(y0 + H, SH) - 1,
               [(i, tuple(spal[i * 3:i * 3 + 3]), nn) for i, nn in
                c.most_common(5)]))


if __name__ == "__main__":
    sys.exit(main())
