#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t249 S7: (a) validate OBJ=0xfda074 set-equality at t1254: entries must be
rec+0x33 EXACTLY for every rec with owner==race (and nothing else);
(b) widget anchor: pointer sites of OBJ-0xab and OBJ in data seg;
(c) full ring sweep: signature-hit count per slot (does a 60 ever appear?
    is the object absent in the live session because the screen never opened?).
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

def sig_hits(mem):
    hits = []
    for o in range(0, len(mem) - 0x8cf, 4):
        if struct.unpack_from("<H", mem, o + 0x8c9)[0] != 0x8d: continue
        if struct.unpack_from("<I", mem, o + 0xab)[0] != 0: continue
        if struct.unpack_from("<I", mem, o + 0xbb)[0] != 0xffffffff: continue
        if mem[o + 0xc5] != 0: continue
        hits.append(o)
    return hits

# (a) set-equality at t1254
mem = zipfile.ZipFile("work/r1/bank-t1254/48.sav").read("Memory")
B = S.base_of(mem, anch); OFF = 0x82bb0
race = mem[B + OFF + 0x7458e]
rbase, recs = records(mem)
OBJ = 0xfda074
cnt = struct.unpack_from("<H", mem, OBJ + 0x8c7)[0]
ents = [struct.unpack_from("<I", mem, OBJ + 0xc7 + 8*k)[0] for k in range(cnt)]
want = sorted(j + 0x33 for j, v in recs.items() if v[1] == race)
got = sorted(ents)
print(f"(a) t1254 OBJ count={cnt} | set-equal: {got == want} | "
      f"missing {len(set(want)-set(got))} extra {len(set(got)-set(want))}")
extra = sorted(set(got) - set(want)); miss = sorted(set(want) - set(got))
for e in extra[:8]:
    print(f"    extra {e:#x} (rec@{e-0x33:#x} owner {recs.get(e-0x33, ('?',None))[1]})")
for e in miss[:8]:
    print(f"    miss  {e:#x} {recs.get(e-0x33)}")
# second dwords
zbad = sum(1 for k in range(cnt) if struct.unpack_from("<I", mem, OBJ+0xcb+8*k)[0] != 0)
print(f"    companion dwords nonzero: {zbad}/{cnt}")

# (b) widget anchor
tgt = struct.pack("<I", OBJ)
sites = [m.start() for m in re.finditer(re.escape(tgt), mem)]
print(f"(b) ptr-sites of OBJ: {len(sites)}")
for s in sites[:15]:
    dsx = s - B - OFF
    print(f"    site {s:#x} dsx={dsx:#x} {'DATA-SEG' if 0<=dsx<0x20000 else 'heap'}")

# (c) ring sweep (sampled by mtime across slots)
print("(c) ring sweep:")
slots = [s for s in sorted(glob.glob("work/r1/playcap/save/*.sav"), key=os.path.getmtime)
         if os.path.getsize(s) > 200000]
hist = collections.Counter()
for p in slots:
    m = zipfile.ZipFile(p).read("Memory")
    Bb = S.base_of(m, anch)
    t = struct.unpack_from("<I", m, Bb + OFF + 0x12e10)[0]
    hs = sig_hits(m)
    cs = [struct.unpack_from("<H", m, o + 0x8c7)[0] for o in hs]
    hist[tuple(cs)] += 1
    if len(hs) > 1 or (cs and cs[0] not in (102,)):
        print(f"    {os.path.basename(p)} turn {t}: hits {[hex(o) for o in hs]} counts {cs}")
print(f"    per-slot count-signature hist: {dict(hist)}  over {len(slots)} slots")
