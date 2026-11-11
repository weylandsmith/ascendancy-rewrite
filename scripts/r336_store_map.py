#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t336 S1: enumerate EVERY store instruction in fn 0x575e4 (windows.txt parser)
with its target displacement, grouped by displacement.

Input: work/r331_disasm.txt (objdump -D -M intel of the restored payload image,
imagebase 0 => addresses ARE payload-file offsets per the pointer-law family).

Usage: python3 scripts/r336_store_map.py [--start 0x575e4] [--end 0x59900]
"""
import argparse, collections, re

pat = re.compile(r'^\s*([0-9a-f]+):\t([0-9a-f][0-9a-f ]*?)\t+(.*)$')

SIZES = r'(?:BYTE|WORD|DWORD|FWORD|QWORD|TBYTE|XMMWORD)?(?:\s+PTR)?'
MEM = r'\[([a-z]+)(?:\+0x([0-9a-f]+)|-0x([0-9a-f]+))?\]'
store_res = [
    re.compile('^mov\\s+' + SIZES + '\\s*' + MEM + '\\s*,'),
    re.compile('^(?:fsts|fstp)\\s+' + SIZES + '\\s*' + MEM),
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--start', default='0x575e4')
    ap.add_argument('--end', default='0x59900')
    ap.add_argument('--path', default='work/r331_disasm.txt')
    ap.add_argument('--sites', type=int, default=12)
    a = ap.parse_args()
    lo, hi = int(a.start, 16), int(a.end, 16)

    ins = []
    with open(a.path) as f:
        for s in f:
            m = pat.match(s)
            if m:
                addr = int(m.group(1), 16)
                if lo <= addr < hi:
                    ins.append((addr, m.group(3).rstrip()))
    print(f"# insns in [{hex(lo)},{hex(hi)}): {len(ins)}  first={hex(ins[0][0])} last={hex(ins[-1][0])}")

    grp = collections.defaultdict(list)
    other_store = collections.Counter()
    for addr, i in ins:
        hit = None
        for rx in store_res:
            m = rx.match(i)
            if m:
                base = m.group(1)
                disp = int(m.group(2), 16) if m.group(2) else (-int(m.group(3), 16) if m.group(3) else 0)
                hit = (base, disp)
                break
        if hit:
            grp[hit].append((addr, i))
        elif i.startswith('push'):
            grp[('stk', 0)].append((addr, i))
        elif i.startswith(('rep movs', 'stos', 'xchg', 'fild')):
            other_store[i.split()[0]] += 1

    print("\n# === stores by (base, disp) ===")
    win = [(k, v) for k, v in grp.items() if k[0] not in ('esp', 'ebp', 'stk')]
    loc = [(k, v) for k, v in grp.items() if k[0] in ('esp', 'ebp')]
    stk = grp.get(('stk', 0), [])
    print("## window/heap-record stores (non-stack bases)")
    for (base, disp), v in sorted(win, key=lambda kv: (kv[0][1], kv[0][0])):
        print(f"  {base}+0x{disp:x}  n={len(v)}  sites: " + " ".join(hex(x[0]) for x in v[:a.sites]))
    print("## stack-local stores (esp/ebp) by displacement")
    for (base, disp), v in sorted(loc, key=lambda kv: (kv[0][1], kv[0][0])):
        print(f"  {base}+0x{disp:x}  n={len(v)}")
    print(f"## pushes: {len(stk)}   other store-ish: {dict(other_store)}")

if __name__ == '__main__':
    main()
