"""tPF6-B: census imm32 occurrences of a value in the obj0 code range.

Usage: ~/tools/revenv/bin/python scripts/tPF6b_imm32.py VALUE_HEX [VALUE_HEX ...]
Prints each address where the little-endian imm32 appears (code range only),
plus the enclosing function from work/functions_full.tsv.
"""
import sys, bisect, struct

data = open('work/ascend_restored.bin', 'rb').read()
LO, HI = 0x14bb0, 0x82bb0
funcs = sorted((int(a, 16), int(b, 16))
               for a, b in (l.split() for l in open('work/functions_full.tsv').read().splitlines()[1:]))
starts = [f[0] for f in funcs]

def enclosing(a):
    i = bisect.bisect_right(starts, a) - 1
    if i < 0:
        return '?'
    st, sz = funcs[i]
    return f"{st:x}" if a < st + sz else f"~{st:x}"

for v in sys.argv[1:]:
    val = int(v, 16)
    pat = struct.pack('<I', val)
    hits = []
    i = LO
    while True:
        j = data.find(pat, i, HI)
        if j < 0:
            break
        hits.append(j)
        i = j + 1
    print(f"imm32 {val:x}: {len(hits)} sites")
    for a in hits:
        print(f"  {a:x}  fn {enclosing(a)}")
