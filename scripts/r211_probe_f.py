#!/usr/bin/env python3
"""t211 probe F: does guest RAM hold any dword == P0 + 0x4a350 (pointer law)?
If yes, the phase-flip block 0x4a350 has a runtime binding (handler table,
t191 pattern); if no dword anywhere in the member references it, the block is
unreachable in-corpus. Static edges are already ZERO (probe_e control:
0x4b740's six t210 callers reproduce exactly)."""
import os, struct, sys, zipfile, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_slot as S

H = 136
pay = open("work/ascend_payload.bin", "rb").read()
anch = S.anchors_cached(".", pay)
cands = sorted(glob.glob("work/r1/playcap-*/*.sav", recursive=False) +
               glob.glob("work/r1/playcap/save/*.sav") +
               glob.glob("work/r1/playcap*/save/*.sav"))
print("save candidates:", len(cands))
used = 0
for path in cands:
    try:
        z = zipfile.ZipFile(path)
        m = z.read("Memory")
    except Exception:
        continue
    B = S.base_of(m, anch)
    if B is None:
        continue
    P0 = B - H
    targets = {P0 + 0x4a350: "phase-flip 0x4a350",
               P0 + 0x49f54: "travel leg 0x49f54 (expect NONE, E8-only)",
               P0 + 0x49f28: "dispatcher 0x49f28 (expect NONE if E8-only)"}
    print(f"\n-- {path} B={hex(B)} P0={hex(P0)} member={len(m)}")
    for t, label in targets.items():
        pat = struct.pack("<I", t & 0xFFFFFFFF)
        pos, start = [], 0
        while True:
            k = m.find(pat, start)
            if k < 0:
                break
            if k % 4 == 0:
                pos.append(hex(k))
            start = k + 1
        print(f"  {label}: {len(pos)} aligned dwords", pos[:8])
    used += 1
    if used >= 3:
        break
print("\nsaves examined:", used)
sys.exit(0 if used else 2)
