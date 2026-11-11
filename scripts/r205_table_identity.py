#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t205 — adjudicate the identity of the stride-0x60 table at static 0x13bc5
(and the byte at 0x13bc4, one byte earlier).

Three banked readings conflict (docs/STATE.md t205 assignment):
  (a) t200 planets-ui.md S6   : STAR RECORDS, base 0x13bc5, u32[+0]=star type K,
                                iterated count = u16[0x16145] (~50).
  (b) t204 callers of 0x43a4c : EBX = 0x13bc5 + 0x60*RACE_IDX, called SPECIES
                                record; subtrahend key = byte[0x13bc4].
  (c) aicode §3 / income-law S6: DAT_00013bc4 == 2 as a SCALAR gov-type byte,
                                income-law S6(a) calls it "species table stride 0x60".
Race count word[0x13b98] == 4 (t204, 20/20 saves); star count ~50. One table
cannot be both.

Tests (pointer law: guest addr = B + 0x82bb0 + static offset):
  T1 VALIDITY-DEPTH: is u32 @ 0x13bc5+0x60*k a legal star type {0..12} for all
     k < star_count (per-star) or only for k < race_count (per-race)?
     Also compares base 0x13bc4 (off-by-one hypothesis).
  T2 BYTE AT 0x13bc4: constant across k and across saves (=> scalar global that
     merely abuts the table) or varying per-row (=> row field / row base).
  T3 HANDLE UNIFORMITY: dword[row+2] (the 0x43aee bitmap-base operand) — same
     value for every row? (t204 banked "same per-run handle" as inference.)
  T4 ROW SIGNATURE DEPTH: how many rows look initialised (nonzero) vs the two
     candidate bounds; report the largest k with nonzero content.
  T5 OWNER-FIELD CROSS-CHECK: dword @ 0x13bc4+0x60k+0x59 and @0x13bc5+0x60k+0x59
     (ships.md S11 +0x59 owner ptr / aicode:521 "owning STAR record law"): do
     they point INTO the same table (per-star self-refs) or into a race block?

