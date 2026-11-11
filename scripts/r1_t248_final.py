#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t248 FINAL: owner-field structural proof at BOTH timestamps with the
verify.py keying (star tokens from raw star-record bytes, no printable filter).
(a) subset: every colonised planet's (1<<owner) bit is in its star's +0x14.
(b) equality: star+0x14 & 0x7f == OR over its planets.
(c) count(NAMED && owner==race) vs header."""
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
    planets = []
    for k in range(160):
        j = base + k*STRIDE
        raw = mem[j:j+NAMEW]
        if raw.strip(b"\x00") == b"": continue
        planets.append({"name": raw.split(b"\x00")[0].decode(errors="replace"),
                        "owner": mem[j+0x33]})
    star_base = B + OFF + 0x13bc5
    nstar = struct.unpack_from("<H", mem, B + OFF + 0x16145)[0]
    by_sys = collections.defaultdict(list)
    for p in planets:
        by_sys[re.sub(r"\s+[IVX]+$", "", p["name"])].append(p)
    keyed = {}
    for i in range(nstar):
        raw = mem[star_base+i*0x60 : star_base+(i+1)*0x60]
        # keep separators: nulls/controls become b" " so tokens don't merge
        clean = bytes(c if 32 <= c < 127 else 32 for c in raw)
        toks = [t.decode() for t in re.findall(rb"[A-Z][A-Za-z]{3,}", clean)]
        nm = next((t for t in toks if t in by_sys), None)
        if nm:
            keyed[i] = (nm, raw[0x14])
    return race, turn, planets, keyed

for label, path, hdr in (("t1086 ring", None, 60), ("t1254 bank", "work/r1/bank-t1254/48.sav", 102)):
    if path is None:
        slots = [s for s in sorted(glob.glob("work/r1/playcap/save/*.sav"),
                                   key=os.path.getmtime) if os.path.getsize(s) > 200000]
        path = slots[-1]
    race, turn, planets, keyed = load(path)
    n_mine = sum(1 for p in planets if p["owner"] == race)
    colonised = sum(1 for p in planets if p["owner"] != 0xFF)
    sub_bad = eq_bad = n_keyed_planets = 0
    for i, (nm, sb) in keyed.items():
        want = 0
        for p in by_sys[nm] if False else []:
            pass
    by_sys = collections.defaultdict(list)
    for p in planets:
        by_sys[re.sub(r"\s+[IVX]+$", "", p["name"])].append(p)
    bad_list = []
    for i, (nm, sb) in keyed.items():
        want = 0
        for p in by_sys[nm]:
            if p["owner"] != 0xFF:
                want |= 1 << p["owner"]
                n_keyed_planets += 1
                if not (sb >> p["owner"]) & 1:
                    sub_bad += 1
        if (sb & 0x7F) != want:
            eq_bad += 1
            if len(bad_list) < 6:
                bad_list.append((nm, hex(sb), hex(want)))
    print(f"== {label} ({os.path.basename(path)}) turn {turn} race {race} | header {hdr}")
    print(f"   planets(named) {len(planets)} colonised {colonised} | star systems keyed {len(keyed)}/50")
    print(f"   (a) subset: planets in keyed systems {n_keyed_planets}, owner-bit-missing violations {sub_bad}")
    print(f"   (b) equality star&0x7f==OR: violations {eq_bad} {bad_list}")
    print(f"   (c) count(owner==race) = {n_mine} vs header {hdr}")
