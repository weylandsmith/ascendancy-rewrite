#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r324_census.py — BatModeWnd RAM class-table census (t324).

Reads the BatModeWnd class table from LIVE RAM via a production save's
`Memory` ZIP member (pointer law: full guest-RAM image) — zero guest boot,
zero scratch copy, production session untouched. See docs/re/_wip_t324.md.

Anchoring (measured, S1-S2 of the WIP doc):
  * [wmgr+0x3337] stride 0x27 is the LANE POOL (data payload 0x16147), NOT a
    window-name registry — do not use it to find BatModeWnd.
  * The BatModeWnd class table's SOLE installer is fn 0x1ac21:
    `mov [rec+0xa7], 0x58e8` (image census of all [+0xa7] stores: 0x58e8
    occurs ONLY there). 0x58e8 is a DATA payload offset, not rebased.
  * Table slot k in RAM = P0 + <static fn offset>. Cited BATMODE table
    (t296/t323): [0x1abfc, 0x30d08, 0x1aef8, 0x1d858, 0x311b8, 0x1e9dc].

Verdict logic:
  EXACT match of all 6 slots (slot - P0 == cited) AND no flagged
  [win+0xb1] writer in the table  => NEGATIVE ABSOLUTE (t323 stands).
  Any slot diff or a flagged writer present => t323 REOPENS.

Model validation is built in: the Icarus star-record pointer 0x256825 (a
stored guest-physical u32) must read b"Icarus" at +0x1c before the table
result is trusted.
"""
import os, sys, glob, struct, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_slot as SL

ROOT = "/home/hrethric/projects/ascendancy"
H = 0x88
OFF = 0x82bb0
TABLE_DATA_OFF = 0x58e8          # fn 0x1ac21: mov [rec+0xa7], 0x58e8
CITED = [0x1abfc, 0x30d08, 0x1aef8, 0x1d858, 0x311b8, 0x1e9dc]
WRITERS = {0x32100, 0x31f30, 0x339a4}
STAR_PTR = 0x256825              # Icarus star record (t307 S5)


def census(save_path, pay, anch):
    mem = zipfile.ZipFile(save_path).read("Memory")
    B = SL.base_of(mem, anch)
    if B is None:
        return None
    P0 = B - H
    # model validation: Icarus star record name at +0x1c
    i = STAR_PTR + H
    name = mem[i + 0x1c:i + 0x1c + 8].split(b"\x00")[0]
    # table at data payload offset TABLE_DATA_OFF -> member idx B+OFF+X
    t = struct.unpack_from("<6I", mem, B + OFF + TABLE_DATA_OFF)
    codeoffs = [x - P0 for x in t]
    exact = all(codeoffs[k] == CITED[k] for k in range(6))
    writers = [hex(c) for c in codeoffs if c in WRITERS]
    incode = sum(1 for c in codeoffs if 0 <= c < len(pay))
    return dict(B=B, P0=P0, name=name, slots=t, codeoffs=codeoffs,
                exact=exact, writers=writers, incode=incode)


def main():
    pay = SL.load_payload(ROOT)
    anch = SL.anchors_cached(ROOT, pay)
    saves = sorted(glob.glob(os.path.join(ROOT, "work/r1/playcap/save/5*.sav")),
                   key=os.path.getmtime)
    if not saves:
        print("no saves under work/r1/playcap/save/5*.sav"); return 2
    rows = []
    for s in saves:
        r = census(s, pay, anch)
        if r is None:
            rows.append((s, None)); continue
        ok = (r["name"] == b"Icarus") and (r["incode"] == 6)
        print("%s B=0x%x P0=0x%x model(Icarus,6/6)=%s EXACT=%s writers=%s" % (
            os.path.basename(s), r["B"], r["P0"], ok, r["exact"], r["writers"]))
        rows.append((s, r))
    got = [r for _, r in rows if r]
    if not got or not all(r["name"] == b"Icarus" and r["incode"] == 6 for r in got):
        print("MODEL VALIDATION FAILED — table result NOT trusted"); return 2
    if all(r["exact"] and not r["writers"] for r in got):
        print("\nVERDICT: NEGATIVE ABSOLUTE — live RAM table == cited BATMODE "
              "table (6/6, P0-rebased), fn 0x32100 absent in all %d saves. "
              "t323 caveat (b) discharged; every OQ-019 capture route "
              "cited-dead. Row stays open per strict-close (no positive "
              "SELECT witness ever)." % len(got))
        return 0
    print("\nVERDICT: MISMATCH — t323 REOPENS. Offending slots:")
    for r in got:
        if not r["exact"] or r["writers"]:
            for k in range(6):
                c, q = r["codeoffs"][k], CITED[k]
                if c != q:
                    w = " <== FLAGGED WRITER" if c in WRITERS else ""
                    print("  slot%d: ram 0x%x != cited 0x%x%s" % (k, c, q, w))
    return 1


if __name__ == "__main__":
    sys.exit(main())
