#!/usr/bin/env python3
"""t248 S4b: owner-AND predicates with u16 + bit forms, scored 60@t1086 AND
102@t1254. Also probe the SECOND stride-0x7b array the star records point to
(star+0x46..+0x55 hold 3-byte pointers ~0x26f3xx, stride 0x7b apart)."""
import struct, sys, zipfile, glob, os, collections, re
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
    recs = []
    for k in range(160):
        j = base + k*STRIDE
        raw = mem[j:j+NAMEW]
        if raw.strip(b"\x00") == b"": continue
        recs.append((mem[j+0x33], j))
    return mem, B, race, recs

slots = [s for s in sorted(glob.glob("work/r1/playcap/save/*.sav"), key=os.path.getmtime)
         if os.path.getsize(s) > 200000]
memA, BA, rA, recsA = load(slots[-1])
memC, BC, rC, recsC = load("work/r1/bank-t1254/48.sav")

def cnt(mem, recs, race, pred):
    return sum(1 for o, j in recs if o == race and pred(mem, j))

hits = []
for d in range(STRIDE-1):
    a = cnt(memA, recsA, rA, lambda m, j, d=d: struct.unpack_from("<H", m, j+d)[0] != 0)
    if a == 60:
        c = cnt(memC, recsC, rC, lambda m, j, d=d: struct.unpack_from("<H", m, j+d)[0] != 0)
        hits.append(("owner&u16!=0", d, c))
for d in range(STRIDE):
    for k in range(8):
        a = cnt(memA, recsA, rA, lambda m, j, d=d, k=k: (m[j+d] >> k) & 1)
        if a == 60:
            c = cnt(memC, recsC, rC, lambda m, j, d=d, k=k: (m[j+d] >> k) & 1)
            hits.append(("owner&bit", d, k, c))
print("owner-AND hits at 60@1086 (need 102@1254):")
for h in hits:
    print("   ", h, "MATCH-BOTH" if h[-1] == 102 else "")

# --- second array via star-record pointers
star_base = BC + OFF + 0x13bc5
ptrs = set()
for i in range(50):
    raw = memC[star_base+i*0x60 : star_base+(i+1)*0x60]
    for off in range(0x40, 0x5a):
        v = raw[off] | (raw[off+1] << 8) | (raw[off+2] << 16)
        if 0x260000 <= v < 0x280000:
            ptrs.add((i, off, v))
print(f"\nt1254 star-record 3-byte pointers in 0x260000..0x280000: {len(ptrs)}")
byoff = collections.Counter(off for _, off, _ in ptrs)
print("  source offsets:", sorted(byoff.items()))
if ptrs:
    lo = min(v for *_, v in ptrs); hi = max(v for *_, v in ptrs)
    print(f"  target span {lo:#x}..{hi:#x} ({hi-lo:#x})")
    # pointer law: phys p lives at member idx p + H (H=0x88)
    H = BC - 0x1BF450
    tgt = sorted(v for *_, v in ptrs)
    for d in range(0, 0x40):
        vals = [memC[v+H+d] for v in tgt]
        if sum(1 for x in vals if x == rC) in (60, 102):
            print(f"  runtime +0x{d:02x}: count==race {sum(1 for x in vals if x==rC)} (sampled {len(tgt)} ptr recs)")
    # are these the SAME 0x7b records? check name field at each
    named = 0
    for v in tgt:
        raw = memC[v+H:v+H+NAMEW]
        if re.fullmatch(NAME_RE, raw):
            named += 1
    print(f"  of {len(tgt)} pointer targets, {named} have a clean name field at +0x00")
