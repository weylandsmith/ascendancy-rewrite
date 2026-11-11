#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t249 S3: inspect raw candidate list-objects. For each u32-aligned P with
u16[P+0x8c7]==want, dump entry pointers at P+0xcb (stride 8) and classify:
-> planet record? -> other? Also try stride 4 and offset variants, and check
whether entries point to PLANET RECORDS OF ANY owner (list may be unfiltered).
"""
import struct, sys, zipfile, glob, os, re
sys.path.insert(0, "scripts")
import r1_slot as S
STRIDE = 123; NAMEW = 19
NAME_RE = rb"[A-Z][A-Za-z]{2,}(?: [IVX]+)?\x00"

def load(path):
    mem = zipfile.ZipFile(path).read("Memory")
    B = S.base_of(mem, anch)
    return mem, B

def planet_index(mem):
    hits = set(m.start() for m in re.finditer(NAME_RE, mem))
    cands = [h for h in hits if all(h + i*STRIDE in hits for i in range(15))]
    def runlen(c):
        n = 0; p = c
        while p in hits: n += 1; p += STRIDE
        return n
    c = max(cands, key=runlen); base = c
    while base - STRIDE in hits: base -= STRIDE
    recs = {}
    for k in range(160):
        j = base + k*STRIDE
        raw = mem[j:j+NAMEW]
        if raw.strip(b"\x00") == b"": continue
        recs[j] = (raw.split(b"\x00")[0].decode(errors="replace"), mem[j+0x33])
    return base, recs

pay = S.load_payload("."); anch = S.anchors_cached(".", pay)

def probe(label, path, want):
    mem, B = load(path)
    OFF = 0x82bb0
    race = mem[B + OFF + 0x7458e]
    base, recs = planet_index(mem)
    print(f"== {label} turn {struct.unpack_from('<I', mem, B+OFF+0x12e10)[0]} race {race} want {want}")
    cands = [o for o in range(0x10000, len(mem)-0x8ff, 4)
             if struct.unpack_from("<H", mem, o+0x8c7)[0] == want]
    print(f"   raw cands {len(cands)}")
    for P in cands:
        s8 = [struct.unpack_from("<I", mem, P+0xc7+k*8)[0] for k in range(min(want, 6))]
        hits8 = sum(1 for e in s8 if e in recs)
        s4 = [struct.unpack_from("<I", mem, P+0xcb+k*4)[0] for k in range(min(want, 6))]
        hits4 = sum(1 for e in s4 if e in recs)
        # zero-run size right after count (0x8c9..): list objs have bookkeeping
        tail = mem[P+0x8c9:P+0x8d9]
        if hits8 or hits4:
            print(f"   P={P:#x} s8hits {hits8}/6 s4hits {hits4}/6 s8={[hex(x) for x in s8[:4]]}")
            for e in s8[:3]:
                if e in recs: print(f"      -> {recs[e]}")
    return mem, B, recs

slots = [s for s in sorted(glob.glob("work/r1/playcap/save/*.sav"), key=os.path.getmtime)
         if os.path.getsize(s) > 200000]
probe("t1086 ring", slots[-1], 60)
probe("t1254 bank", "work/r1/bank-t1254/48.sav", 102)
