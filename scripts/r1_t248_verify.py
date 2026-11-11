#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t248 VERIFY: planet-record +0x33 == owner race index (0xFF = unowned)?

Chain to close (docs/re/selfplay.md t247 lead):
  V1  count(+0x33 != 0xFF) == sum(star+0x5a) over ALL 50 stars
  V2  per-system: count(colonised planets of system) == that star's +0x5a
  V3  count(+0x33 == 0) == 102 == header, and every such planet sits in a
      star whose owner byte has the player bit set
  V4  the co-owned star (owner byte 129) splits its planets across owners,
      explaining the 104-vs-102 delta exactly
"""
import struct, sys, zipfile, collections, re, os
sys.path.insert(0, "scripts")
import r1_slot as S

OFF = 0x82bb0
STRIDE = 0x7b
BANK = os.environ.get("BANK", "work/r1/bank-t1254")
SLOT = os.environ.get("SLOT", "48")

pay = S.load_payload("."); anch = S.anchors_cached(".", pay)
mem = zipfile.ZipFile(f"{BANK}/{SLOT}.sav").read("Memory")
B = S.base_of(mem, anch)
race = mem[B + OFF + 0x7458e]
turn = struct.unpack_from("<I", mem, B + OFF + 0x12e10)[0]
pbase = None
# locate planet table by the known first name (Vega I) at stride 0x7b
NAME_RE = rb"[A-Z][A-Za-z]{2,}(?: [IVX]+)?\x00"
hits = set(m.start() for m in re.finditer(NAME_RE, mem))
cand = [h for h in hits if all(h + k*STRIDE in hits for k in range(20))]
runs = sorted(((sum(1 for k in range(200) if h + k*STRIDE in hits), h) for h in cand), reverse=True)
h0 = runs[0][1]
while h0 - STRIDE in hits and h0 - 2*STRIDE in hits:
    h0 -= STRIDE
pbase = h0

planets = []
k = 0
while h0 + k*STRIDE in hits:
    j = h0 + k*STRIDE
    m = re.match(NAME_RE, mem[j:j+40])
    planets.append({
        "idx": k, "j": j, "name": mem[j:j+m.end()-1].decode(),
        "owner": mem[j + 0x33], "pidx": mem[j + 0x65],
    })
    k += 1
print(f"slot {SLOT} turn {turn} race {race} | {len(planets)} planet records @phys {pbase-0x88:#x}")

star_base = B + OFF + 0x13bc5
NSTAR = struct.unpack_from("<H", mem, B + OFF + 0x16145)[0]
stars = []
for i in range(NSTAR):
    r = mem[star_base + i*0x60 : star_base + (i+1)*0x60]
    nm = b"".join(bytes([c]) for c in r if 32 <= c < 127)
    stars.append({"idx": i, "owner": r[0x14], "n5a": r[0x5a], "ascii": nm[:24].decode(errors="replace")})
print(f"NSTAR WORD ds:0x16145 = {NSTAR}")

# ---- V1 global totals
colonised = sum(1 for p in planets if p["owner"] != 0xFF)
sum5a_all = sum(s["n5a"] for s in stars)
print(f"V1 colonised(+0x33!=FF)={colonised}  sum(star+0x5a) all stars={sum5a_all}  "
      f"{'MATCH' if colonised == sum5a_all else 'MISMATCH'}")

# ---- build system grouping from names (star name = planet name minus roman)
def sysname(n):
    return re.sub(r"\s+[IVX]+$", "", n)
by_sys = collections.defaultdict(list)
for p in planets:
    by_sys[sysname(p["name"])].append(p)
print(f"distinct system names in planet table: {len(by_sys)}")

# star names: which ascii run in a star record is the system name? try each and
# see which one keys into by_sys
keyed = collections.Counter()
for s in stars:
    toks = re.findall(rb"[A-Z][A-Za-z]{3,}", b"".join(
        bytes([c]) for c in mem[star_base+s['idx']*0x60:(star_base+s['idx']*0x60+0x60)]))
    for t in toks:
        keyed[t.decode()] += 1
star_name_of = {}
for s in stars:
    raw = mem[star_base+s['idx']*0x60 : star_base+s['idx']*0x60+0x60]
    toks = re.findall(rb"[A-Z][A-Za-z]{3,}", b"".join(bytes([c]) for c in raw))
    for t in toks:
        if t.decode() in by_sys:
            star_name_of[s["idx"]] = t.decode(); break
print(f"stars whose ascii names a planet-system: {len(star_name_of)}/{NSTAR}")

# ---- V2 per-system colonised count vs star +0x5a
if len(star_name_of) >= 30:
    ok = bad = 0
    for si, nm in star_name_of.items():
        c = sum(1 for p in by_sys[nm] if p["owner"] != 0xFF)
        if c == stars[si]["n5a"]:
            ok += 1
        else:
            bad += 1
            if bad <= 8:
                print(f"  V2 MISMATCH sys {nm} star{si}: colonised={c} +0x5a={stars[si]['n5a']} owner={stars[si]['owner']}")
    print(f"V2 per-system colonised == star+0x5a: {ok} ok / {bad} bad")

    # ---- V3 player count + bit-set consistency
    n_mine = sum(1 for p in planets if p["owner"] == race)
    print(f"V3 count(+0x33==race{race}) = {n_mine}")
    owner_hist = collections.Counter(p["owner"] for p in planets)
    print(f"    owner hist: {sorted(owner_hist.items())}")
    inconsistent = []
    for p in planets:
        if p["owner"] == 0xFF:
            continue
        si = star_name_of.get(star_name_of and sysname(p["name"]))
        pass
    # per star: every planet owner must have its bit in the star owner byte
    bit_bad = 0
    for si, nm in star_name_of.items():
        sbits = stars[si]["owner"]
        for p in by_sys[nm]:
            if p["owner"] == 0xFF:
                continue
            if not (sbits >> p["owner"]) & 1:
                bit_bad += 1
                if bit_bad <= 8:
                    print(f"  V3b BIT MISMATCH {p['name']} owner={p['owner']} star{si} ownerbyte={sbits}")
    print(f"V3b planets whose owner-bit is IN the star owner byte: violations {bit_bad}")

# ---- V4 co-owned stars
co = [s for s in stars if bin(s["owner"]).count("1") >= 2]
print(f"V4 co-owned stars: {[(s['idx'], s['owner'], s['n5a'], star_name_of.get(s['idx'])) for s in co]}")
for s in co:
    nm = star_name_of.get(s["idx"])
    if nm:
        rows = [(p["name"], p["owner"]) for p in by_sys[nm]]
        mine = sum(1 for _, o in rows if o == race)
        print(f"   sys {nm}: {rows} -> player-owned {mine} of {len(rows)}")
delta = sum(s["n5a"] for s in stars if (s["owner"] >> race) & 1)
mine = sum(1 for p in planets if p["owner"] == race)
print(f"V4 sum(+0x5a) over player-bit-set stars = {delta}; per-planet player count = {mine}; delta {delta-mine}")
