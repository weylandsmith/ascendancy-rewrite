#!/usr/bin/env python3
"""le_base_scan.py — find the constant C with VA = file_offset + C for
ascend.exe's Watcom flat image, using vtable structure rather than strings.

Context: scripts/le_contiguity_test.py proved rel32 call targets resolve
correctly in FILE space (5.17% of call targets land on a Watcom prologue vs
0.07% for page-shifted controls, 76:1), so code is stored in memory order.
String-immediate voting was inconclusive (small-constant noise), so this
script uses a stronger object: Watcom C++ emits VTABLES — runs of dwords that
are absolute addresses of virtual functions. Every entry must point at a
prologue, so the correct C makes many simultaneous constraints true at once.

Method:
  1. P = set of file offsets whose first bytes match a strict Watcom prologue.
  2. For every dword value v in the file, candidate C = v - p for each p in P
     is too wide; instead, for each dword v compute the set of C values that
     would make v land on a prologue — but only accept C if a WINDOW of k
     consecutive dwords at that location ALL land on prologues.
  3. Report the C with the most multi-entry support; require the winner to
     beat the runner-up substantially, else report INCONCLUSIVE.
"""
import os, struct, sys, collections
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(ROOT, 'game', 'ascend.exe')

STRICT = [b'\x55\x8b\xec', b'\x55\x57\x56', b'\x55\x53\x56\x57', b'\x55\x83\xec',
          b'\x55\xe8', b'\x55\x56\x57', b'\x55\x55', b'\x55\x53']


def main():
    data = open(EXE, 'rb').read()
    N = len(data)
    pro = set()
    for o in range(0x2b00, 0x85000):
        b = data[o:o + 4]
        if any(b.startswith(p) for p in STRICT):
            pro.add(o)
    print(f"strict-prologue offsets: {len(pro)}")

    # Prologue offsets are dense; index them for nearest-hit queries.
    plist = sorted(pro)
    import bisect

    def lands(off_set, C):
        """does (off_set + C) equal a prologue offset?"""
        i = bisect.bisect_left(plist, off_set + C)
        return i < len(plist) and plist[i] == off_set + C

    best = collections.Counter()
    detail = {}
    for base in range(0x2b00, N - 16, 4):
        vals = [struct.unpack_from('<I', data, base + 4 * k)[0] for k in range(6)]
        if any(v > 0x400000 for v in vals):
            continue
        for C in range(-0x100000, 0x400000, 4):
            n = sum(1 for v in vals if lands(v, C))
            if n >= 5:
                best[C] += n
                detail.setdefault(C, []).append(base)
                break
    if not best:
        print("INCONCLUSIVE: no dword window yields 5 simultaneous prologue hits")
        return 1
    top = best.most_common(6)
    print("top C candidates (support, sample vtable location):")
    for C, s in top:
        locs = detail[C][:3]
        print(f"  C={C:#09x} support={s} n_windows={len(detail[C])} at {[hex(x) for x in locs]}")
    c1, s1 = top[0]
    s2 = top[1][1] if len(top) > 1 else 0
    if s1 >= 3 * max(s2, 1):
        print(f"\nVERDICT: C = {c1:#x} (file_offset + C = VA). Load raw at base {c1:#x}.")
        return 0
    print("\nINCONCLUSIVE: winner not dominant; vtable hypothesis needs refining.")
    return 2


if __name__ == '__main__':
    sys.exit(main())
