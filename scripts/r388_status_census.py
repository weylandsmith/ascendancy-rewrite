#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""t388 — census of 10status.shp (STATUSWND chrome, windows.txt TYPE 16).

Why this file first: STATE.md t388 mandates "census it first (dims per V/A
law)". The V/A/X per-record law is the banked one (docs/re/shp.md S16/S17 +
t182/t197 amendments) and is imported verbatim from scripts/r1_shp_unifiedlaw
.py rather than re-implemented, so the census cannot drift from the law.

Prints, per record: index, dims at the canonical slot (k0: u32 pair @rec;
k>=1: u32 pair @rec+0x10), orientation as decoded, span [rec,nxt), law tag,
and the painted-pixel profile for the chrome decision (does k0 cover 640x480,
is it mostly opaque backdrop or mostly skip-pixels).

Also censuses 1starmap.shp frames 3/4/5/7 (the sidebar icon law, ui-runtime
.md §6a) so the rail icons land on cited record indices.

Exit 0 = census produced; 2 = harness error (missing file).
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_shp_unifiedlaw as U

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def census(path, want=None):
    if not os.path.isfile(path):
        print("MISSING:", path)
        return 2
    d, count, te, tsz, starts, ends = U.parse(path)
    print(f"# {os.path.basename(path)}  records={count} table_end={te} "
          f"table_size={tsz} filesize={len(d)}")
    print("rec  tag  W    H    span           past  rows  opaque  "
          "skiprows  firstrow_opaque")
    for k in range(count):
        if want is not None and k not in want:
            continue
        rec, nxt = starts[k], ends[k]
        tag = U.rec_state(d, k, rec, nxt)
        d_off = rec if k == 0 else rec + 0x10
        s_off = rec + 8 if k == 0 else rec + 0x18
        if d_off + 8 > len(d):
            print(f"{k:>3}  {tag}")
            continue
        w0, h = struct.unpack_from("<II", d, d_off)
        past = rows = opaque = skiprows = first = 0
        W, H = w0, h
        # Paint profile straight from the banked free walk (x_profile's dict
        # carries counts, not the per-row list).
        if 0 < H <= 4096 and 0 < W <= 4096:
            r = U.rowwalk_free(d, s_off, H, W)
            if r is None and W != H:
                r = U.rowwalk_free(d, s_off, W, H)
                W, H = H, W
            if r is not None:
                i_after, painted = r
                past = max(0, i_after - nxt)
                rows = len(painted)
                opaque = sum(painted)
                skiprows = sum(1 for p in painted if p == 0)
                first = painted[0] if painted else 0
        print(f"{k:>3}  {tag:<4} {W:<4} {H:<4} [{rec:#x},{nxt:#x}) "
              f"{past:<5} {rows:<5} {opaque:<7} {skiprows:<9} {first}")
    return 0


def main():
    rc = census(os.path.join(ROOT, "extracted/ascend01/data/10status.shp"))
    print()
    rc |= census(os.path.join(ROOT, "extracted/ascend01/data/1starmap.shp"),
                 want={3, 4, 5, 7, 65, 66})
    return rc


if __name__ == "__main__":
    sys.exit(main())
