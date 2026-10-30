#!/usr/bin/env python3
"""t207 C-W2 — is byte[race-row + 2] a per-race CONTACT flag (dynamic) or a
static species attribute?

The witness gate 0x3a20b `cmp byte [eax*2 + 0x12fb3], 0` (eax = 0x1ee*k)
reads race-row base 0x12fb4 + 0x3dc*k, byte +0. All eight 0x12fb3 sites are
scale-2 (row stride 0x3dc) — a packed/interleaved view of the 0x1ee race-diplo
rows (t202 banked row0 base 0x12fb3, owner byte +0, ability byte +0x19d).

Prints per save (pointer law): race count, owner bytes, row[+0], row[+2]
(scalar 0x12fb4+... AND scale-form 0x12fb3+2*0x1ee*k — must agree), and the
relation matrix [0x12fd6] cell (i,j) for all race pairs — so row[+2]/[+0]
can be correlated with whether the pair has EVER been in contact
(relation state != 0 == never-contacted per t187: 0=uninitialized/never,
1=PEACE, 2=WAR, 3=ALLIANCE).

Prediction if CONTACT-flag: row[k].byte0 == 0 iff race k has no relation cell
!= 0 with anyone... more precisely the gate is indexed by ATTACKER k, so
predict byte0(k)==0 iff race k has zero contacts (never met anyone).
Exit 0 = census produced."""
import glob
import os
import struct
import struct
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_slot as S

OFF = 0x82BB0
RACE_ROW = 0x12FB4   # scale-2 form base (0x12fb3 is one byte left of it)
STATE = 0x12FD6      # relation-state matrix base (t180)
NRACES = 0x13B96


def main():
    pay = open("work/ascend_payload.bin", "rb").read()
    anch = S.anchors_cached(".", pay)
    n = 0
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
        nr = struct.unpack_from("<I", mem, M + NRACES)[0] >> 16
        rows = []
        for k in range(min(nr, 6)):
            owner = mem[M + RACE_ROW + 2 * 0x1EE * k + 0]
            b0_scalar = mem[M + 0x12FB4 + 0x1EE * k]
            b2_scalar = mem[M + 0x12FB4 + 0x1EE * k + 2]
            w1c9 = struct.unpack_from("<h", mem, M + 0x12E16 + 0x1EE * k + 0x1C9)[0]
            st = [mem[M + STATE + 0x1EE * k + j] for j in range(min(nr, 6))]
            ncontacts = sum(1 for j, v in enumerate(st) if j != k and v != 0)
            rows.append((k, owner, b0_scalar, b2_scalar, w1c9, st, ncontacts))
        if n <= 3 or n % 5 == 0:
            print(f"\n{os.path.basename(f)} nraces={nr}")
            for k, owner, b0, b2, w, st, nc in rows:
                print(f"  race{k} owner={owner} row+0={b0} row+2={b2} "
                      f"DECLARE_WAR={w} state_row={st} contacts={nc}")
    # aggregate correlation: byte0 vs contacts
    print(f"\nsaves={n}")


main()
