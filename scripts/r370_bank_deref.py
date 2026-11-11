#!/usr/bin/env python3
"""t370 — deref pass over a banked playtest ring (Memory image).

Measurements (the tl-mode census cannot do these — no Memory image):
 1. STAR COORD GRID CENSUS: star table stride 96, name-anchored
    (scripts/r1_star_table.py law; H = base - 0x1BF450 per its load_slots;
    triple at name-0x14 f32[3]). Are star triples multiples of 32? Decides
    whether an ON-32-GRID magnetron landing is compatible with the rng%200
    jitter law (docs/re/ships.md S19 T3) or refutes it.
 2. TARGET DEREF for a named ship: kind byte +0x58, +0x59 target ptr
    (guest-physical; the Memory zip IS guest linear memory). Per
    FUN_00021f58 the placement source triple is target[+0x08..+0x10] when
    EDI==target[0], else target[+0x14..+0x1c] when EDI==target[4]. Dump
    both triples + target id words + ship pos.
 3. Per-slot +0x88/+0x8c dump for the named slots (power / hull-integrity
    per pership-spec §1 — NOT 'charges'; the ring use-counter is separate).

Usage: r370_bank_deref.py DIR [NAME ...]     (default names: Guandagnini)
"""
import glob
import os
import struct
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r1_slot as S
import r1_star_table as ST


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    d = sys.argv[1]
    names_want = [n.lower() for n in sys.argv[2:]] or ["guandagnini"]
    files = sorted(glob.glob(os.path.join(d, "*.sav")), key=os.path.getmtime)
    pay = S.load_payload(os.getcwd())
    anch = S.anchors_cached(os.getcwd(), pay)
    for f in files:
        try:
            mem = zipfile.ZipFile(f).read("Memory")
        except Exception as e:
            print(f"{os.path.basename(f)} unzip {repr(e)[:60]}")
            continue
        B = S.base_of(mem, anch)
        if B is None or len(mem) < 0x90000:
            print(f"{os.path.basename(f)} base UNRESOLVED/short")
            continue
        dsc = S.read_slot(f, mem, B)
        H = B - 0x1BF450

        # 1) star grid census
        st = ST.find_star_names(mem, H)
        # find_star_names returns (rec_off_without_H, name); r1_star_table
        # .check adds H at every read (p = B + H) — do the same here.
        grid = {"on32": 0, "off32": 0, "bad": 0}
        xyz_by_name = {}
        recs = []
        for p0, nm in st:
            rec_p = p0 + H
            try:
                xyz = struct.unpack_from("<3f", mem, rec_p + ST.S_XYZ)
            except Exception:
                grid["bad"] += 1
                continue
            recs.append((nm, xyz))
            xyz_by_name[nm.lower()] = tuple(round(v, 1) for v in xyz)
            if all(abs(c / 32.0 - round(c / 32.0)) < 1e-6 for c in xyz):
                grid["on32"] += 1
            else:
                grid["off32"] += 1
        print(f"== {os.path.basename(f)} t{dsc['turn']}  stars={len(recs)} "
              f"on32={grid['on32']} off32={grid['off32']} bad={grid['bad']}")
        off = [(nm, tuple(round(v, 1) for v in xyz)) for nm, xyz in recs
               if not all(abs(c / 32.0 - round(c / 32.0)) < 1e-6 for c in xyz)]
        for nm, t in off[:10]:
            print(f"   OFF-GRID star {nm} {t}")

        # 2/3) named ship records
        base, n = S.ship_array_law(mem, B)
        for k in range(n):
            rb = base + k * 0x162
            nm = mem[rb + 0x34:rb + 0x34 + 20].split(b"\x00")[0].decode("latin-1", "replace")
            if nm.lower() not in names_want:
                continue
            kind, hi = mem[rb + 0x58], mem[rb + 0x59]
            tgt = struct.unpack_from("<I", mem, rb + 0x59)[0]
            pos = tuple(round(v, 1) for v in struct.unpack_from("<3f", mem, rb + 0x9e))
            line = (f"  s{k} {nm}: kind={kind}/{hex(hi)} tgt={hex(tgt)} "
                    f"pos={pos} +0x88={struct.unpack_from('<I',mem,rb+0x88)[0]} "
                    f"+0x8c={struct.unpack_from('<I',mem,rb+0x8c)[0]} "
                    f"type={mem[rb+0x67]} pay={hex(struct.unpack_from('<I',mem,rb+0x68)[0])} "
                    f"trip6c={tuple(round(v,1) for v in struct.unpack_from('<3f',mem,rb+0x6c))}")
            print(line)
            # OQ-011 POINTER LAW: runtime u32 = P0 + payload-file-offset =>
            # guest-linear addr = runtime - P0, P0 = B - H = 0x1BF450.
            # (Corroborated live this session: +0x59 tgt 0x255c85 - 0x1BF450
            #  = star record k=7 name slot at NAME_ANCHOR_HINT+7*96.)
            P0 = 0x1BF450
            ga = tgt - P0
            if 0 < ga < len(mem) - 0x20:
                w0, w4 = struct.unpack_from("<II", mem, ga)
                t8 = tuple(round(v, 1) for v in struct.unpack_from("<3f", mem, ga + 0x08))
                t14 = tuple(round(v, 1) for v in struct.unpack_from("<3f", mem, ga + 0x14))
                nm_at = mem[ga:ga + 18].split(b"\x00")[0].decode("latin-1", "replace")
                print(f"      guest={hex(ga)} name?'{nm_at}' tgt[0]={hex(w0)} tgt[4]={hex(w4)} [+8]={t8} [+0x14]={t14}")
                for snm, sxyz in xyz_by_name.items():
                    if sxyz in (t8, t14):
                        which = "t8" if sxyz == t8 else "t14"
                        print(f"      == star {snm} coords MATCH at {which}")
                        sxyz_raw = xyz_by_name[snm]
                        jitter = tuple(round(p - s + (0 if which == "t14" else 0), 1)
                                       for p, s in zip(pos, sxyz_raw))
                        print(f"      pos-star(=jitter+200y) {jitter}")
        return 0
    print("no readable slot")
    return 1


if __name__ == "__main__":
    sys.exit(main())
