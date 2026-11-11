#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t248 predicate search: find f such that count(f(planet)) == header at BOTH
t1086 (60) and t1254 (102). Owned-by-race0 counts: 80 @1086, 108 @1254.
Sweeps per byte offset d and per value v: ==v, !=v, >v, bit k set; also u16."""
import struct, sys, zipfile, collections, re, os, glob
sys.path.insert(0, "scripts")
import r1_slot as S
OFF = 0x82bb0; STRIDE = 123; NAMEW = 19
NAME_RE = rb"[A-Z][A-Za-z]{2,}(?: [IVX]+)?\x00"
pay = S.load_payload("."); anch = S.anchors_cached(".", pay)

def table(path):
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
    recs = []
    for k in range(151):
        j = base + k*STRIDE
        raw = mem[j:j+NAMEW]
        if raw.strip(b"\x00") == b"": continue
        recs.append({"k": k, "name": raw.split(b"\x00")[0].decode(errors="replace"),
                     "owner": mem[j+0x33], "j": j})
    return mem, B, race, recs

slots = [s for s in sorted(glob.glob("work/r1/playcap/save/*.sav"), key=os.path.getmtime)
         if os.path.getsize(s) > 200000]
memA, BA, raceA, recsA = table(slots[-1])          # t1086
memC, BB, raceB, recsC = table("work/r1/bank-t1254/48.sav")  # t1254
print(f"A: turn {struct.unpack_from('<I', memA, BA+OFF+0x12e10)[0]} owned {sum(1 for r in recsA if r['owner']==raceA)} (header 60)")
print(f"C: turn {struct.unpack_from('<I', memC, BB+OFF+0x12e10)[0]} owned {sum(1 for r in recsC if r['owner']==raceB)} (header 102)")

def cnt(mem, recs, pred):
    return sum(1 for r in recs if pred(mem, r))

found = []
for d in range(STRIDE):
    for v in range(256):
        a = cnt(memA, recsA, lambda m, r, d=d, v=v: m[r["j"]+d] == v)
        if a == 60:
            c = cnt(memC, recsC, lambda m, r, d=d, v=v: m[r["j"]+d] == v)
            found.append(("==v", d, v, c))
        b = cnt(memA, recsA, lambda m, r, d=d, v=v: m[r["j"]+d] != v)
        if b == 60:
            c = cnt(memC, recsC, lambda m, r, d=d, v=v: m[r["j"]+d] != v)
            found.append(("!=v", d, v, c))
for d in range(STRIDE):
    for k in range(8):
        a = cnt(memA, recsA, lambda m, r, d=d, k=k: (m[r["j"]+d] >> k) & 1)
        if a == 60:
            c = cnt(memC, recsC, lambda m, r, d=d, k=k: (m[r["j"]+d] >> k) & 1)
            found.append(("bit", d, k, c))
print("preds hitting 60 @1086 (value, count@1254 — want 102):")
for f in found:
    print("   ", f, "MATCH-BOTH" if f[3] == 102 else "")
# combined preds: owner==race AND <pred>
found2 = []
for d in range(STRIDE):
    a = cnt(memA, recsA, lambda m, r, d=d: r["owner"] == raceA and m[r["j"]+d] != 0)
    if a == 60:
        c = cnt(memC, recsC, lambda m, r, d=d: r["owner"] == raceB and m[r["j"]+d] != 0)
        found2.append(("owner&!=0", d, c))
for d in range(STRIDE):
    for v in range(256):
        a = cnt(memA, recsA, lambda m, r, d=d, v=v: r["owner"] == raceA and m[r["j"]+d] == v)
        if a == 60:
            c = cnt(memC, recsC, lambda m, r, d=d, v=v: r["owner"] == raceB and m[r["j"]+d] == v)
            found2.append(("owner&==v", d, v, c))
print("owner-AND preds hitting 60:")
for f in found2:
    print("   ", f, "MATCH-BOTH" if f[-1] == 102 else "")
