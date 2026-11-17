#!/usr/bin/env python3
"""t414 census: record dims of shp libs (container law rewrite/src/formats/shp.h)."""
import struct

def census(path):
    data = open(path, 'rb').read()
    magic = data[:4]
    count, tsz = struct.unpack_from('<II', data, 4)
    starts = [struct.unpack_from('<Q', data, 0x10 + 8 * i)[0] for i in range(count - 1)]
    out = []
    for k in range(count):
        rec = (0x10 + tsz) if k == 0 else starts[k - 1]
        off = rec if k == 0 else rec + 0x10
        try:
            w, h = struct.unpack_from('<II', data, off)
        except Exception:
            w = h = 0
        out.append((k, w, h))
    return magic.decode(errors='replace'), count, out

import sys
for lib in sys.argv[1:]:
    p = f'/tmp/uishow/extracted/ascend01/data/{lib}'
    m, c, o = census(p)
    print(lib, 'magic', m, 'count', c)
    print(' dims:', o)
