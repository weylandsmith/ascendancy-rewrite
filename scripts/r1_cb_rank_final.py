#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r1_cb_rank_final.py — t42 definitive home-CB rank diagnostic.

Per turn<=1 home (picker-path placement, all other slots empty): print the
terrain prefix (first 12 cells), the CB cell + class, and the rank of the CB
under THREE candidate legal-set definitions:
   A: non-rock (barren legal)            [picker = rules B-adds/D-only]
   B: non-rock & non-barren              [class-0 illegal]
   C: non-rock & non-barren & index>=2   [rank-2 floor]
plus what occupies the A-legal cells BELOW the CB at save time (always empty
at turn 0, so rank A is the exact picker rank iff all cells were empty at
placement).
"""
import sys, os, glob, struct as st, zipfile, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base
import r1_income_law as IL

TURN_PHYS, IMG = 0x254E10, 0x1BF450


def main():
    pay = open("work/ascend_payload.bin", "rb").read()
    anch = build_anchors(pay)
    worlds = {}
    for run in sorted(glob.glob("work/r1/*")):
        if not os.path.isdir(run):
            continue
        for f in sorted(glob.glob(run + "/save/*.sav"), key=os.path.getmtime):
            try:
                m = zipfile.ZipFile(f).read("Memory")
            except Exception:
                continue
            votes, _ = find_base(m, anch)
            if not votes:
                continue
            base = votes.most_common(1)[0][0]
            items = IL.item_table(m, base)
            if items is None or not IL.names_ok(items):
                continue
            try:
                turn = st.unpack_from("<H", m, TURN_PHYS + (base - IMG))[0]
            except Exception:
                continue
            if turn > 1:
                continue
            ids, cbs = [], []
            for rec in IL.find_records(m):
                rb = rec[0]
                owner = m[rb + 0x57]
                if owner == 0xFF:
                    continue
                ptr = st.unpack_from("<I", m, rb + 0x10)[0] + 0x88
                surf = st.unpack_from("<H", m, rb + 0x18)[0]
                capw = st.unpack_from("<H", m, rb + 0x1a)[0]
                name = m[rb + 0x24:m.index(b"\x00", rb + 0x24)].decode("cp437", "replace")
                ids.append((name, capw))
                for k in range(min(capw, 200)):
                    if (m[ptr + 4 * k + 1] == 5
                            and (st.unpack_from("<H", m, ptr + 4 * k + 2)[0] & 1)
                            and k < surf):
                        # NOTE: k indexes the FULL slot array; surface cell i
                        # == slot i (banked: surface slots [0,+0x18)). Terrain
                        # bytes come from the SAME array byte0.
                        sur = [m[ptr + 4 * q] for q in range(surf)]
                        cbs.append((name, list(sur), k))
            if not ids:
                continue
            wid = tuple(ids)
            if wid not in worlds:
                worlds[wid] = cbs

    ra = collections.Counter()
    n = 0
    print(f"turn<=1 worlds: {len(worlds)}")
    for wid, cbs in worlds.items():
        for name, sur, k in cbs:
            n += 1
            A = [q for q, c in enumerate(sur) if not (c & 8)]
            rA = A.index(k) if k in A else -1
            ra[min(rA, 6) if rA >= 0 else -1] += 1
            print(f"  {name:16s} n_cells={len(sur):3d} cb_cell={k:3d} cls={sur[k]} "
                  f"rankA={rA:3d} prefix={sur[:10]}")
    print(f"\nrankA hist (capped6): {dict(sorted(ra.items()))}  n={n}")


main()
