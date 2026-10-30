#!/usr/bin/env python3
"""t207 C-W2b — the capture-path CEILING operands, measured on 20 saves.

CORRECTED ALGEBRA (the compiler splits 494 = (32x - x)*8 - x = 247x, read
with scale 2): 0x3a20b `cmp byte [eax*2 + 0x12fb3], 0` with eax=247*a lands
on diplo-row(a) + 0x19d  (0x12fb3 = row0 + 0x19d) — the t202 ABILITY byte.
0x3a27c [eax+0x12fdf], eax=494*v -> row(v)+0x1c9 = DECLARE_WAR threshold
(§8 map). 0x3a283 [edx+0x12fc8], edx=494*v+2*a -> row(v)+0x1b2+2*a = the
ATTITUDE cell a->v (diplomacy.md S7 law). NO third-party matrix needed for
this site: the capture path reads the ATTITUDE after the handler penalty and
slams it to DECLARE-10 when it is STILL ABOVE the line (invasion guarantees
the victim's t180 declare-war chooser fires).

Measures per save (pointer law):
 A1 ability byte row(a)+0x19d distribution (0 -> witness -1 -> forced
    invasion result 1 per 0x3a34c).
 A2 per ordered pair (a,v): DECL(v) vs attitude[a->v]; count PAIRS WITH
    attitude > DECL (these are the cells the slam would hit on an invasion).
 A3 states row (0x1c0+t) alongside for attribution (at-war pairs CANNOT
    reach the slam: the handler returns 0 and 0x3a25d skips).
 A4 honest-negative scan: any ship (unit table 0x3a095 stride 0x162, rows
    with self-handle dword[+2]>>16==k) carrying gizmo slot word==0x49
    (Invasion Module, row 73) — corpus witnesses for invasion capability.
Exit 0 = census produced."""
import glob
import os
import struct
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_slot as S

OFF = 0x82BB0


def main():
    pay = open("work/ascend_payload.bin", "rb").read()
    anch = S.anchors_cached(".", pay)
    n = 0
    tot_pairs = slam_pairs = atwar_pairs = 0
    ab_map = {}
    inv_saves = 0
    for f in sorted(glob.glob("work/r1/playcap/save/*.sav")):
        try:
            mem = zipfile.ZipFile(f).read("Memory")
        except Exception:
            continue
        B = S.base_of(mem, anch)
        if B is None:
            continue
        n += 1
        M = B + OFF
        nr = struct.unpack_from("<I", mem, M + 0x13B96)[0] >> 16
        for a in range(nr):
            ab = mem[M + 0x12E16 + 494 * a + 0x19D]
            ab_map[ab] = ab_map.get(ab, 0) + 1
            for v in range(nr):
                if a == v:
                    continue
                row = M + 0x12E16 + 494 * v
                decl = struct.unpack_from("<h", mem, row + 0x1C9)[0]
                att = struct.unpack_from("<h", mem, row + 0x1B2 + 2 * a)[0]
                state = mem[row + 0x1C0 + a]
                tot_pairs += 1
                if state == 2:
                    atwar_pairs += 1
                    continue
                if att > decl:
                    slam_pairs += 1
        # A4 invasion module witnesses (ship record = unit table 0x3a095 stride
        # 0x162; validity: owner byte +0x57? ships use +0x54 handle; use
        # slot-count [rec+0x15a] bound + owner idx < nraces filter)
        found = 0
        for k in range(400):
            base = M + 0x3A095 + 0x162 * k
            if base + 0x162 > len(mem):
                break
            own = struct.unpack_from("<I", mem, base + 0x54)[0] >> 16
            cnt = struct.unpack_from("<I", mem, base + 0x15A)[0]
            if own >= nr or cnt == 0 or cnt > 64:
                continue
            for i in range(cnt):
                if mem[base + 0xAB + 7 * i] == 0x49:
                    found += 1
                    break
        if found:
            inv_saves += 1
        if n <= 2 or n == 20:
            r0 = M + 0x12E16
            print(f"{os.path.basename(f)} nr={nr} race0 ab={mem[r0+0x19d]} "
                  f"DECL0={struct.unpack_from('<h',mem,r0+0x1C9)[0]} "
                  f"att01={struct.unpack_from('<h',mem,r0+0x1B2+2)[0]} "
                  f"states0={[mem[r0+0x1C0+j] for j in range(nr)]} "
                  f"inv_mod_ships={found}")
    print(f"\nsaves={n} pairs={tot_pairs} at_war_pairs={atwar_pairs}")
    print(f"non-war pairs with attitude>DECL (slam-eligible): {slam_pairs}")
    print("ability byte distribution:", dict(sorted(ab_map.items())))
    print(f"saves with >=1 invasion-module ship: {inv_saves}/{n}")


main()
