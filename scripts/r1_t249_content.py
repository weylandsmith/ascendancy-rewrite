#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t249 S5: find planet-LIST OBJECTS by content, not by count.
Law (static, this session): the list class stores entries inline at
obj+0xc7 stride 8 (add-routine FUN_00032d1c 0x32e9f/0x32eb6: ptr at
199+count*8, companion dword 0 at 203+count*8, count u16 @+0x8c7).
So: scan every aligned u32 run where >=4 consecutive stride-8 entries point
to DISTINCT planet records; report base, run length, and the count field at
(base-0xc7)+0x8c7. Also zip-member census (is 'Memory' the whole guest RAM?).
"""
import struct, sys, zipfile, glob, os, re, collections
sys.path.insert(0, "scripts")
import r1_slot as S
STRIDE = 123; NAMEW = 19
NAME_RE = rb"[A-Z][A-Za-z]{2,}(?: [IVX]+)?\x00"
pay = S.load_payload("."); anch = S.anchors_cached(".", pay)

def records(mem):
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

def probe(label, path):
    with zipfile.ZipFile(path) as z:
        print(f"== {label} members: {[(i.filename, i.file_size) for i in z.infolist()][:8]}")
        mem = z.read("Memory")
    B = S.base_of(mem, anch)
    OFF = 0x82bb0
    race = mem[B + OFF + 0x7458e]
    turn = struct.unpack_from("<I", mem, B + OFF + 0x12e10)[0]
    rbase, recs = records(mem)
    n_mine = sum(1 for j, v in recs.items() if v[1] == race)
    print(f"   turn {turn} race {race} recs {len(recs)} count(owner==race) {n_mine} "
          f"rec0={rbase:#x} len(mem)={len(mem):#x}")
    found = []
    o = 0
    n = len(mem)
    while o < n - 32:
        v = struct.unpack_from("<I", mem, o)[0]
        if v in recs:
            run = 0
            for k in range(0, 200):
                e = struct.unpack_from("<I", mem, o + k*8)[0] if o + k*8 + 4 <= n else None
                if e in recs: run += 1
                else: break
            if run >= 3:
                lb = o  # candidate entries base
                obj = lb - 0xc7
                cnt = struct.unpack_from("<H", mem, obj + 0x8c7)[0] if 0 <= obj and obj + 0x8cd <= n else None
                owners = collections.Counter(recs[struct.unpack_from('<I', mem, o+k*8)[0]][1] for k in range(run))
                found.append((o, run, cnt, dict(owners)))
                o += run*8
                continue
        o += 4
    for o, run, cnt, owners in found[:20]:
        print(f"   entries@{o:#x} run {run} obj={o-0xc7:#x} u16[obj+0x8c7]={cnt} owners={owners}")
    return mem, B, recs

slots = [s for s in sorted(glob.glob("work/r1/playcap/save/*.sav"), key=os.path.getmtime)
         if os.path.getsize(s) > 200000]
probe("t1086 ring", slots[-1])
probe("t1254 bank", "work/r1/bank-t1254/48.sav")
