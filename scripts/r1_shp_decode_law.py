#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r1_shp_decode_law.py — OQ-005 codec validation (t61).

Grammar recovered VERBATIM from FUN_0005caac instruction stream
(work/ascend_restored.bin 0x5cca3..0x5ce77; docs/re/shp.md S9):
  row stream, repeat:
    C = next byte
    C == 0        -> end of row
    C == 1        -> L = next byte; skip L pixels (transparent)
    C odd, C > 1  -> literal copy of C>>1 bytes from stream
    C even, C > 0 -> run: next byte repeated C>>1 times
  header law [asm 0x5cabe/0x5cac7 + stride use]: dims fields store W-1, H-1;
  header = [ptr][W-1][H-1] (12 B) at record start; stream follows at +12.
  The blit's row loop iterates over the CLIP rect, not shape height: rows
  outside the rect are stream-SKIPPED (0x5cc42: control, +C>>1 after
  lit/run, +1 after skip byte, C==0 advances). So a record's stream =
  ANY number of well-formed row streams; validation discriminator =
  EXACT-SPAN consumption from stream start to record end, every record,
  with every row's pixels <= W (skip may exceed W: no clip).

Prefix law per record (shp.md S3): rec0 dims u32-pair at record start
(header size 12, stream at +12); rec1+ dims u16-pair; prefix length then
either 8 (zero u32 follows dims, 39 libs) or 12 (two more u16s, 124 libs).
This script decides per-LIBRARY between 8 and 12 by exact-span.
Opaque header variants (10 expl libs) are reported separately.
"""
import os, struct, sys, glob, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAGIC = b"1.10"

def parse(p):
    d = open(p, "rb").read()
    if d[:4] != MAGIC: raise ValueError("magic")
    count = struct.unpack_from("<I", d, 4)[0]
    tsz = struct.unpack_from("<I", d, 8)[0]
    if tsz != 8 * (count + 1): raise ValueError("table size")
    table_end = 0x10 + tsz
    # S1 law: slots 0..N-2 point to records 1..N-1; slots N-1, N are
    # library metadata (never used here). rec0 sits at table_end; the last
    # record runs to EOF.
    starts = [table_end]
    for k in range(count - 1):
        starts.append(struct.unpack_from("<Q", d, 0x10 + 8 * k)[0])
    starts.append(len(d))
    spans = [starts[i + 1] - starts[i] for i in range(len(starts) - 1)]
    starts = starts[:-1]
    if any(s <= 0 for s in spans): raise ValueError("span")
    return d, count, table_end, starts, spans

def rows_from(buf, i, end, W):
    """walk row streams from i; return rows count if EXACTLY consumes to end
    with every-row-pixels<=W, else None."""
    rows = 0
    while i < end:
        x = 0
        while True:
            if i >= end: return None
            C = buf[i]; i += 1
            if C == 0:
                if x > W: return None
                break
            if C == 1:
                if i >= end: return None
                x += buf[i]; i += 1
                if x > W: return None
            elif C & 1:
                n = C >> 1
                x += n; i += n
                if x > W or i > end: return None
            else:
                n = C >> 1
                i += 1
                x += n
                if x > W or i > end: return None
        rows += 1
    return rows

def try_library(path):
    d, count, table_end, starts, spans = parse(path)
    rec0_ok = False
    # rec0: u32 dims pair (8 B header), stream at +8 (shp.md S1: listbox
    # rec0 dims then stream directly)
    w0, h0 = struct.unpack_from("<II", d, starts[0])
    if 0 < w0 <= 4095 and 0 < h0 <= 4095:
        r = rows_from(d, starts[0] + 8, starts[0] + spans[0], w0 + 1)
        if r is not None: rec0_ok = True
    if not rec0_ok:
        return ("opaque-rec0", None, None, None)
    # rec1+: u16 dims pair AT RECORD START; then zero u32 (prefix 8) or
    # two more u16s (prefix 12)
    for pfx in (8, 12):
        ok = True
        for k in range(1, count):
            s = starts[k]; sp = spans[k]
            if sp < pfx + 1: ok = False; break
            w16, h16 = struct.unpack_from("<HH", d, s)
            W = w16 + 1
            if W < 1 or W > 4095: ok = False; break
            if rows_from(d, s + pfx, s + sp, W) is None: ok = False; break
        if ok:
            return ("decode-ok", rec0_ok, pfx, count)
    return ("rec0-only", rec0_ok, None, count)

def main():
    libs = sorted(glob.glob(os.path.join(ROOT, "extracted", "**", "*.shp"), recursive=True))
    tally = collections.Counter()
    details = []
    for p in libs:
        try:
            state, r0, pfx, n = try_library(p)
        except Exception as e:
            tally["container-error"] += 1
            details.append((os.path.relpath(p, ROOT), "container-error", str(e)))
            continue
        tally[state + (f"/pfx{pfx}" if pfx else "")] += 1
        if state != "decode-ok":
            details.append((os.path.relpath(p, ROOT), state, f"rec0_ok={r0} n={n}"))
    print("libraries:", len(libs))
    for k, v in sorted(tally.items()): print(f"  {k}: {v}")
    for d in details[:40]: print("  -", *d)

if __name__ == "__main__":
    main()
