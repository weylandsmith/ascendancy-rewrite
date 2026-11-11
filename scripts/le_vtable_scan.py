#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""le_vtable_scan.py — find the constant C (VA = file_offset + C) for the
Watcom flat image of ascend.exe, using call-graph function starts and
pointer-table (vtable-shaped) windows.

Facts this builds on (both measured, see scripts/le_contiguity_test.py):
 * rel32 call targets resolve correctly in FILE space at 76:1 over a
   page-shifted control => code bytes sit in memory order.
 * No single-constant base was provable from string immediates alone.

Method:
 1. P = set of rel32 call-target file offsets -> trustworthy function starts.
 2. W = aligned runs of >=6 dwords with 0 < v < 0x400_000 (pointer-table shape).
 3. For window w with values v0..v5: any C making it a pointer table must map
    v0 and v1 both onto P, so C = p - v0 with p, p+(v1-v0) both in P. The
    delta constraint kills almost all noise; survivors are then required to
    map v2..v5 onto P as well (allowing 1 miss: thunks/externals).
 4. Vote C over all windows. Report the winner only if it dominates.

Exit 0 with the base printed on a decisive winner; 1 otherwise.
"""
import os, struct, sys, collections
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(ROOT, 'game', 'ascend.exe')
PAY, CODE_LO, CODE_HI = 0x2a50, 0x2b00, 0x85000


def function_starts(data):
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    P = set()
    for probe in range(CODE_LO, CODE_HI, 0x400):
        end = min(probe + 0x400, CODE_HI)
        for ins in md.disasm(data[probe:end], probe):
            if ins.mnemonic in ('call', 'jmp') and ins.op_str.startswith('0x'):
                t = int(ins.op_str, 16)
                if CODE_LO <= t < CODE_HI:
                    P.add(t)
    return P


def pointer_windows(data, lo, hi, need=6):
    out = []
    o = lo
    run = []
    while o + 4 <= hi:
        v = struct.unpack_from('<I', data, o)[0]
        if 0 < v < 0x400000:
            if not run:
                run = [o, o + 4, v]  # base, next, list handled below
                vals = [v]
            else:
                vals.append(v)
                run[1] = o + 4
        else:
            if len(vals) >= need:
                out.append((run[0], tuple(vals)))
            vals = []
            run = []
        o += 4
    if vals and len(vals) >= need:
        out.append((run[0], tuple(vals)))
    return out


def main():
    data = open(EXE, 'rb').read()
    N = len(data)
    P = function_starts(data)
    print(f"call-graph function starts: {len(P)}")
    Pset = P
    windows = pointer_windows(data, PAY, N)
    print(f"pointer-shaped windows (>=6 dwords < 0x400000): {len(windows)}")
    if not windows:
        print("no windows")
        return 1

    delta_cache = {}
    votes = collections.Counter()
    support = collections.defaultdict(list)
    for base, vals in windows:
        v0, v1 = vals[0], vals[1]
        d = v1 - v0
        if abs(d) > 0x300000:
            continue
        if d not in delta_cache:
            delta_cache[d] = [p for p in Pset if (p + d) in Pset]
        cands = [p - v0 for p in delta_cache[d]]
        if not cands:
            continue
        for C in cands:
            hits = 0
            for v in vals[:6]:
                if (v + C) in Pset:
                    hits += 1
            if hits >= 5:
                votes[C] += 1
                support[C].append((base, hits))
    if not votes:
        print("INCONCLUSIVE: no C produces a 5/6-pointer window anywhere.")
        return 1
    top = votes.most_common(8)
    print("\ntop C (distinct windows supported):")
    for C, k in top:
        ex = support[C][0]
        print(f"  C={C:#09x} windows={k} example window@{ex[0]:#x} hits={ex[1]}")
    c1, s1 = top[0]
    s2 = top[1][1] if len(top) > 1 else 0
    if s1 >= 2 * max(s2, 1) and s1 >= 5:
        print(f"\nVERDICT: C = {C:#x}".replace('{C:#x}', f'{c1:#x}'))
        print(f"Load the raw payload (game/ascend.exe + {PAY:#x} .. EOF) at base "
              f"{c1 - PAY:#x} relative to payload start, or the whole file at {c1:#x} - {N:#x} "
              f"(VA = fileoff + {c1:#x}).")
        return 0
    print("\nINCONCLUSIVE: winner does not dominate.")
    return 2


if __name__ == '__main__':
    sys.exit(main())
