#!/usr/bin/env python3
"""t248: hunt the per-planet owner table in the banked t1254 slot.

Hypothesis chain (docs/re/selfplay.md t247): header "102 Planets Occupied"
= player-OWNED planets; star-record byte +0x5a = colonised count per star
(sum over player-bit-set stars = 104, delta 2 sits on co-owned star idx25
owner=129). The per-planet owner must live somewhere; prime candidate is the
151-record stride-0x7b PLANET TABLE (law: r1_planet_layout.py, resume.gam
mirror 151/151 byte-identical except +0x68/+0x69 counters).

Legs:
 1. anchor the planet table in work/r1/bank-t1254/48.sav by first name;
 2. census every record byte offset: look for a field whose
    count(owner==race0) == 102 or count(owner!=0xFF-sentinel) ~ colonised;
 3. cross-check the co-owned star idx25: its 4 planets should split owner
    2x race0 + 2x race7.
"""
import struct, sys, zipfile, collections, re, os
sys.path.insert(0, "scripts")
import r1_slot as S

OFF = 0x82bb0
STRIDE = 0x7b
SAV = "work/r1/bank-t1254/48.sav"

pay = S.load_payload("."); anch = S.anchors_cached(".", pay)
mem = zipfile.ZipFile(SAV).read("Memory")
B = S.base_of(mem, anch)
H = B - 0x1BF450            # pointer law: phys p at member idx p+H
race = mem[B + OFF + 0x7458e]
turn = struct.unpack_from("<I", mem, B + OFF + 0x12e10)[0]
print(f"B={B:#x} H={H:#x} race={race} turn={turn}")

# --- leg 1: locate planet table by name pattern (0x7b stride law) --------
NAME_RE = rb"[A-Z][A-Za-z]{2,}(?: [IVX]+)?\x00"
# candidate bases: any name hit whose next-3 records are exactly stride away
hits = [m.start() for m in re.finditer(NAME_RE, mem[H:H+0x400000])]
hits = [h + H for h in hits]
good = []
for h in hits:
    ok = 0
    p = h
    hs = set(hits)
    while p in hs:
        ok += 1; p += STRIDE
    if ok >= 8:
        good.append((ok, h))
good.sort(reverse=True)
print("stride-0x7b name runs >=8 (top 5):", [(n, hex(b)) for n, b in good[:5]])
if not good:
    sys.exit("planet table not found")
n_run, base = good[0]
# walk back to true record 0 (run may start mid-table)
while True:
    prev = base - STRIDE
    hs = set(hits)
    if prev in hs and (prev - STRIDE) in hs:
        base = prev
    else:
        break
# count records forward
recs = 0
p = base
hs = set(hits)
while p in hs:
    recs += 1; p += STRIDE
print(f"planet table base phys {base-H:#x} (member idx {base:#x}), name-run recs={recs}")

names = []
for k in range(recs):
    j = base + k * STRIDE
    m = re.match(NAME_RE, mem[j:j+40])
    names.append(mem[j:j+m.end()-1].decode() if m else "?")
print("first 8 names:", names[:8])

# --- leg 2: census every byte offset ------------------------------------
RACE_BIT = 1 << race
star_base = B + OFF + 0x13bc5
star_owner = [mem[star_base + i*0x60 + 0x14] for i in range(50)]
bitset_idx = [i for i in range(50) if (star_owner[i] >> race) & 1]
sum5a = sum(mem[star_base + i*0x60 + 0x5a] for i in bitset_idx)
print(f"stars bit-set={len(bitset_idx)} sum+0x5a={sum5a} (header 102 expected)")

for d in range(STRIDE):
    vals = [mem[base + k*STRIDE + d] for k in range(recs)]
    hist = collections.Counter(vals)
    n_ff = hist.get(0xFF, 0)
    n_zero = hist.get(0, 0)
    # candidate owner-ish fields: small value set, or sentinel-heavy
    small = {v for v in vals if v not in (0, 0xFF)}
    if (hist.get(0,0) >= 40 and len(small) <= 9 and max(small or [0]) <= 7) or \
       (n_ff >= 40 and len(small) <= 9):
        print(f"  +0x{d:02x}: hist {sorted(hist.items())}")

# --- leg 2b: direct 102 test on u8/u16 per-record aggregates -------------
for d in range(STRIDE):
    s = sum(mem[base + k*STRIDE + d] for k in range(recs))
    if 95 <= s <= 115:
        print(f"  SUM +0x{d:02x} over {recs} recs = {s}")

# --- leg 3: star idx25 split check (needs star link field; try name prefix)
print("idx25 owner:", star_owner[25], " +0x5a:", mem[star_base+25*0x60+0x5a])
# dump star record 25 nonzero bytes for the link hunt
r25 = mem[star_base+25*0x60 : star_base+26*0x60]
nz = [(o, r25[o]) for o in range(0x60) if r25[o]]
print("star25 nonzero:", nz)
