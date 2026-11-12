#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t377 — RAM design-row readout for the gizmos the witnesses key on.

Why: the M1 magnetron use committed at world-distance ~4700 while gizmos.txt
row 60 says Range 50 (gate operand Range<<5 = 1600 per raw 0x4cb76..0x4cb95).
Either the RAM row's +0x3a differs from the file column or the gate operand
story is wrong. Read the LOADED row directly: table base = B + 0x82bb0 +
0x7650c, stride 0x6a (t185 T1 law, 1368-member census). Columns per t87 map:
raw +0x32 cat, +0x36 power, +0x3a range, +0x3e level, +0x42 numUses,
+0x46 industry, +0x4a/+0x4e special, +0x33 flag word (t101 convention).
Prints name ptr-resolved? Names are DAT_00078484-heap strings — print the
+0x00 dword instead; identity comes from the row INDEX (file-order law T1).

Usage: r377_design_rows.py DIR [IDX ...]   (default IDX: 9 60 73)
"""
import glob
import os
import struct
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r1_slot as S

TABLE_OFF = 0x82bb0 + 0x7650c
STRIDE = 0x6A


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    d = sys.argv[1]
    idxs = [int(a) for a in sys.argv[2:]] or [9, 60, 73]
    pay = S.load_payload(os.getcwd())
    anch = S.anchors_cached(os.getcwd(), pay)
    for f in sorted(glob.glob(os.path.join(d, "*.sav")), key=os.path.getmtime)[-3:]:
        try:
            mem = zipfile.ZipFile(f).read("Memory")
        except Exception as e:
            print(f"{os.path.basename(f)} unzip {repr(e)[:60]}")
            continue
        B = S.base_of(mem, anch)
        if B is None:
            print(f"{os.path.basename(f)} base UNRESOLVED")
            continue
        print(f"== {os.path.basename(f)} B={hex(B)}")
        for i in idxs:
            p = B + TABLE_OFF + i * STRIDE
            cat = mem[p + 0x32]
            flags = struct.unpack_from("<H", mem, p + 0x33)[0]
            power, rng, level, uses, ind = struct.unpack_from("<5I", mem, p + 0x36)
            sp1, sp2 = struct.unpack_from("<2I", mem, p + 0x4a)
            print(f"  row {i:3d}: cat={cat} flags={flags:#06x} power={power} "
                  f"range={rng} level={level} numUses={uses} ind={ind} "
                  f"sp1={sp1} sp2={sp2}")


if __name__ == "__main__":
    main()
