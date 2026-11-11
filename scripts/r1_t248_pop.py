#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t248 S5: header counts 60 @t1086 while count(owner==race)=80; at t1254 both
are 102. Hypothesis: the header counts OCCUPIED (=populated) planets. Sweep
u32-width predicates and per-record nonzero-byte-count forms, scored 60@t1086
then re-scored 102@t1254."""
import struct, sys, zipfile, glob, os, re, collections
sys.path.insert(0, "scripts")
import r1_slot as S
OFF = 0x82bb0; STRIDE = 123; NAMEW = 19
NAME_RE = rb"[A-Z][A-Za-z]{2,}(?: [IVX]+)?\x00"
pay = S.load_payload("."); anch = S.anchors_cached(".", pay)

def load(path):
    mem = zipfile.ZipFile(path).read("Memory")
    B = S.base_of(mem, anch)
    hits = set(m.start() for m in re.finditer(NAME_RE, mem))
    cands = [h for h in hits if all(h + i*STRIDE in hits for i in range(15))]
    def runlen(c):
        n = 0; p = c
        while p in hits: n += 1; p += STRIDE
        return n
    c = max(cands, key=runlen); base = c
    while base - STRIDE in hits: base -= STRIDE
    race = mem[B + OFF + 0x7458e]
    rows = []
    for k in range(151):
        j = base + k*STRIDE
        raw = mem[j:j+NAMEW]
        if raw.strip(b"\x00") == b"": continue
        if mem[j+0x33] != race: continue
        rows.append(mem[j:j+STRIDE])
    return rows

slots = [s for s in sorted(glob.glob("work/r1/playcap/save/*.sav"), key=os.path.getmtime)
         if os.path.getsize(s) > 200000]
A = load(slots[-1])          # t1086, target 60
C = load("work/r1/bank-t1254/48.sav")   # t1254, target 102
print(f"owned rows: A(t1086)={len(A)} C(t1254)={len(C)}")

hits = []
for d in range(STRIDE-3):
    a = sum(1 for r in A if struct.unpack_from("<I", r, d)[0] != 0)
    if a == 60:
        c = sum(1 for r in C if struct.unpack_from("<I", r, d)[0] != 0)
        hits.append(("u32!=0", d, c))
for d in range(STRIDE-3):
    for v in (0xFFFFFFFF,):
        a = sum(1 for r in A if struct.unpack_from("<I", r, d)[0] == v)
        if a == 60:
            hits.append(("u32==FF", d, sum(1 for r in C if struct.unpack_from("<I", r, d)[0] == v)))
print("u32 hits at 60:", hits, "-> MATCH-BOTH" if any(h[2] == 102 for h in hits) else "")

# nonzero-byte-count per record buckets
def buckets(rows):
    return collections.Counter(sum(1 for b in r if b) for r in rows)
ba, bc = buckets(A), buckets(C)
# find any threshold t where count(nz>=t) == 60 in A and == 102 in C
for t in range(0, 130):
    a = sum(n for k, n in ba.items() if k >= t)
    if a == 60:
        c = sum(n for k, n in bc.items() if k >= t)
        print(f"  nz>={t}: A=60 C={c}", "MATCH-BOTH" if c == 102 else "")
print("A nz-count hist (top):", ba.most_common(8))
print("C nz-count hist (top):", bc.most_common(8))
