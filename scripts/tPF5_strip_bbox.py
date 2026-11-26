#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""tPF5 (D28 item 10): INDUSTRY-TILE BBOX CENSUS.

The port blits planres/planind/planpro record sel at the windows.txt rect
ORIGIN (rewrite/src/ui/ui.cpp:2356 blitShape(ren, gl, rec, rect.x0, rect.y0))
with NO (L,T) term, while the cited vendor placement law is
dest = anchor + (L,T) (FUN_0005d5a1, banked tA1 in
rewrite/src/formats/shp.cpp:148-163).

This prints, per record of the three gauge libs, the SIGNED bbox quad and
both placement readings, so the vertical-offset claim in D28 item 10 can be
adjudicated against the rect:

  L T R B      signed quad at b_off (== stream-0x10), port shp.cpp:176-179
  W H          bbox-diff dims (tA1 law)
  origin_blit  y-extent the PORT paints: [y0, y0+H)
  anchored     y-extent the VENDOR law paints: [y0+T, y0+T+H)
  band         pixels of the 100-tall rect each reading leaves unpainted

Rects verbatim from extracted/ascend00/windows.txt (PLRES/PLIND/PLPRO).
"""
import struct
import sys

DATA = "/home/hrethric/projects/ascendancy/extracted/ascend01/data"
LIBS = [("planres.shp", 7, 7, 114, 106),
        ("planind.shp", 123, 7, 230, 106),
        ("planpro.shp", 239, 7, 346, 106)]


def load(path):
    img = open(path, "rb").read()
    magic, count, tsz = struct.unpack_from("<III", img, 0)
    assert magic == 0x30312E31, (path, hex(magic))
    assert tsz == 8 * (count + 1), (path, tsz)
    te = 0x10 + tsz
    starts = [te]
    for k in range(count - 1):
        raw = struct.unpack_from("<Q", img, 0x10 + 8 * k)[0]
        starts.append(raw)
    return img, count, starts


def main():
    for name, x0, y0, x1, y1 in LIBS:
        img, count, starts = load(f"{DATA}/{name}")
        rect_h = y1 - y0 + 1
        rect_w = x1 - x0 + 1
        print(f"== {name}  rect {x0},{y0}..{x1},{y1} ({rect_w}x{rect_h})  "
              f"records={count}")
        print("  rec  L     T     R     B      W    H   | port y[..]  "
              "anch y[..]  portBand anchBand  streamCross")
        for k in range(count):
            rec = starts[k]
            nxt = starts[k + 1] if k + 1 < count else len(img)
            s_off = rec + 8 if k == 0 else rec + 0x18
            b_off = s_off - 0x10
            L, T, R, B = struct.unpack_from("<iiii", img, b_off)
            W = R - L + 1
            H = B - T + 1
            port_band = rect_h - H
            anch_band = rect_h - H
            # stream-cross probe: does the record's own span look short vs
            # its H rows? (X-class marker, shp.md S21/S20.2)
            span = nxt - s_off
            cross = "X" if span < H else "."
            print(f"  {k:3d} {L:5d} {T:5d} {R:5d} {B:5d} {W:5d} {H:4d}  | "
                  f"{y0:4d}..{y0+H:4d}  {y0+T:4d}..{y0+T+H:4d}  "
                  f"{port_band:8d} {anch_band:8d}  {cross} span={span}")
        print()


if __name__ == "__main__":
    sys.exit(main())
