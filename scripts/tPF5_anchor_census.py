#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""tPF5: (L,T) BLAST-AREA CENSUS over every lib the port blits via blitShape.

FUN_0005caac [verified raw bytes work/ascend_restored.bin 0x5cb41..0x5cb85]:
  0x5cb44 add [ebp+0x14], [s+4]      screen_x += shapeStruct.clipL (>=0)
  0x5cb4a add [ebp+0x18], [s+8]      screen_y += shapeStruct.clipT (>=0)
  0x5cb5b esi = payload + [payload+8+8*sel]        (entry)
  0x5cb61 dest_x = [esi+0x8]  + screen_x           <-- entry L ADDED
  0x5cb6a dest_y = [esi+0xc]  + screen_y           <-- entry T ADDED
  0x5cb73 right  = [esi+0x10] + screen_x
  0x5cb7c bottom = [esi+0x14] + screen_y
  0x5cb85 stream = entry + 0x18
=> dest = anchor + (L,T). A caller that passes a rect ORIGIN and drops (L,T)
misplaces any record whose bbox does not start at (0,0).

For each lib the port draws, print how many records have L!=0 or T!=0, and the
distinct (L,T) values. A lib whose blitted records are ALL (0,0) is anchor-blind
(port placement equivalent); a lib with T!=0 is mis-placed by the port.
"""
import struct
import sys

DATA = "/home/hrethric/projects/ascendancy/extracted/ascend01/data"

# name -> (records the port actually blits, per ui.cpp call sites)
LIBS = [
    ("planres.shp", range(21)),   # strip gauge 0
    ("planind.shp", range(21)),   # strip gauge 1
    ("planpro.shp", range(21)),   # strip gauge 2
    ("17np.shp", [1, 2, 3, 4]),   # pop grid k1/k2/k3 + field k4
    ("planitem.shp", range(40)),  # structure art + project thumb + ship row
    ("smship19.shp", range(3)),   # ship-row permutation libs (rec 0 blitted)
]
PLANAL = [f"planal{r}.shp" for r in range(1)]  # probed separately below


def load(path):
    img = open(path, "rb").read()
    magic, count, tsz = struct.unpack_from("<III", img, 0)
    if magic != 0x30312E31:
        return None, None, None
    te = 0x10 + tsz
    starts = [te] + [struct.unpack_from("<Q", img, 0x10 + 8 * k)[0]
                     for k in range(count - 1)]
    return img, count, starts


def quad(img, count, starts, k):
    rec = starts[k]
    s_off = rec + 8 if k == 0 else rec + 0x18
    return struct.unpack_from("<iiii", img, s_off - 0x10)


def main():
    for name, idxs in LIBS:
        img, count, starts = load(f"{DATA}/{name}")
        if img is None:
            print(f"{name:16s} MISSING/not-shp")
            continue
        vals = {}
        bad = 0
        for k in idxs:
            if k >= count:
                continue
            try:
                L, T, R, B = quad(img, count, starts, k)
            except struct.error:
                continue
            vals[(L, T)] = vals.get((L, T), 0) + 1
            if L != 0 or T != 0:
                bad += 1
        print(f"{name:16s} blitted={len([k for k in idxs if k < count]):3d} "
              f"nonzero-anchor={bad:3d}  (L,T)->count {dict(sorted(vals.items()))}")

    # every planal lib, all 5 records each (planet disc art)
    tot = 0
    badtot = 0
    seen = {}
    import glob
    import os
    for p in sorted(glob.glob(f"{DATA}/planal*.shp")):
        img, count, starts = load(p)
        if img is None:
            continue
        for k in range(count):
            try:
                L, T, R, B = quad(img, count, starts, k)
            except struct.error:
                continue
            tot += 1
            if L != 0 or T != 0:
                badtot += 1
                seen.setdefault((L, T), 0)
                seen[(L, T)] += 1
    print(f"\nplanal* (all libs, all recs): total={tot} nonzero-anchor={badtot}")
    if seen:
        items = sorted(seen.items(), key=lambda kv: -kv[1])[:12]
        print("  most common nonzero (L,T):", items)
    return 0


if __name__ == "__main__":
    sys.exit(main())
