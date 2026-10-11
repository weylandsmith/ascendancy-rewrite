#!/usr/bin/env python3
"""r1_gizmo_fuel_table.py — t47 fuel/propulsion law measurement.

Static law (decompile FUN_0004a658 @0x4a658, per ship per turn):
  for each queued slot i < dword[ship+0x15a] (stride 7 from ship+0xab):
    t = slot byte +0 (type, != -1); slot dword +3 == -1 (uninit param)
    row = t*0x6a + base (base static DAT_0007653c family)
    if (w16[row+0x03] & 0x20):                    # maintenance class bit
        if dword[ship+0x88] >= dword[row+0x06]:
            dword[ship+0x88] -= dword[row+0x06]   # upkeep burn
    if byte[row+0x02] == 1:
        dword[ship+0x90] += dword[row+0x26]       # propulsion bonus
Runtime base = B + 0x82bb0 + 0x7653c (pointer law; verified by gate-bit
plausibility below).

Exit: 0 = propulsion bonuses measured as consistent small integers
      1 = rows unreadable / all-zero propulsion
      2 = harness broken
"""
import os
import struct
import sys
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_income_law as IL
from r1_sav_scan import build_anchors, find_base

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "work", "r1")
ROW = 0x6A


def runs():
    for d in sorted(os.listdir(BASE)):
        p = os.path.join(BASE, d)
        if not os.path.isdir(p):
            continue
        if os.path.isdir(os.path.join(p, "save")) or os.path.isdir(os.path.join(p, "ck")):
            yield p


def main():
    try:
        build_anchors(IL.PAY)
    except Exception as e:
        print("ANCHORS FAIL:", e)
        return 2
    saves = 0
    prop_hist = collections.Counter()
    gate_rows = collections.Counter()
    cost_hist = collections.Counter()
    for p in runs():
        try:
            slots = IL.load_slots(p)
        except Exception:
            continue
        for f, m, B in slots:
            if B is None:
                continue
            tb = B + 0x82bb0 + 0x7653c
            if tb + 80 * ROW > len(m):
                continue
            # plausibility gate: gate word bit5 set on a MODERATE number
            # of rows only (maintenance gizmos), propulsion flag on few
            n_gate = sum(1 for t in range(80)
                         if struct.unpack_from("<H", m, tb + t * ROW + 3)[0] & 0x20)
            if not (1 <= n_gate <= 40):
                continue
            saves += 1
            for t in range(80):
                r = tb + t * ROW
                pflag = m[r + 2]
                if pflag == 1:
                    prop_hist[(t, struct.unpack_from("<I", m, r + 0x26)[0])] += 1
                if n_gate and (struct.unpack_from("<H", m, r + 3)[0] & 0x20):
                    gate_rows[t] += 1
                    cost_hist[struct.unpack_from("<I", m, r + 6)[0]] += 1
    print("saves walked:", saves)
    print("propulsion rows (idx, bonus dword) -> count:")
    for (t, v), c in sorted(prop_hist.items()):
        print(f"  idx {t:2d} bonus {v:<6d} in {c} saves")
    print("gated (bit5) row idx -> saves:", sorted(gate_rows.items())[:40])
    print("cost dwords on gated rows:", sorted(cost_hist.items())[:20])
    vals = {k[1] for k in prop_hist}
    return 0 if prop_hist and max(vals) <= 64 else 1


if __name__ == "__main__":
    sys.exit(main())
