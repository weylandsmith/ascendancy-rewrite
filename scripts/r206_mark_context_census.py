#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t206 — verify the operand identities the mark-consumer law rests on.

Checks over the 20 playcap saves (pointer law: member = B + 0x82bb0 + X):
  C1 dword[0x12e10+2]>>16 == 0  — so 0x24dd0's handle-index==0 branch
     (HOME-star bit0 re-arm) is TRUE for the diplo-table arg the callers
     actually pass (mov eax,0x12e10 at 0x55ecb/0x55f93). If this fails the
     S5(2) reading is wrong.
  C2 u16[0x12e10+0x3335] — the clear-loop bound N of 0x24e31..0x24e48.
     Compare against the lane count (u16[0x16147-2]? per t190 the lane pool
     count context) and star count u16[0x16145]==50: candidate readings are
     lane-count (58) or something else. Report value, do not force.
  C3 honest-negative re-check under the array reading: window
     [0x48304,0x48304+0x40) all-zero per save (victim bits AND bit0).
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
DIPLO = 0x12E10
STARS_WORD = 0x16145
MARK = 0x48304


def main():
    pay = open("work/ascend_payload.bin", "rb").read()
    anch = S.anchors_cached(".", pay)
    n = 0
    c1 = 0
    c2vals = {}
    c3zero = 0
    for f in sorted(glob.glob("work/r1/playcap/save/*.sav")):
        try:
            mem = zipfile.ZipFile(f).read("Memory")
        except Exception:
            continue
        B = S.base_of(mem, anch)
        if B is None:
            continue
        n += 1

        def u32(X):
            return struct.unpack_from("<I", mem, B + OFF + X)[0]

        def u16(X):
            return struct.unpack_from("<H", mem, B + OFF + X)[0]

        if (u32(DIPLO + 2) >> 16) == 0:
            c1 += 1
        v = u16(DIPLO + 0x3335)
        c2vals[v] = c2vals.get(v, 0) + 1
        win = mem[B + OFF + MARK: B + OFF + MARK + 0x40]
        if not any(win):
            c3zero += 1
        if n == 1:
            print("first save:", os.path.basename(f),
                  "stars@16145 =", u16(STARS_WORD),
                  "diplo[+2]>>16 =", u32(DIPLO + 2) >> 16,
                  "diplo[+0x3335] =", v,
                  "star0[+0x3335] =", u16(0x13BC5 + 0x3335))
    print(f"saves={n}")
    print(f"C1 diplo-table handle-index==0: {c1}/{n}")
    print("C2 u16[0x12e10+0x3335] values:", c2vals,
          "(lane count per t190 == 58; star count 50)")
    print(f"C3 mark window 0x48304..+0x3f all-zero: {c3zero}/{n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
