#!/usr/bin/env python3
"""tNG-C3 k10 WHEEL AUTOPSY — decode 3cfgnew k10/k11/k12 with the S9 codec
and dump row profiles to find the lens-band artifact (docs/re/_wip_tNGC.md
F15-1). Read-only; uses the unified-law X walk (span-unbounded)."""
import struct, sys

P = "extracted/ascend01/data/3cfgnew.shp"

def parse(p):
    d = open(p, "rb").read()
    count = struct.unpack_from("<I", d, 4)[0]
    tsz = struct.unpack_from("<I", d, 8)[0]
    te = 0x10 + tsz
    starts = [te] + [struct.unpack_from("<Q", d, 0x10 + 8 * k)[0] for k in range(count - 1)]
    ends = starts[1:] + [len(d)]
    return d, count, starts, ends

def dims(d, rec, k):
    off = 0x00 if k == 0 else 0x10
    a, b = struct.unpack_from("<II", d, rec + off)
    return a, b

def walk(d, i, H, W, limit):
    """S9 grammar; returns list of rows; each row = list of (x, val|None)."""
    rows = []
    for r in range(H):
        x = 0
        row = []
        while True:
            if i >= limit:
                row.append(("EOF", i)); return rows, i, "EOF"
            C = d[i]; i += 1
            if C == 0:
                break
            if C == 1:
                L = d[i]; i += 1
                row.append(("skip", x, L)); x += L
            elif C & 1:
                n = C >> 1
                vals = list(d[i:i+n]); i += n
                row.append(("lit", x, vals)); x += n
            else:
                n = C >> 1
                v = d[i]; i += 1
                row.append(("run", x, n, v)); x += n
        rows.append(row)
    return rows, i, "OK"

d, count, starts, ends = parse(P)
print(f"N={count}")
for k in (10, 11, 12):
    rec = starts[k]
    a, b = dims(d, rec, k)
    off = 0x08 if k == 0 else 0x18
    print(f"\n== k{k} rec=0x{rec:x} span=0x{ends[k]:x} dims pair=({a},{b}) stream=rec+0x{off:x}")
    for (W, H) in ((a, b), (b, a)):
        rows, i, st = walk(d, rec + off, H, W, len(d))
        # per-row max x touched
        def maxx(row):
            m = 0
            for e in row:
                if e[0] == "skip": m = max(m, e[1] + e[2])
                elif e[0] == "lit": m = max(m, e[1] + len(e[2]))
                elif e[0] == "run": m = max(m, e[1] + e[2])
            return m
        mx = [maxx(r) for r in rows]
        over = [(ri, m) for ri, m in enumerate(mx) if m > W]
        print(f"  orient W={W} H={H}: {st} at 0x{i:x} rows={len(rows)} maxx>W rows: {over[:8]}{'...' if len(over)>8 else ''} overall max={max(mx) if mx else 0}")
