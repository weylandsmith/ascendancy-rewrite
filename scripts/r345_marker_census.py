#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t345: SLOT word2 HIGH BYTE (byte3) CENSUS — is it a constant marker or a live
ship-table index? (OQ-016 residue-(4) follow-through; ZERO CAPTURE, offline.)

WHY. t340 (docs/re/income-law.md S-T340) closed the shield-byte question with
byte3 = "ONE-TIME completion marker" (0x0f, or 0x23 for item 27). This session
found the CONSUMER of that byte: FUN_000396cc (work/t91_code_disasm.txt verbatim)

    mov  ax, WORD PTR [esi+eax*4+0x2]   ; slot word2
    sar  eax, 0x8                        ; byte3
    and  eax, 0x7f                       ; bound
    cmp  eax, 0x6b                       ; assert < 107
    imul eax, eax, 0x162                 ; stride 354
    mov  eax, DWORD PTR [eax+0x3a0e9]    ; rec+0x54 (owner dword)
    ...
    add  eax, 0x3a095 - 0x3a0e9 (tail 0x39754: imul; add eax,0x3a095)

i.e. byte3 is consumed as an INDEX INTO THE 354-BYTE-STRIDE SHIP ARRAY at
0x3a095 (the same table docs/re/aicode.md S2b + docs/re/dosbox-wp-t283 bank).
EVERY one of the 25 call sites of 0x396cc gates on slot byte1 == 0x17 (item 23 =
Ship). The STAMP writer is FUN_00039760 (0x39797..0x39806: index =
(ship_ptr - 0x3a095)/0x162, asserted < 0x6b, then `word2 |= idx<<8`), and the
CLEAR is FUN_00039894 (0x398e6/0x398ee: byte1 := 0xff, word2 := 0 when the slot's
ship matches a given ship record).

So the two readings are distinguishable by measurement:
  H_MARKED  item-23 slots carry a CONSTANT byte3 (t340 reading is complete)
  H_INDEX   item-23 slots carry VARIABLE byte3 in 0..106 (ship index) while
            orbital shield items 26/27 carry the constants 15/35 (union field).

LAWS IN USE (all banked): record walk IL.find_records (t33/OQ-014); slot array
pointer [rec+0x10] is GUEST-PHYSICAL, member starts at +0x88 (t33 correction);
slot dword = byte0 flags / byte1 item id / word2 @+0x2 (t340 verbatim stores);
owner byte rb+0x57 (t248); cells rb+0x18, cap rb+0x1a (t33 cap law cap=cells+10).

