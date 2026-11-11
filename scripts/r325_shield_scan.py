#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r325_shield_scan.py — t325 PHASE A: find shield-item slots + pending shield
builds in (a) the Oct-29 resume state (work/r1/game/RESUME.GAM.user-oct29, the
state every scratch leg session boots) and (b) the newest production ring slot.

Laws (all cited, reused verbatim from scripts/r1_income_law.py):
  planet record REC=123, name-anchor walk find_records(); slot array base =
  u32[rec+0x10] + 0x88 (t33 correction = pointer law; arr indexes DIRECTLY into
  the Memory member, so BPLM target = arr + 4*i + 3 with NO further conversion);
  slot = 4B {class, itemIdx(0xff empty), word2 flags}; shield byte = slot+3.
  Pending build: word +0x50 acc, byte +0x54 item id (T271 reservation law).
  Writer law T39b: flag&8 item completion -> byte3:=0 then word2 |= (0x23|0xf)<<8.
Shield items: 18 Surface Shield, 19 Surface Mega Shield, 26 Orbital Shield,
27 Orbital Mega Shield (T271 item 4 counts).
Exit: 0 findings, 1 negative, 2 harness error.
"""
import os, struct, sys, zipfile, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import r1_income_law as IL

SHIELDS = {18, 19, 26, 27}
OCT29 = os.path.join(ROOT, "work/r1/game/RESUME.GAM.user-oct29")
OCT29_MD5 = "5b382afbb789186c3654f3cec085b2e2"
RING = os.path.join(ROOT, "work/r1/playcap/save")


def mem_from_zip(path):
    m = zipfile.ZipFile(path).read("Memory")
    pay = open(os.path.join(ROOT, "work/ascend_payload.bin"), "rb").read()
    anch = IL.build_anchors(pay)
    v, _ = IL.find_base(m, anch)
    if not v:
        return None, None
    return m, v.most_common(1)[0][0]


def scan(path, label):
    m, B = mem_from_zip(path)
    if m is None:
        print(f"[{label}] BASE-FAIL {path}")
        return 2
    turn = struct.unpack_from("<I", m, B + 0x12E10)[0]
    print(f"[{label}] {path}\n  base B=0x{B:x} turn={turn}")
    items = IL.item_table(m, B)
    if not items or not IL.names_ok(items):
        print("  ITEM TABLE names_ok FAIL (static dump artifact possible)")
        items = None
    if items:
        for k in sorted(SHIELDS):
            r = items[k]
            print(f"  item {k:2d} {r['name'][:28]:28s} flags=0x{r['flags']:04x} "
                  f"(flag8={'YES' if r['flags'] & 8 else 'no'}) cost?")
    recs = IL.find_records(m)
    print(f"  planet records: {len(recs)}")
    n_active = n_pending = 0
    for base, cells, cap, arr in recs:
        owner = m[base + 0x56]
        name = m[base + 0x24:base + 0x33].split(b"\x00")[0].decode("cp437", "replace")
        for i in range(cap):
            s = arr + 4 * i
            cls, it = m[s], m[s + 1]
            if it in SHIELDS:
                w2 = struct.unpack_from("<H", m, s + 2)[0]
                b3 = m[s + 3]
                n_active += 1
                print(f"  ACTIVE slot planet={name!r} owner={owner} idx={i} "
                      f"class={cls} item={it} word2=0x{w2:04x} byte3={b3} "
                      f"BPLM=00{ (s+3) & 0xFFFFFF:06X}")
    pend = struct.unpack_from("<H", m, 0)[0]  # placeholder unused
    # pending builds live per planet record at +0x50 acc / +0x54 item
    for base, cells, cap, arr in recs:
        it = m[base + 0x54]
        acc = struct.unpack_from("<H", m, base + 0x50)[0]
        if it != 0xFF and it != 0:
            cost = None
            if items:
                # COST u16 at item row +8; item table member idx = B+0x82bb0+0x73e40
                try:
                    cost = struct.unpack_from("<H", m, B + 0x82BB0 + 0x73E40 + it * IL.ITEM_STRIDE + 8)[0]
                except Exception:
                    cost = None
            tag = "SHIELD!" if it in SHIELDS else ""
            name = m[base + 0x24:base + 0x33].split(b"\x00")[0].decode("cp437", "replace")
            owner = m[base + 0x56]
            n_pending += 1
            print(f"  PENDING planet={name!r} owner={owner} item={it} acc={acc} {tag}")
    print(f"  totals: active-shield-slots={n_active} pending-any={n_pending}")
    return 0 if (n_active or n_pending) else 1


rc = 0
# Ring .sav zips (dosbox states) are the live-state surface (t259 law: live
# state lives in the RING, not RESUME.GAM; RESUME.GAM is the VENDOR save, raw
# data, not a zip -- measured this session).
import glob
ring = sorted(glob.glob(os.path.join(RING, "*.sav")), key=os.path.getmtime)
if ring:
    rc |= scan(ring[-1], f"ring-newest-{os.path.basename(ring[-1])}")
else:
    print("ring empty (harness error)")
    rc = 2
sys.exit(rc & 1 if rc == 1 else rc)
