#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t200 — K census: the COSMOSWnd star-pip type field (star_record+0x00).

Law under test (docs/re/planets-ui.md S6, derived from FUN_00029788's star
blit site 0x298dc): the star-pip blit SELECTOR is SEL = 4*K + cls, where
K = u32 [star_record + 0x00] and star_record = 0x13bc5 + 0x60*star_index
(runtime B + 0x82bb0 + those; pointer law), iterated over the window's star
list built by FUN_00028fc0 (count = u16 [0x16145]).

cos_star.shp has 55 records (k0..k54). The t196/t197 dims-zero residue is
k40..k51.  SEL reaches k40 iff K >= 10, k51 iff K == 12 & cls == 3.
So a census of K bounds whether the residue is addressable AT ALL.

Exit 0 = census produced (prints histogram + SEL reach). 2 = harness error.
"""
import glob
import os
import struct
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_slot as S

OFF = 0x82BB0          # payload pool base (pointer law)
STAR_BASE = 0x13BC5    # static star-record table base
STAR_STRIDE = 0x60
NUM_STARS = 0x16145    # u16 count word read by FUN_00028fc0


def main():
    pay = open("work/ascend_payload.bin", "rb").read()
    anch = S.anchors_cached(".", pay)
    hist = {}
    nsave = 0
    for f in sorted(glob.glob("work/r1/playcap/save/*.sav")):
        mem = zipfile.ZipFile(f).read("Memory")
        B = S.base_of(mem, anch)
        if B is None:
            print(f"  {os.path.basename(f)}: no base vote", file=sys.stderr)
            continue
        n = struct.unpack_from("<H", mem, B + OFF + NUM_STARS)[0]
        for i in range(n):
            k = struct.unpack_from("<I", mem, B + OFF + STAR_BASE + STAR_STRIDE * i)[0]
            hist[k] = hist.get(k, 0) + 1
        nsave += 1
    if not nsave:
        return 2
    lo, mx = min(hist), max(hist)
    print(f"saves={nsave} K range {lo}..{mx}")
    print("K histogram:", dict(sorted(hist.items())))
    print(f"SEL = 4K+cls reach: min {4*lo} max {4*mx+3}")
    for target in (40, 51, 52, 54):
        k_needed = target // 4
        reach = k_needed <= mx
        print(f"  record k{target}: needs K>={k_needed} -> "
              f"{'REACHABLE per census' if reach else 'NOT reachable (census bound)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