Exit: 0 = census ran (prints the verdict line); 2 = harness broken.
"""
import collections
import glob
import os
import struct as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_income_law as IL
from r1_sav_scan import build_anchors

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TURN_PHYS, IMAGE_MAP_BASE = 0x254E10, 0x1BF450
SHIP_ITEM, SHIELD_SURF, SHIELD_ORB, MEGA_ORB = 23, 18, 26, 27
BOUND = 0x6b  # 107, asserted at 0x39709 / 0x397b2


def turn_of(m, base):
    off = TURN_PHYS + (base - IMAGE_MAP_BASE)
    if 0 <= off and off + 2 <= len(m):
        t = st.unpack_from("<H", m, off)[0]
        if t < 20000:
            return t
    return None


def slots_of(m, rb):
    """(cell, byte1_item, word2) for every slot row of a planet record."""
    ptr = st.unpack_from("<I", m, rb + 0x10)[0]
    cap = st.unpack_from("<H", m, rb + 0x1a)[0]
    cells = st.unpack_from("<H", m, rb + 0x18)[0]
    arr = ptr + 0x88
    if not (0 <= arr and arr + cap * 4 <= len(m)) or cap == 0 or cap > 200:
        return None, None, []
    out = []
    for i in range(cap):
        b1 = m[arr + i * 4 + 1]
        w2 = st.unpack_from("<H", m, arr + i * 4 + 2)[0]
        out.append((i, b1, w2))
    return cells, cap, out


def main():
    try:
        pay = open(IL.PAY, "rb").read()
        build_anchors(pay)
    except Exception as e:                                   # harness broken
        print("ANCHORS FAIL:", e)
        return 2

    if "--all" in sys.argv:
        dirs = sorted(set(glob.glob(os.path.join(ROOT, "work/r1/*/"))))
    else:
        # Default = the t342 assignment corpus (fast); --all for the full sweep.
        dirs = [os.path.join(ROOT, x) for x in (
            "work/r1/playcap", "work/r1/playcap/caps", "work/r1/bank-t1254",
            "work/r1/t340-shieldc-20261108-014705")]
    n_saves_ok = 0
    n_dirs = 0
    pair_hist = collections.Counter()          # (item, byte3) over ALL slot rows
    item23_vals = collections.Counter()        # byte3 values for item-23 rows
    item23_active = collections.Counter()
    distinct_per_planet = []                   # planets with >1 distinct byte3
    examples = []

    for d in dirs:
        try:
            slots = IL.load_slots(d)
        except Exception:
            continue
        if not slots:
            continue
        n_dirs += 1
        for f, m, B in slots:
            recs = list(IL.find_records(m))
            if not recs:
                continue
            n_saves_ok += 1
            for rb, cells, cap, arr in recs:
                if not (0 <= arr and arr + cap * 4 <= len(m)) or cap == 0 or cap > 200:
                    continue
                owner = m[rb + 0x57]
                n23 = set()
                for cell in range(cap):
                    b1 = m[arr + cell * 4 + 1]
                    w2 = st.unpack_from("<H", m, arr + cell * 4 + 2)[0]
                    b3 = (w2 >> 8) & 0xFF
                    pair_hist[(b1, b3)] += 1
                    if b1 == SHIP_ITEM:
                        item23_vals[b3] += 1
                        if w2 & 1:
                            item23_active[b3] += 1
                        n23.add(b3)
                        if len(examples) < 25:
                            examples.append((os.path.basename(f), hex(rb), owner,
                                             cells, cap, cell, hex(w2), b3))
                if len(n23) > 1:
                    distinct_per_planet.append((os.path.basename(f), hex(rb),
                                                owner, sorted(n23)[:12]))

    print(f"run dirs with slots: {n_dirs}; saves with >=1 record: {n_saves_ok}")
    print("\n=== ITEM-23 (Ship) slot rows: byte3 histogram (ALL rows) ===")
    for v, c in sorted(item23_vals.items()):
        print(f"  byte3={v:3d} ({v:#04x}) count={c}")
    print(f"  distinct byte3 values on item-23 rows: {len(item23_vals)}")
    print("\n=== ITEM-23 ACTIVE rows (word2 bit0): byte3 histogram ===")
    for v, c in sorted(item23_active.items())[:40]:
        print(f"  byte3={v:3d} count={c}")
    print("\n=== shield/orbital rows for contrast ===")
    for it in (SHIELD_SURF, SHIELD_ORB, MEGA_ORB):
        vs = {k[1]: c for k, c in pair_hist.items() if k[0] == it}
        tot = sum(vs.values())
        top = sorted(vs.items(), key=lambda kv: -kv[1])[:6]
        print(f"  item {it}: {tot} rows, distinct byte3 {len(vs)}, top {top}")
    print("\n=== planets with >1 distinct item-23 byte3 ===")
    print(f"  count: {len(distinct_per_planet)}")
    for e in distinct_per_planet[:12]:
        print("   ", e)
    print("\n=== item-23 examples (file, rec, owner, cells, cap, cell, word2, b3) ===")
    for e in examples[:25]:
        print("   ", e)

    n23_total = sum(item23_vals.values())
    if n23_total == 0:
        print("\nVERDICT: NO ITEM-23 SLOT ROWS IN CORPUS - hypothesis "
              "undecidable offline.")
    elif len(item23_vals) == 1:
        print(f"\nVERDICT: H_MARKED - item-23 byte3 CONSTANT "
              f"{next(iter(item23_vals))} over {n23_total} rows.")
    else:
        inb = sum(c for v, c in item23_vals.items() if v < BOUND)
        print(f"\nVERDICT: H_INDEX - item-23 byte3 takes {len(item23_vals)} "
              f"distinct values over {n23_total} rows ({inb} within the "
              f"asserted 0..106 bound).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
