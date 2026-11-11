#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r1_ability_charge.py — OQ-020 census: slot word+2 upper byte values.

Law context (income-law.md S10 + T57): completion walk FUN_00038f68 calls
FUN_00039b6c for every ACTIVE slot whose item FLAG&4 (special ability); on
non-zero supply it writes byte3 := 0 and word+2 |= supply << 8. FUN_00039b6c
constants (decompile verbatim): item 28 -> (45, 7, 3); item 29 -> (90, 8, 3);
item 30 -> (90, 8, 3); item 17 -> (200, 0, 2); others 0.
This census reports word+2>>8 (and word+2&0xFF, byte3) for flag&4 items
across every readable save, plus consecutive-pair DECREMENTS (the period
parameter's behavioural signature).
Usage: r1_ability_charge.py [run_dirs...]   (default: all work/r1/*)
"""
import os, sys, zipfile, collections, struct as st

R = "/home/hrethric/projects/ascendancy"
sys.path.insert(0, R + "/scripts")
import r1_income_law as IL

FLAG4 = (17, 28, 29, 30)  # runtime-verified flags&4 among measured items

def slot_view(run_dir):
    slots = IL.load_slots(run_dir)
    out = []
    for name, m, P0 in slots:
        tab = IL.item_table(m, P0)
        if tab is None or not IL.names_ok(tab):
            continue
        v = {}
        for rec in IL.find_records(m):
            rb = rec[0]
            if m[rb + 0x57] == 0xFF:
                continue
            arr = st.unpack_from("<I", m, rb + 0x10)[0] + 0x88
            cells = st.unpack_from("<H", m, rb + 0x18)[0]
            for k in range(cells + 10):
                it = m[arr + 4 * k + 1]
                if it not in FLAG4:
                    continue
                w2 = st.unpack_from("<H", m, arr + 4 * k + 2)[0]
                v[IL.planet_name(m, 0, 0) if False else (rb, k)] = (
                    it, w2, m[arr + 4 * k + 3], w2 & 1)
        out.append((name, v))
    return out

def main():
    dirs = sys.argv[1:]
    if not dirs:
        dirs = [os.path.join(R, "work/r1", d) for d in sorted(os.listdir(R + "/work/r1"))]
    hist = collections.Counter()
    dec = collections.Counter()
    n = 0
    for d in dirs:
        if not os.path.isdir(d):
            continue
        try:
            seq = slot_view(d)
        except Exception:
            continue
        prev = None
        for name, v in seq:
            for key, (it, w2, b3, active) in v.items():
                hist[(it, w2 >> 8)] += 1
                n += 1
            if prev is not None:
                for key in set(prev) & set(v):
                    a = prev[key][1] >> 8
                    b = v[key][1] >> 8
                    if b < a:
                        dec[(prev[key][0], a - b)] += 1
            prev = v
    print("observations", n)
    print("upper-byte hist:", dict(sorted(hist.items())))
    print("decrement hist (item, delta):", dict(sorted(dec.items())))

if __name__ == "__main__":
    main()
