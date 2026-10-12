#!/usr/bin/env python3
"""r1_t81_mpop.py — verify the banked +0x4a recalc equation's SEED term is
the word +0x55 (income-law.md L609-620 claims `MOV AX,[EBX+0x55]` @0x38bd4
and +0x4a == clamp(0,100, +0x55 + sum MPOP(active items, skip flags bit2)).

Positive-control style: recompute for every owned record in one slot and
compare against the STORED +0x4a word.
"""
import os, struct as st, sys, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base
from r1_income_law import find_records, item_table, names_ok

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLOT = os.path.join(ROOT, "work", "r1", "r1deep-20261005-230146", "save", "60.sav")


def main():
    pay = open(os.path.join(ROOT, "work", "ascend_payload.bin"), "rb").read()
    anch = build_anchors(pay)
    m = zipfile.ZipFile(SLOT).read("Memory")
    v, _ = find_base(m, anch)
    B = v.most_common(1)[0][0]
    items = item_table(m, B)
    if items is None or not names_ok(items):
        print("item table cross-check FAILED")
        return 2
    agree = 0
    tot = 0
    for r in find_records(m):
        base = r[0]
        if m[base + 0x57] == 0xFF:
            continue
        seed = st.unpack_from("<H", m, base + 0x55)[0]
        arr = st.unpack_from("<I", m, base + 0x10)[0]
        cap = m[base + 0x1a]
        ssum = 0
        if 0 < arr < len(m) - cap * 4:
            for i in range(cap):
                it = m[arr + i * 4 + 1]
                fl = st.unpack_from("<H", m, arr + i * 4 + 2)[0]
                if it == 0xFF or (fl & 1) == 0:
                    continue
                if items[it]["flags"] & 4:
                    continue
                ssum += items[it]["mpop"]
        pred = min(100, max(0, seed + ssum))
        stored = st.unpack_from("<H", m, base + 0x4a)[0]
        tot += 1
        agree += pred == stored
        if pred != stored and tot <= 8:
            nm = m[base + 0x24:base + 0x44].split(b"\x00")[0].decode(errors="replace")
            print(f"  {nm:16s} seed={seed} ssum={ssum} pred={pred} stored={stored}")
    print(f"equation +0x4a == clamp(seed +0x55 + MPOP): {agree}/{tot}")
    return 0 if agree == tot else 1


if __name__ == "__main__":
    sys.exit(main())