Exit 0 = census produced; 2 = harness error.
"""
import glob
import os
import struct
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_slot as S

OFF = 0x82BB0
A4 = 0x13BC4           # the disputed byte
A5 = 0x13BC5           # the disputed table base
STRIDE = 0x60
RACE_CNT = 0x13B98     # u16
STARS_WORD = 0x16145   # u16 count read by FUN_00028fc0
STARS_T = 0x16143      # u32 >> 16 == total stars (score.md S3)
TURN = 0x12E10
MAXROW = 60
STAR_TYPES = set(range(13))


def main():
    pay = open("work/ascend_payload.bin", "rb").read()
    anch = S.anchors_cached(".", pay)
    nsaves = 0
    valid5 = [0] * MAXROW          # rows with K in {0..12} base 0x13bc5
    valid4 = [0] * MAXROW          # ditto base 0x13bc4
    nonzero = [0] * MAXROW         # rows with any nonzero byte in the 0x60 window
    byte4_per_save = {}
    rowvar_byte0 = set()           # distinct byte[0x13bc4+0x60k] over k>0
    handles = {}                   # save -> set of dword[0x13bc5+0x60k+2]
    handles4 = {}
    handle_mismatch = []           # (save, k, dword[+2]>>16) violating ==k
    detail = None
    owner_ptr_targets = {}
    owner_ptr_targets4 = {}
    counts = []
    for f in sorted(glob.glob("work/r1/playcap/save/*.sav"),
                    key=lambda p: os.path.getmtime(p)):
        mem = zipfile.ZipFile(f).read("Memory")
        B = S.base_of(mem, anch)
        if B is None:
            print(f"  {os.path.basename(f)}: no base vote", file=sys.stderr)
            continue
        P = B + OFF                  # guest addr of static offset 0
        nsaves += 1
        nr = struct.unpack_from("<H", mem, P + RACE_CNT)[0]
        nst = struct.unpack_from("<H", mem, P + STARS_WORD)[0]
        nT = struct.unpack_from("<I", mem, P + STARS_T)[0] >> 16
        turn = struct.unpack_from("<I", mem, P + TURN)[0]
        counts.append((os.path.basename(f), turn, nr, nst, nT))
        b4 = mem[P + A4]
        byte4_per_save[f"{turn}:{os.path.basename(f)}"] = b4
        hs, hs4 = set(), set()
        for k in range(MAXROW):
            p4 = P + A4 + STRIDE * k
            p5 = P + A5 + STRIDE * k
            k5 = struct.unpack_from("<I", mem, p5)[0]
            k4 = struct.unpack_from("<I", mem, p4)[0]
            if k5 in STAR_TYPES:
                valid5[k] += 1
            if k4 in STAR_TYPES:
                valid4[k] += 1
            if any(mem[p4:p4 + STRIDE]):
                nonzero[k] += 1
            if k:
                rowvar_byte0.add(mem[P + A4 + STRIDE * k])
            hs.add(struct.unpack_from("<I", mem, p5 + 2)[0])
            hs4.add(struct.unpack_from("<I", mem, p4 + 2)[0])
            if struct.unpack_from("<I", mem, p5 + 2)[0] >> 16 != k:
                handle_mismatch.append((os.path.basename(f), k,
                                        struct.unpack_from("<I", mem, p5 + 2)[0] >> 16))
            # [row+0x59]: ships.md S11 owner ptr / aicode:521 "owning STAR record".
            # Classify: row index if it lands on a row boundary of this table,
            # 'unaligned-in-table', or 'outside' (with the raw static offset).
            for src, tbl in ((p4, owner_ptr_targets4), (p5, owner_ptr_targets)):
                v = struct.unpack_from("<I", mem, src + 0x59)[0] - P
                if A4 <= v < A4 + STRIDE * MAXROW:
                    key = (v - A4) // STRIDE if (v - A4) % STRIDE == 0 else "in-table-UNALIGNED"
                else:
                    key = f"outside@{v:#x}"
                tbl[key] = tbl.get(key, 0) + 1
        handles[os.path.basename(f)] = hs
        handles4[os.path.basename(f)] = hs4
        if detail is None or turn > detail[0]:
            detail = (turn, os.path.basename(f), P, mem, nst)
    if not nsaves:
        return 2

    print(f"=== t205 table identity :: {nsaves} saves (mtime order) ===")
    print("counts (file, turn, races=u16[0x13b98], stars=u16[0x16145], T=u32[0x16143]>>16):")
    for c in counts[:4] + counts[-2:]:
        print("   ", c)

    print("\nT1 validity depth: rows k with u32 in {0..12} (of %d saves)" % nsaves)
    print("  base 0x13bc5 k: valid-count  ->", " ".join(f"{k}:{v}" for k, v in enumerate(valid5) if v))
    print("  base 0x13bc4 k: valid-count  ->", " ".join(f"{k}:{v}" for k, v in enumerate(valid4) if v))

    print("\nT2 byte[0x13bc4] per save:", sorted(set(byte4_per_save.values())),
          "(all values seen:", " ".join(f"{v}" for v in byte4_per_save.values()), ")")
    print("   byte[0x13bc4+0x60k] k>0 distinct:", sorted(rowvar_byte0))

    print("\nT3 SELF-HANDLE LAW: dword[0x13bc5+96k+2]>>16 == k (t204 inferred "
          "'same per-run handle' for every row; test it exactly):")
    print("   base 0x13bc5:", {k: len(v) for k, v in handles.items()})
    print("   base 0x13bc4:", {k: len(v) for k, v in handles4.items()})
    print("   mismatches (save, k, value):", handle_mismatch[:12],
          "" if len(handle_mismatch) <= 12 else f"... {len(handle_mismatch)} total")

    print("\nT4 initialised rows (nonzero window) ->",
          " ".join(f"{k}:{v}" for k, v in enumerate(nonzero) if v))
    last = max((k for k, v in enumerate(nonzero) if v == nsaves), default=-1)
    print(f"   deepest row nonzero in ALL saves: k={last}")

    print("\nT5 [row+0x59] dword, mod-0x60 bucket (in-table => bucket<60):")
    print("   base 0x13bc4:", dict(sorted(owner_ptr_targets4.items())[:12]))
    print("   base 0x13bc5:", dict(sorted(owner_ptr_targets.items())[:12]))

    if detail:
        turn, name, P, mem, nst = detail
        print(f"\nDETAIL latest save {name} turn={turn} stars={nst}")
        print("  static bytes 0x13b90..0x13c00 (payload/initialised data):")
        print("   ", pay[0x13b90:0x13c00].hex())
        print("   same in save:")
        print("   ", mem[P + 0x13b90:P + 0x13c00].hex())
        print("  rows k=0..7 [u32@0x13bc5+96k | byte@0x13bc4+96k | +0x16 +0x17 | +0x1c word]:")
        for k in range(8):
            p5 = P + A5 + STRIDE * k
            p4 = P + A4 + STRIDE * k
            print(f"    k={k:2d} {struct.unpack_from('<I', mem, p5)[0]:10d}"
                  f" {mem[p4]:3d} {mem[p4+0x16]:3d},{mem[p4+0x17]:3d}"
                  f" {struct.unpack_from('<H', mem, p4+0x1c)[0]:6d}"
                  f" owner@+0x59={struct.unpack_from('<I', mem, p4+0x59)[0]-P:#x}")
    return 0


def dword_targets(_v):
    return ()


if __name__ == "__main__":
    sys.exit(main())
