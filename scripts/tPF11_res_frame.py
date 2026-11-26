#!/usr/bin/env python3
"""tPF11_res_frame.py — decode 20res.shp records (the research-screen
TYPE-100 STATENUMBER-20 frame lib, windows.txt:1756-1758) and report the
written/transparent structure of each record. Frame law: FUN_00030fb8
0x31004 blits record SHAPEFRAME at the window origin; RESWIN rect
7,46-476,472 (470x427 logical)."""
import struct, sys, os
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from r1_shp_decode_law import parse

LIB = "extracted/ascend01/data/20res.shp"

def decode_record(d, start, end, W, H):
    px = [[-1] * W for _ in range(H)]
    i = start
    for r in range(H):
        x = 0
        while True:
            if i >= end:
                return None
            c = d[i]; i += 1
            if c == 0:
                break
            if c == 1:                      # transparent skip
                x += d[i]; i += 1
                continue
            n = c >> 1
            if c & 1:                       # literal run of n bytes
                for k in range(n):
                    if x < W:
                        px[r][x] = d[i + k]
                    x += 1
                i += n
            else:                           # single-byte run
                v = d[i]; i += 1
                for xx in range(x, min(x + n, W)):
                    px[r][xx] = v
                x += n
    return px

def main():
    d, count, table_end, starts, spans = parse(LIB)
    print(f"lib {LIB}: {count} records, size {len(d)}")
    for k in range(count):
        w0, h0 = struct.unpack_from("<II", d, starts[k])
        W, H = w0 + 1, h0 + 1
        px = decode_record(d, starts[k] + 8, starts[k] + spans[k], W, H)
        if px is None:
            print(f"  k{k}: dims {W}x{H} span {spans[k]} DECODE-FAIL")
            continue
        nz = sum(1 for row in px for v in row if v >= 0)
        c = Counter(v for row in px for v in row if v >= 0)
        print(f"  k{k}: dims {W}x{H} span {spans[k]} written={nz} "
              f"top={c.most_common(6)}")
        if W <= 32 and H <= 40:
            for row in px:
                print("    " + "".join(" ." if v < 0 else f"{v:02x}"
                                       for v in row))
    # k1..k5 dims words looked odd in the quick pass; dump raw first 16B
    for k in range(count):
        print(f"k{k} raw:", d[starts[k]:starts[k]+16].hex())

if __name__ == "__main__":
    main()
