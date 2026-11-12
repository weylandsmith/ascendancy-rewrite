#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t379 — DEATH vs RECLAIM SHAPES: count-word census over the playtest banks.

Question (queue row t379, witness S64 M5): at the 1253->1254 boundary tl
rows show s12 name-cleared + kind 4->0 (corpse RETAINED inside the window)
while s40 'Intil-Za' VANISHED from the rows (window length 41->40). Are these
TWO different vendor shapes, or ONE law read two ways?

Candidate discriminator (the fleet-list law, ships.md item 3 / r1_slot.
ship_array_law): the tl row window is `range(min(count_word>>16, 0x6b))`
(r1_playcap_watch.py process(): base, n = ship_array_law; ship_raw for
k in range(min(n,0x6b))). A slot can therefore disappear from the rows TWO
ways with different underlying memory states:
  (A) corpse-retained: record stays in the window, marker row (handle
      0xffff0000, kind 0, name cleared) — the C4 finalizer shape 0x249b4.
  (B) window-shrink: the COUNT WORD itself decremented below the slot index,
      so the record is simply outside the scanned window (the count word is
      NOT the census — live rows exist past it; ships.md fleet-list item 3,
      MEASURED 4 live at indices >= 30 of 30).

Measurements (banks are on disk; ZERO new capture):
 1. per-save count word (u32 @ B+kDataSeg+0x43489 >> 16) + turn for both
    banks; the boundary delta is the direct test of (B).
 2. per-save DEAD-MARKER census over the FULL 0..0x6a window (marker law:
    (u32@+0x54)>>16 == 0xffff, r256c oc_of) — corpse rows at t1254 in the
    full window support (A); their absence supports pure-shrink.
 3. slot 12 and slot 40 detail per save: handle u32@+0x54, name bytes
    @+0x34 (first 20, NUL-cut), kind @+0x58 — the M5 pair adjudicated at
    the record level, not the tl-row level.

Usage: r379_shape_census.py DIR1 DIR2 ...
"""
import glob
import os
import struct
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r1_slot as S

COUNT_X = 0x43489          # ShipSave::kCountX / r1_slot SHIP['count']
STRIDE = 0x162
SLOTS = 0x6b               # ShipSave::kArraySlots


def main():
    dirs = sys.argv[1:]
    if not dirs:
        print(__doc__)
        return 2
    pay = S.load_payload(os.getcwd())
    anch = S.anchors_cached(os.getcwd(), pay)
    for d in dirs:
        files = sorted(glob.glob(os.path.join(d, "*.sav")), key=os.path.getmtime)
        print(f"== {d} ({len(files)} saves)")
        for f in files:
            try:
                mem = zipfile.ZipFile(f).read("Memory")
            except Exception as e:
                print(f"  {os.path.basename(f)} unzip {repr(e)[:60]}")
                continue
            B = S.base_of(mem, anch)
            if B is None or len(mem) < 0x90000:
                print(f"  {os.path.basename(f)} base FAILED")
                continue
            M = B + S.OFF
            cw = struct.unpack_from("<I", mem, M + COUNT_X)[0] >> 16
            turn = S.read_slot(f, mem, B).get("turn")
            base = B + S.OFF + S.SHIP["x"]
            dead, live = [], 0
            for k in range(SLOTS):
                r = base + k * STRIDE
                if r + STRIDE > len(mem):
                    break
                h = struct.unpack_from("<I", mem, r + 0x54)[0]
                if h >> 16 == 0xFFFF:
                    dead.append(k)
                else:
                    live += 1
            detail = []
            for k in (12, 40):
                r = base + k * STRIDE
                h = struct.unpack_from("<I", mem, r + 0x54)[0]
                nm = mem[r + 0x34:r + 0x34 + 20].split(b"\x00")[0].decode("latin-1", "replace")
                kind = mem[r + 0x58]
                detail.append(f"s{k} h={h:#010x} kind={kind} name={nm!r}")
            print(f"  {os.path.basename(f)} turn={turn} count={cw} "
                  f"fullwin_dead={len(dead)}@{dead[:12]} live={live} | " + " | ".join(detail))
    return 0


if __name__ == "__main__":
    sys.exit(main())
