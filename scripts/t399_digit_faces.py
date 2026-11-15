#!/usr/bin/env python3
"""t399: decode 1starmap.shp digit faces k55..k64 (DIGITFRAMES 55 law,
docs/re/ui-runtime.md) and print ASCII art so the digit->frame mapping seam
closes by measurement. RLE grammar: docs/re/shp.h header (shp.md S9)."""
import struct, sys

def load(path):
    d = open(path, 'rb').read()
    magic, count, tsz = struct.unpack_from('<III', d, 0)
    starts = [0x10 + tsz] + list(struct.unpack_from('<%dQ' % (count - 1), d, 0x10))
    return d, count, starts

def decode(d, rec, k):
    off = rec if k == 0 else rec + 0x10
    w, h = struct.unpack_from('<II', d, off)
    pos = off + 8
    rows = []
    for _ in range(h):
        row = []
        while len(row) < w:
            c = d[pos]; pos += 1
            if c == 0:
                break
            if c == 1:
                row += [-1] * d[pos]; pos += 1      # skip = transparent
            elif c & 1:
                n = c >> 1
                row += list(d[pos:pos + n]); pos += n
            else:
                row += [d[pos]] * (c >> 1); pos += 1
        rows.append(row[:w])
    return w, h, rows

d, count, starts = load(sys.argv[1] if len(sys.argv) > 1
                        else 'extracted/ascend01/data/1starmap.shp')
for k in range(55, 65):
    w, h, rows = decode(d, starts[k], k)
    # ink = any nonzero non-skip value; vendor digits are single-ink
    print(f"k{k} {w}x{h}")
    for r in rows:
        print(''.join('#' if v > 0 else ('.' if v == -1 else ' ') for v in r))
