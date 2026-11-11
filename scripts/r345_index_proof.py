#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t345 PROOF STEP: are the item-23 slot byte3 values LIVE INDEXES into the
354-byte ship array, or dead completion constants?

Static law (work/t91_code_disasm.txt verbatim, FUN_000396cc 0x396cc..0x3975d):
    bound assert idx < 0x6b ; rec = 0x3a095 + idx*0x162
    assert DWORD [rec+0x54] hi-word != 0xffff   (0x39733 jne / assert 0x405)
FUN_00039760 (stamp, 0x39797..0x39806):
    idx = (ship_ptr - 0x3a095) / 0x162 ; assert idx < 0x6b ;
    assert [0x3a095+idx*0x162+0x54] hi != 0xffff ; word2 |= idx<<8
    PRE-ASSERTS 0x39780: `cmp si,[ecx+0x18]; jae ok` -> the assert fires when
    cell < cells, i.e. THE STAMP PATH IS FORBIDDEN ON SURFACE CELLS (orbital only).

Live law (docs/re/income-law.md T58 verbatim): ship array = DS+0x3a095 stride
0x162, DS = B + 0x82bb0; ship owner dword at rec+0x54 hi-word (aicode.md S2b,
`sar 0x10; cmp == race`). 0xFFFF = empty slot.

So: for every item-23 orbital slot row, resolve idx=byte3 and read the ship
owner. H_INDEX predicts a real race id (0..N) far more often than chance; the
completion-constant reading predicts nothing meaningful (idx 15/35 are just the
two hardcoded constants).

Also measures the item-table FLAGS words (DS:0x73e40+0x28*idx+6) to confirm the
bit8 gate of the completion marker block 0x39245 and the bit4/bit8 classes the
rewrite's orbitalThreatFor/shieldThreatFor use.

Exit 0 = ran; 2 = harness broken.
"""
import collections
import os
import struct as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_income_law as IL
from r1_sav_scan import build_anchors

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHIP_ITEM = 23
STRIDE = 0x162
ARRAY_OFF = 0x3a095
BOUND = 0x6b

DIRS = [os.path.join(ROOT, x) for x in (
    "work/r1/playcap", "work/r1/bank-t1254", "work/r1/t340-shieldc-20261108-014705")]


def main():
    try:
        pay = open(IL.PAY, "rb").read()
        build_anchors(pay)
    except Exception as e:
        print("ANCHORS FAIL:", e)
        return 2

    resolved = collections.defaultdict(collections.Counter)  # idx -> owner hist
    idx_seen = collections.Counter()
    surface_stamp = 0
    orbital_rows = 0
    marker_split = collections.Counter()
    flags_rows = {}
    n_saves = 0

    for d in DIRS:
        try:
            slots = IL.load_slots(d)
        except Exception as ex:
            print("load_slots fail", d, ex)
            continue
        for f, m, B in slots:
            ds = B + 0x82BB0
            if ds + ARRAY_OFF + BOUND * STRIDE + 0x58 > len(m):
                continue
            if not flags_rows:
                for k in range(0, 40):
                    base = ds + 0x73E40 + k * 0x28
                    if base + 0x28 > len(m):
                        break
                    flags_rows[k] = st.unpack_from("<H", m, base + 6)[0]
            count_word = st.unpack_from("<H", m, ds + 0x43483)[0] \
                if ds + 0x43485 <= len(m) else None
            n_saves += 1
            for rb, cells, cap, arr in IL.find_records(m):
                if not (0 <= arr and arr + cap * 4 <= len(m)) or cap == 0 or cap > 200:
                    continue
                for cell in range(cap):
                    if m[arr + cell * 4 + 1] != SHIP_ITEM:
                        continue
                    w2 = st.unpack_from("<H", m, arr + cell * 4 + 2)[0]
                    idx = (w2 >> 8) & 0x7F
                    if idx >= BOUND:
                        resolved[-1][(w2 >> 8) & 0xFF] += 1
                        continue
                    ship = ds + ARRAY_OFF + idx * STRIDE
                    owner_hi = st.unpack_from("<H", m, ship + 0x54)[0]
                    idx_seen[idx] += 1
                    resolved[idx][owner_hi] += 1
                    if cell < cells:
                        surface_stamp += 1
                    else:
                        orbital_rows += 1
                    # bit0 (active) / bit1 split of byte3 for the marker class
                    bi = m[arr + cell * 4 + 1]
                    if bi in (18, 19, 23, 26, 27):
                        marker_split[(bi, w2 & 1, (w2 >> 1) & 1,
                                      "b3zero" if (w2 >> 8) == 0 else "b3set",
                                      "surf" if cell < cells else "orbit")] += 1

    print(f"saves used: {n_saves}")
    print(f"item-23 rows resolved: {sum(idx_seen.values())} "
          f"(orbital {orbital_rows}, surface-cell {surface_stamp})")
    print("\n=== idx -> ship-array owner hi-word (rec+0x54) ===")
    tot_live = 0
    tot = 0
    for idx in sorted(idx_seen):
        c = resolved[idx]
        n = sum(c.values())
        tot += n
        live = sum(v for k, v in c.items() if k != 0xFFFF)
        tot_live += live
        top = sorted(c.items(), key=lambda kv: -kv[1])[:4]
        print(f"  idx {idx:3d} n={n:4d} live={live:4d} "
              f"owners={[(hex(k), v) for k, v in top]}")
    print(f"\nTOTAL: {tot_live}/{tot} resolved ship slots are NON-empty "
          f"(owner != 0xFFFF) = "
          f"{100.0*tot_live/tot if tot else 0:.2f}%")
    print("\n=== MARKER SPLIT (item, bit0 active, bit1, byte3, cell class) ===")
    for k in sorted(marker_split):
        print(f"  item {k[0]:2d} bit0={k[1]} bit1={k[2]} {k[3]:6s} {k[4]:5s} n={marker_split[k]}")

    print("\n=== item-table FLAGS words (DS:0x73e40+0x28*i+6) ===")
    for k in sorted(flags_rows):
        w = flags_rows[k]
        marks = []
        if w & 0x8:
            marks.append("bit8(MARKER-GATE)")
        if w & 0x4:
            marks.append("bit4(ORBITAL-DEF)")
        print(f"  item {k:2d} flags={w:#06x} {' '.join(marks)}")
    print("\nVERDICT BASIS: a high non-empty rate on DIFFERENT idx values proves "
          "byte3 addresses live ship records (H_INDEX). The completion-constant "
          "reading cannot produce per-idx variation (r345_marker_census measured "
          "17 distinct values on item-23 rows).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
