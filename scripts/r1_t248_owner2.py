#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t248 second-timestamp + structural closure for the per-planet owner law.

planet-record BYTE +0x33 (stride 0x7b table, phys 0x26d07b in the banked
t1254 slot) == owning race index, 0xFF == unowned.

Checks per slot:
  A  count(owner==race)            vs the header law (102 @t1254, 60 @t1086/92)
  B  star owner byte == OR over its planets' (1<<owner), bit7 aside
  C  star +0x5a == planet slots in system (total), NOT colonised count
  D  the planets inside player-bit-set stars that are NOT player-owned
     (the 104-vs-102 delta explained concretely)
  E  resume.gam static mirror: same field at file offset 0x9b1a+0x33
"""
import struct, sys, zipfile, collections, re, os, glob
sys.path.insert(0, "scripts")
import r1_slot as S

OFF = 0x82bb0
STRIDE = 0x7b
H_PTR = 0x88
NAME_RE = rb"[A-Z][A-Za-z]{2,}(?: [IVX]+)?\x00"

pay = S.load_payload("."); anch = S.anchors_cached(".", pay)

def sysname(n):
    return re.sub(r"\s+[IVX]+$", "", n)

def analyse(mem, B, label, header_planets=None):
    race = mem[B + OFF + 0x7458e]
    turn = struct.unpack_from("<I", mem, B + OFF + 0x12e10)[0]
    hits = set(m.start() for m in re.finditer(NAME_RE, mem))
    cand = [h for h in hits if all(h + k*STRIDE in hits for k in range(20))]
    if not cand:
        print(f"{label}: planet table NOT resident"); return None
    h0 = max(cand, key=lambda h: sum(1 for k in range(200) if h + k*STRIDE in hits))
    while h0 - STRIDE in hits and h0 - 2*STRIDE in hits:
        h0 -= STRIDE
    planets = []
    k = 0
    while h0 + k*STRIDE in hits:
        j = h0 + k*STRIDE
        m = re.match(NAME_RE, mem[j:j+40])
        planets.append({"name": mem[j:j+m.end()-1].decode(),
                        "owner": mem[j+0x33], "pidx": mem[j+0x65]})
        k += 1
    star_base = B + OFF + 0x13bc5
    nstar = struct.unpack_from("<H", mem, B + OFF + 0x16145)[0]
    stars = []
    for i in range(nstar):
        raw = mem[star_base+i*0x60 : star_base+(i+1)*0x60]
        toks = [t.decode() for t in re.findall(
            rb"[A-Z][A-Za-z]{3,}", b"".join(bytes([c]) for c in raw if 32 <= c < 127))]
        stars.append({"idx": i, "owner": raw[0x14], "n5a": raw[0x5a], "toks": toks})
    by_sys = collections.defaultdict(list)
    for p in planets:
        by_sys[sysname(p["name"])].append(p)
    star_name_of = {}
    for s in stars:
        for t in s["toks"]:
            if t in by_sys:
                star_name_of[s["idx"]] = t
                break
    n_mine = sum(1 for p in planets if p["owner"] == race)
    hist = collections.Counter(p["owner"] for p in planets)
    print(f"\n== {label}: turn {turn} race {race} | {len(planets)} planets, {nstar} stars")
    print(f"   A count(+0x33==race) = {n_mine}"
          + (f"   header={header_planets}  {'MATCH' if n_mine==header_planets else 'MISMATCH'}"
             if header_planets is not None else ""))
    print(f"     owner hist {sorted(hist.items())}")
    # B
    bad = []
    for si, nm in star_name_of.items():
        want = 0
        for p in by_sys[nm]:
            if p["owner"] != 0xFF:
                want |= 1 << p["owner"]
        got = stars[si]["owner"]
        if (got & 0x7F) != want:
            bad.append((nm, hex(got), hex(want)))
    print(f"   B starbyte&0x7f == OR(1<<owner of its planets): violations {len(bad)} {bad[:5]}")
    # C
    ok = sum(1 for si, nm in star_name_of.items() if len(by_sys[nm]) == stars[si]["n5a"])
    print(f"   C star+0x5a == TOTAL planet slots in system: {ok}/{len(star_name_of)} ok")
    ok2 = sum(1 for si, nm in star_name_of.items()
              if sum(1 for p in by_sys[nm] if p["owner"] != 0xFF) == stars[si]["n5a"])
    print(f"     (colonised-count reading would be {ok2}/{len(star_name_of)} — refuted)" if ok2 < ok else "")
    # D
    bitsys = [s for si, s in enumerate(stars) if (s["owner"] >> race) & 1]
    slots = sum(s["n5a"] for s in bitsys)
    alien = []
    for s in bitsys:
        nm = star_name_of.get(s["idx"])
        if not nm: continue
        for p in by_sys[nm]:
            if p["owner"] != race:
                alien.append((p["name"], p["owner"], hex(s["owner"])))
    print(f"   D player-bit-set stars {len(bitsys)}, slots {slots}, non-player planets {alien}")
    return {"turn": turn, "race": race, "n_mine": n_mine, "hist": dict(hist)}

# --- banked t1254 slots (header said 102)
res = []
for slot in ("48", "55"):
    mem = zipfile.ZipFile(f"work/r1/bank-t1254/{slot}.sav").read("Memory")
    B = S.base_of(mem, anch)
    r = analyse(mem, B, f"bank-t1254/{slot}", header_planets=102)
    if r: res.append(r)

# --- live ring (the resumed session; header law measured 60 at t1086..1092)
for p in sorted(glob.glob("work/r1/playcap/save/*.sav"), key=os.path.getmtime)[-3:]:
    mem = zipfile.ZipFile(p).read("Memory")
    B = S.base_of(mem, anch)
    if B is None:
        print(f"{p}: no base"); continue
    analyse(mem, B, f"live-ring/{os.path.basename(p)}", header_planets=60)

# --- E: resume.gam static mirror
gam = open("game/resume.gam", "rb").read()
p0 = 0x9b1a
print("\n== E resume.gam static mirror (first name @0x9b1a, stride 123)")
print("   rec0 name:", gam[p0:gam.index(b"\x00", p0)].decode(errors="replace"))
h = collections.Counter()
n = 0
p = p0
while p < len(gam):
    m = re.match(NAME_RE, gam[p:p+40])
    if not m: break
    h[gam[p+0x33]] += 1; n += 1; p += STRIDE
print(f"   {n} records, +0x33 hist {sorted(h.items())}")
