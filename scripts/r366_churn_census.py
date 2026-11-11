#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r366_churn_census.py - t366 WRITE-SIDE grounding: which ship-record bytes
churn across adjacent autosaves at the SAME turn (idle ring rotation), and
which across a TURN BOUNDARY (bank-t261 drive corpus)? Grounds the
durable/transient honest note (STATE t365 claim: stance/gate/activeSlot are
engagement-transient; measure what the save actually varies).

Laws (cited, mirrored from r360/r256c):
  * member offset = B + 0x82bb0 + 0x3a095, stride 0x162, cap 0x6b (spec A1/S1).
  * base B via unanimous anchor vote (r1_sav_scan; find_base -> (votes, pos)).
  * adjacent pairing guard: prev_turn in {turn, turn-1} AND mtime gap <= 120s
    (selfplay.md t273 harness bug (2), pership-spec S5).
Exit 0 measured, 2 harness error.
"""
import os, struct, sys, zipfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import r1_sav_scan as SS
import r1_slot as RS

OFF = 0x82BB0
SHIP_X = 0x3A095
STRIDE = 0x162
CAP = 0x6B
TURN_X = 0x12E10

# Named fields from rewrite/src/formats/shipsave.h Record (offset, len, name)
FIELDS = [
    (0x00, 4, "weaponLevel"), (0x04, 4, "shieldLevel"), (0x08, 4, "laneStepX"),
    (0x0c, 4, "laneStepZ"), (0x10, 4, "driveTotal"), (0x14, 4, "hullBaseDrive"),
    (0x18, 4, "powerMax"), (0x1c, 4, "cat2PowerCarry"), (0x20, 4, "scannerTotal"),
    (0x24, 4, "specialCount"), (0x28, 4, "targetSlot"), (0x31, 1, "playerDesign"),
    (0x54, 4, "ownerHandle"), (0x56, 1, "ownerRace"), (0x58, 1, "orderKind"),
    (0x59, 4, "orderTarget"), (0x5d, 1, "actEnum"), (0x5e, 4, "actTarget"),
    (0x62, 1, "resolverFlag+gate"), (0x63, 4, "activeSlot/slotPtr"),
    (0x67, 1, "orderType"), (0x68, 4, "orderPayload"),
    (0x6c, 12, "absTriple"), (0x88, 4, "power"), (0x8c, 4, "integrity"),
    (0x90, 4, "shields"), (0x94, 4, "moves"), (0x98, 4, "maxIntegrity"),
    (0x9c, 2, "statusFlags"), (0x9e, 12, "pos"), (0xaa, 1, "hullKind"),
    (0xab, 0xaf, "ring+tail(0xab..0x159)"), (0x15a, 4, "invCap"),
    (0x15e, 4, "filled"),
]


def load(path, anch):
    try:
        mem = zipfile.ZipFile(path).read("Memory")
    except Exception as e:
        return None
    B = RS.base_of(mem, anch)
    if B is None:
        return None
    turn = struct.unpack_from("<I", mem, B + OFF + TURN_X)[0]
    if not (1 <= turn <= 4000):
        return None
    return (mem, B, turn, B + OFF + SHIP_X)


def census(pairs, label):
    field_churn = {name: 0 for _, _, name in FIELDS}
    byte_churn = {}
    n_live_pairs = 0
    for (f1, m1, a1), (f2, m2, a2) in pairs:
        n_live_pairs += 1
        for k in range(CAP):
            r1, r2 = a1 + k * STRIDE, a2 + k * STRIDE
            for foff, flen, fname in FIELDS:
                if m1[r1 + foff:r1 + foff + flen] != m2[r2 + foff:r2 + foff + flen]:
                    field_churn[fname] += 1
            for off in range(STRIDE):
                if m1[r1 + off] != m2[r2 + off]:
                    byte_churn[off] = byte_churn.get(off, 0) + 1
    print(f"\n== {label}: {n_live_pairs} adjacent pairs x {CAP} slots ==")
    print("FIELD: churn_count  (0 = byte-durable across these pairs)")
    for _, _, name in FIELDS:
        print(f"  {name:24s} {field_churn[name]}")
    if byte_churn:
        print("RAW churned offsets (per-slot pair counts):")
        for off in sorted(byte_churn):
            print(f"  +0x{off:03x}: {byte_churn[off]}")


def main():
    pay = RS.load_payload(ROOT)
    anch = SS.build_anchors(pay)

    # (A) Production ring, SAME-turn adjacent pairs (idle churn class)
    savedir = os.path.join(ROOT, "work", "r1", "playcap", "save")
    slots = sorted((f for f in os.listdir(savedir) if f.endswith(".sav")),
                   key=lambda f: os.path.getmtime(os.path.join(savedir, f)))
    loaded = []
    for f in slots:
        r = load(os.path.join(savedir, f), anch)
        if r:
            loaded.append((f,) + r)
    turns = sorted(set(x[3] for x in loaded))
    print(f"ring: loaded {len(loaded)}/{len(slots)}, turns {turns}")
    same_turn, boundary = [], []
    for i in range(len(loaded) - 1):
        f1, m1, B1, t1, a1 = loaded[i]
        f2, m2, B2, t2, a2 = loaded[i + 1]
        gap = abs(os.path.getmtime(os.path.join(savedir, f2)) -
                  os.path.getmtime(os.path.join(savedir, f1)))
        if gap > 120:
            continue  # t273 guard (2)
        if t1 == t2:
            same_turn.append(((f1, m1, a1), (f2, m2, a2)))
        elif t2 == t1 + 1:
            boundary.append(((f1, m1, a1), (f2, m2, a2)))
    census(same_turn, "RING same-turn (idle) pairs")
    census(boundary, "RING turn-boundary pairs")

    # (B) t340 scratch drive ring-final: REAL turn advances t1086..t1093
    drive = os.path.join(ROOT, "work", "r1", "t340-shieldc-20261108-014705",
                         "ring-final")
    if os.path.isdir(drive):
        dslots = sorted((f for f in os.listdir(drive) if f.endswith(".sav")),
                        key=lambda f: os.path.getmtime(os.path.join(drive, f)))
        dl = []
        for f in dslots:
            r = load(os.path.join(drive, f), anch)
            if r:
                dl.append((f,) + r)
        print(f"\ndrive(ring-final): loaded {len(dl)}/{len(dslots)}, "
              f"turns {sorted(set(x[3] for x in dl))}")
        dpairs = []
        for i in range(len(dl) - 1):
            f1, m1, B1, t1, a1 = dl[i]
            f2, m2, B2, t2, a2 = dl[i + 1]
            gap = abs(os.path.getmtime(os.path.join(drive, f2)) -
                      os.path.getmtime(os.path.join(drive, f1)))
            if gap > 120 or t2 not in (t1, t1 + 1):
                continue
            dpairs.append(((f1, m1, a1), (f2, m2, a2)))
        census(dpairs, "DRIVE ring-final adjacent pairs (advancing corpus)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
