#!/usr/bin/env python3
"""t248: is the t1086 count(80) inflated by table slots whose names don't key
any star record? Count owner==race only among planets in star-named systems,
at both timestamps. Also print the tail names past k=140.
"""
import struct, sys, zipfile, collections, re, os, glob
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
    turn = struct.unpack_from("<I", mem, B + OFF + 0x12e10)[0]
    star_base = B + OFF + 0x13bc5
    nstar = struct.unpack_from("<H", mem, B + OFF + 0x16145)[0]
    star_sys = set()
    for i in range(nstar):
        raw = mem[star_base+i*0x60 : star_base+(i+1)*0x60]
        toks = [t.decode() for t in re.findall(rb"[A-Z][A-Za-z]{3,}",
                b"".join(bytes([c]) for c in raw if 32 <= c < 127))]
        star_sys.update(toks)
    recs = []
    for k in range(160):
        j = base + k*STRIDE
        raw = mem[j:j+NAMEW]
        if raw.strip(b"\x00") == b"":
            continue
        nm = raw.split(b"\x00")[0].decode(errors="replace")
        recs.append({"k": k, "name": nm, "sys": re.sub(r"\s+[IVX]+$", "", nm),
                     "owner": mem[j+0x33]})
    return mem, B, race, turn, star_sys, recs

for label, path, hdr in (("t1086 ring", "LIVE", 60), ("t1254 bank", "work/r1/bank-t1254/48.sav", 102)):
    if path == "LIVE":
        slots = [s for s in sorted(glob.glob("work/r1/playcap/save/*.sav"), key=os.path.getmtime)
                 if os.path.getsize(s) > 200000]
        path = slots[-1]
    mem, B, race, turn, star_sys, recs = load(path)
    in_star = [r for r in recs if r["sys"] in star_sys]
    orph = [r for r in recs if r["sys"] not in star_sys]
    mine_all = sum(1 for r in recs if r["owner"] == race)
    mine_star = sum(1 for r in in_star if r["owner"] == race)
    print(f"\n== {label} ({os.path.basename(path)}) turn {turn} race {race}: header={hdr}")
    print(f"   records {len(recs)} | in-star-system {len(in_star)} (mine {mine_star}) | orphan {len(orph)}")
    print(f"   count(owner==race) ALL = {mine_all} | STAR-KEYED = {mine_star}")
    if orph[:12]:
        print("   orphan examples:", [(r["k"], r["name"], hex(r["owner"])) for r in orph[:12]])
    print("   tail k>=138:", [(r["k"], r["name"], hex(r["owner"])) for r in recs if r["k"] >= 138])
