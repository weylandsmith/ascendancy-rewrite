#!/usr/bin/env python3
"""t249 S6: locate the planet-list OBJECT by its OPEN-TIME signature.
FUN_00051834 case 1 (screen open) does on the freshly alloc'd list obj:
   [obj+0xab]=0 ; [obj+0x8c9]=0x8d ; [obj+0xc5]=0 ; [obj+0xbb]=0xffffffff
   FUN_00032fdc -> u16[obj+0x8c7]=0 (zero count)
   for k < u16@0x3a093: if byte[rec0+0x33+k*0x7b]==race: FUN_00032d1c (add)
   FUN_00033470 ; FUN_00032f6c (selected := param)
So the header PLANETS number == u16[obj+0x8c7] of THIS object, frozen at the
turn the screen was last OPENED (no per-turn refresh exists in this routine).
Scan both slots for the signature; report count, bound, entries.
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
    for k in range(200):
        j = base + k*STRIDE
        raw = mem[j:j+NAMEW]
        if raw.strip(b"\x00") == b"": continue
        recs[j] = (raw.split(b"\x00")[0].decode(errors="replace"), mem[j+0x33], k)
    return base, recs

def probe(label, path):
    mem = zipfile.ZipFile(path).read("Memory")
    B = S.base_of(mem, anch)
    OFF = 0x82bb0
    race = mem[B + OFF + 0x7458e]
    turn = struct.unpack_from("<I", mem, B + OFF + 0x12e10)[0]
    rbase, recs = records(mem)
    bound = struct.unpack_from("<H", mem, B + OFF + 0x3a093)[0]
    n_all = sum(1 for v in recs.values() if v[1] == race)
    n_bound = sum(1 for j, v in recs.items() if v[1] == race and v[2] < bound)
    print(f"== {label} ({os.path.basename(path)}) turn {turn} race {race} "
          f"bound u16@0x3a093={bound} named={len(recs)} owner==race all={n_all} "
          f"within-bound={n_bound}")
    # signature scan: [o+0xab]==0, byte[o+0xc5]==0, [o+0xbb]==0xffffffff,
    # u16[o+0x8c9]==0x8d
    hits = []
    for o in range(0, len(mem) - 0x8cf, 4):
        if struct.unpack_from("<H", mem, o + 0x8c9)[0] != 0x8d: continue
        if struct.unpack_from("<I", mem, o + 0xab)[0] != 0: continue
        if struct.unpack_from("<I", mem, o + 0xbb)[0] != 0xffffffff: continue
        if mem[o + 0xc5] != 0: continue
        hits.append(o)
    print(f"   signature hits: {len(hits)}")
    for o in hits:
        cnt = struct.unpack_from("<H", mem, o + 0x8c7)[0]
        sel = struct.unpack_from("<H", mem, o + 0x8cd)[0]
        ent = [struct.unpack_from("<I", mem, o + 0xc7 + 8*k)[0] for k in range(min(cnt, 5))]
        kinds = []
        for e in ent:
            if e in recs: kinds.append(f"rec{recs[e][0]}")
            else: kinds.append(hex(e))
        print(f"   OBJ={o:#x} (heapoff {o-B:#x}) count={cnt} sel={sel} ent0..={kinds}")
    return mem, B, hits

slots = [s for s in sorted(glob.glob("work/r1/playcap/save/*.sav"), key=os.path.getmtime)
         if os.path.getsize(s) > 200000]
probe("t1086 ring", slots[-1])
probe("t1254 bank", "work/r1/bank-t1254/48.sav")
