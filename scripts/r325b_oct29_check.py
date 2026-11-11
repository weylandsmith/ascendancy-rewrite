#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r325b — t325 Phase A2: (1) newest production ring slot turn (sitting
corroboration on the SAVE axis, t215 law); (2) oct29 raw vendor save walk —
does the scratch-boot campaign (RESUME.GAM.user-oct29) have a pending shield
build?; (3) item 26 row cost/ind (turn-budget arithmetic)."""
import os, struct, sys, zipfile, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import r1_income_law as IL

pay = open(os.path.join(ROOT, "work/ascend_payload.bin"), "rb").read()
anch = IL.build_anchors(pay)

# 1) save-axis turn check
ring = sorted(glob.glob(os.path.join(ROOT, "work/r1/playcap/save/*.sav")),
              key=os.path.getmtime)
print("=== production ring, newest 6 by mtime ===")
for f in ring[-6:]:
    mm = zipfile.ZipFile(f).read("Memory")
    vv, _ = IL.find_base(mm, anch)
    if not vv:
        print(os.path.basename(f), "BASE-FAIL"); continue
    BB = vv.most_common(1)[0][0]
    turn = struct.unpack_from("<I", mm, BB + 0x82BB0 + 0x12E10)[0]
    print(os.path.basename(f), "turn", turn)

# 2) oct29 raw vendor save
raw = open(os.path.join(ROOT, "work/r1/game/RESUME.GAM.user-oct29"), "rb").read()
NAME_RE = re.compile(rb"[A-Z][A-Za-z]{2,}(?: [IVX]+)?\x00")
hits = [m.start() for m in NAME_RE.finditer(raw)]
hs = set(hits)
best = (0, None)
for h in hits:
    n = 0; p = h
    while p in hs:
        n += 1; p += 123
    if n > best[0]:
        best = (n, h)
print("=== oct29 raw vendor save ===")
print("longest 123-stride name run:", best)
n0, p0 = best
recs = {}
p = p0
while p in hs and p + 123 <= len(raw):
    name = raw[p:raw.index(b"\x00", p)].decode("cp437", "replace")
    base = p - 0x24
    ptr = struct.unpack_from("<I", raw, base + 0x10)[0]
    it = raw[base + 0x54]
    acc = struct.unpack_from("<H", raw, base + 0x50)[0]
    recs[name] = (ptr, it, acc)
    p += 123
print(f"records walked: {len(recs)}")
shields = {18, 19, 26, 27}
pend = [(nm, v) for nm, v in recs.items() if v[1] in shields]
print("PENDING SHIELD builds in oct29:", pend or "NONE")
for nm in ("Gridsor I", "Vega I", "Smorgasbord II"):
    print(" ", nm, recs.get(nm))

# 3) item rows (from ring 52 RAM)
m = zipfile.ZipFile(os.path.join(ROOT, "work/r1/playcap/save/52.sav")).read("Memory")
v, _ = IL.find_base(m, anch); B = v.most_common(1)[0][0]
idx = B + 0x82BB0 + 0x73E40
print("=== item rows (runtime RAM) ===")
for k in (18, 19, 26, 27):
    b = idx + k * IL.ITEM_STRIDE
    name = m[b + 10:b + 40].split(b"\x00")[0].decode("cp437", "replace")
    ind = struct.unpack_from("<b", m, b)[0]
    cost = struct.unpack_from("<H", m, b + 8)[0]
    flags = struct.unpack_from("<H", m, b + 6)[0]
    print(f"item {k:2d} {name:24s} ind={ind} cost={cost} flags=0x{flags:04x}")
# Gridsor I slot 76 live view
for base, cells, cap, arr in IL.find_records(m):
    name = m[base + 0x24:base + 0x33].split(b"\x00")[0].decode("cp437", "replace")
    if name == "Gridsor I":
        s76 = arr + 4 * 76
        print(f"ring52 Gridsor I slot76 raw={m[s76:s76+4].hex()} byte3=0x{m[s76+3]:02x} "
              f"BPLM=00{arr + 4*76 + 3 & 0xFFFFFF:06X}")
