#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t337: STATE-TABLE (winmgr+0x3066/0x3068/0x306a+0x8e*id, winmgr+0x4226)
READER INVENTORY.

Method (zero capture, static): work/r331_disasm.txt objdump -D -M intel,
imagebase 0 => addresses are payload-file offsets.

1. Function-boundary map: every `call <abs>` target is a function start; sorted
   starts give extents (approximate, verified by dumping prologues).
2. Site census: every insn mentioning displacements 0x3066/0x3068/0x306a/0x4226
   AND every `imul *,0x8e` (the STATE-record stride multiply).
3. Per-site: read vs store classification, enclosing function, callers of that
   function.

Usage: python3 scripts/r337_state_readers.py [--dump fn_hex ...]
"""
import argparse, bisect, collections, re

pat = re.compile(r'^\s*([0-9a-f]+):\t([0-9a-f][0-9a-f ]*?)\t+(.*)$')
call_re = re.compile(r'^call\s+(?:0x)?([0-9a-f]{4,6})\b')
DISP = re.compile(r'\+0x(3066|3068|306a|4226)\b')
MEM = r'\[([a-z]+)(?:\+0x([0-9a-f]+)|-0x([0-9a-f]+))?\]'
def is_store(t):
    if t.startswith(('fsts', 'fstp')):
        return True
    if t.startswith(('inc ', 'dec ', 'neg ', 'negl')):
        return '[' in t
    if t.startswith('mov'):
        # store iff a memory operand appears BEFORE the first comma
        comma = t.find(',')
        lb = t.find('[')
        return lb != -1 and (comma == -1 or lb < comma)
    return False

def load(path):
    ins = []
    with open(path) as f:
        for s in f:
            m = pat.match(s)
            if m:
                ins.append((int(m.group(1), 16), m.group(3).rstrip()))
    return ins

def bounds(ins):
    starts = set()
    for a, t in ins:
        m = call_re.match(t)
        if m:
            starts.add(int(m.group(1), 16))
    starts |= {ins[0][0]}
    starts = sorted(s for s in starts if s >= ins[0][0])
    return starts

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--path', default='work/r331_disasm.txt')
    ap.add_argument('--dump', default='')
    a = ap.parse_args()
    ins = load(a.path)
    addr2i = {x[0]: i for i, x in enumerate(ins)}
    addrs = [x[0] for x in ins]
    starts = bounds(ins)
    soffs = starts
    def fnof(x):
        i = bisect.bisect_right(soffs, x) - 1
        return soffs[i] if i >= 0 else None
    callers = collections.defaultdict(set)
    for ad, t in ins:
        m = call_re.match(t)
        if m:
            callers[int(m.group(1), 16)].add(ad)

    if a.dump:
        for h in a.dump.split(','):
            s = int(h, 16)
            e = fnof(s + 1) or s + 0x200
            i0 = addr2i[s]
            print(f"\n===== fn {hex(s)} .. {hex(e)} ({'next-call-start' }) callers: "
                  + " ".join(hex(c) for c in sorted(callers.get(s, []))[:40]))
            for i in range(i0, len(ins)):
                ad, t = ins[i]
                if ad >= e: break
                print(f"  {ad:#x}\t{t}")
        return

    # --- site census
    by_fn = collections.defaultdict(list)
    for ad, t in ins:
        m = DISP.search(t)
        stride = 'imul' in t and '0x8e' in t
        if not (m or stride):
            continue
        kind = 'STORE' if any(rx.match(t) for rx in store_res) else ('STRIDE' if stride else 'READ?')
        if m and m.group(1) in ('3066', '3068', '306a', '4226') and not stride:
            # distinguish read vs store already; mark stride-multiplies separately
            kind = 'STORE' if any(rx.match(t) for rx in store_res) else 'READ'
        by_fn[fnof(ad)].append((ad, kind, m.group(1) if m else '8e', t))

    print(f"# functions with STATE-disp/stride sites: {len(by_fn)}")
    for f in sorted(by_fn):
        v = by_fn[f]
        reads = [x for x in v if x[1] == 'READ']
        stores = [x for x in v if x[1] == 'STORE']
        strides = [x for x in v if x[1] == 'STRIDE']
        cl = sorted(callers.get(f, set()))
        print(f"\nfn {f:#x}  n={len(v)} reads={len(reads)} stores={len(stores)} stride0x8e={len(strides)}"
              f"  callers({len(cl)}): " + " ".join(hex(c) for c in cl[:30]))
        for ad, kind, d, t in v:
            print(f"   {ad:#x} {kind:6s} +0x{d}\t{t}")

if __name__ == '__main__':
    main()
