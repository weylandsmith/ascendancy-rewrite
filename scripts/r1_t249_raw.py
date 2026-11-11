#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t249 S4: raw dump of list-object candidates. Print P, count, and the first
few u32 at P+0xcb (stride 8) with range classification, plus a hex window at
P+0x8b0..P+0x910 for shape. No recs assumption."""
import struct, sys, zipfile, glob, os, re, collections
sys.path.insert(0, "scripts")
import r1_slot as S
pay = S.load_payload("."); anch = S.anchors_cached(".", pay)

def load(path):
    mem = zipfile.ZipFile(path).read("Memory")
    B = S.base_of(mem, anch)
    return mem, B

def cls(v, mem, B):
    OFF = 0x82bb0
    if v == 0: return "null"
    if v == 0xffffffff: return "ff"
    dsx = v - B - OFF
    if 0 <= dsx < 0x20000: return f"dsx{dsx:#x}"
    if B <= v < B + 17_055_880: return f"heap{v-B:#x}"
    if v < 0x100000: return f"lo{v:#x}"
    return f"out{v:#x}"

def probe(label, path, want, show=12):
    mem, B = load(path)
    print(f"== {label} B={B:#x} want {want}")
    cands = [o for o in range(0x10000, len(mem)-0x910, 4)
             if struct.unpack_from("<H", mem, o+0x8c7)[0] == want]
    rng = collections.Counter()
    for P in cands:
        s8 = [struct.unpack_from("<I", mem, P+0xc7+8*k)[0] for k in range(4)]
        rng[tuple(cls(v, mem, B)[:4] for v in s8)] += 1
    for k, n in rng.most_common(10):
        print(f"   pattern {k}: {n}")
    for P in cands[:show]:
        s8 = [struct.unpack_from("<I", mem, P+0xc7+8*k)[0] for k in range(4)]
        print(f"   P={P:#x} heapoff={P-B:#x} s8={[cls(v,mem,B) for v in s8]}")

slots = [s for s in sorted(glob.glob("work/r1/playcap/save/*.sav"), key=os.path.getmtime)
         if os.path.getsize(s) > 200000]
probe("t1086 ring", slots[-1], 60)
probe("t1254 bank", "work/r1/bank-t1254/48.sav", 102)
