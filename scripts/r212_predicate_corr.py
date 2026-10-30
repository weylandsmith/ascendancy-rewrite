#!/usr/bin/env python3
"""t212 — predicate correlation for dword[0x482fb] over banked campaign saves.

Static leg is CLOSED (see _wip_t212 S3/S4/S5): zero encodings of the slot
exist except the presenter's two reads; no pointer to the region exists in
RAM; no near-base [reg+disp] writer exists. The remaining question is
SEMANTIC: what does the value count? score.md S6/S8 show it tracks owned
SYSTEMS closely for most of a run but diverges (banked 23 vs systems_full 26;
oscillates 12..22 while systems_any=36/full=34 flat).

For every trusted save (t>0 or score>=1) across the r1sav-*/r1deep-* corpus +
current playcap ring, read:
  V   = dword[0x482fb]                      (the displayed count)
  P0  = player index (byte 0x7458e)
  ownP   = #stars with byte[0x13bc5+0x60k+0x15] bit (1<<P0)   (owned stars)
  ownR   = per-race owned counts (races 0..u16[0x13b98]-1)
  visP   = #stars explorer-byte? (byte +0x14 !=0)  [context]
  occ    = #stars with owner byte != 0             [context]
  planets= #planet records joined (count word at star +0x2A pointers live)
Then test candidate identities V == ownP, V == ownP-ish +/- 1, V == max_r ownR,
V == any_r ownR, and print rows where V != ownP (the divergence witnesses —
those are what the writer law must explain).
Exit 0 always (findings); 2 harness error.
"""
import glob
import os
import struct
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_slot as S

OFF = 0x82BB0
TURN = 0x12E10
STARS_WORD = 0x16145
RACE_CNT = 0x13B98
STAR_BASE = 0x13BC5
PLAYER = 0x7458E

ROOTS = sorted(glob.glob("work/r1/r1sav-*") + glob.glob("work/r1/r1deep-*"))
ROOTS.append("work/r1/playcap")


def main():
    pay = open("work/ascend_payload.bin", "rb").read()
    anch = S.anchors_cached(".", pay)
    ntrust = 0
    eq_ownP = 0
    diverge = []
    vals = {}
    for root in ROOTS:
        for f in sorted(glob.glob(os.path.join(root, "save", "*.sav")),
                        key=lambda p: os.path.getmtime(p)):
            try:
                mem = zipfile.ZipFile(f).read("Memory")
            except Exception:
                continue
            B = S.base_of(mem, anch)
            if B is None:
                continue
            P = B + OFF
            turn = struct.unpack_from("<I", mem, P + TURN)[0]
            V = struct.unpack_from("<I", mem, P + 0x482FB)[0]
            if not (turn > 0 or V >= 1):
                continue
            ntrust += 1
            p0 = mem[P + PLAYER]
            nr = struct.unpack_from("<H", mem, P + RACE_CNT)[0]
            nst = struct.unpack_from("<H", mem, P + STARS_WORD)[0]
            nr = max(1, min(nr, 8))
            own = [0] * nr
            occ = 0
            for k in range(min(nst, 60)):
                b = mem[P + STAR_BASE + 0x60 * k + 0x15]
                if b:
                    occ += 1
                for r in range(nr):
                    if b & (1 << r):
                        own[r] += 1
            ownP = own[p0] if p0 < nr else 0
            if V == ownP:
                eq_ownP += 1
            else:
                diverge.append((root, os.path.basename(f), turn, V, p0,
                                tuple(own), occ))
            vals.setdefault(V, 0)
            vals[V] += 1
    print(f"trusted saves={ntrust}  V==ownP(player owned stars): {eq_ownP} "
          f"({100*eq_ownP//max(1,ntrust)}%)")
    print(f"V value histogram: "
          + " ".join(f"{k}:{v}" for k, v in sorted(vals.items())))
    print(f"\nDIVERGENCE rows V != ownP ({len(diverge)}):")
    for d in diverge[:60]:
        root, name, turn, V, p0, own, occ = d
        print(f"  {root.split('/')[-1]}/{name} t={turn} V={V} player={p0} "
              f"own={list(own)} occupied={occ}")
    # does V ever equal ANOTHER race's count? (wrong-index hypothesis)
    hits_other = sum(1 for root, n, t, V, p0, own, occ in diverge
                     if V in own)
    print(f"\ndivergent rows where V still equals SOME race's owned count: "
          f"{hits_other}/{len(diverge)}")
    # max hypothesis
    hits_max = sum(1 for root, n, t, V, p0, own, occ in diverge
                   if V == max(own))
    print(f"divergent rows where V == max_r own: {hits_max}/{len(diverge)}")


if __name__ == "__main__":
    main()
