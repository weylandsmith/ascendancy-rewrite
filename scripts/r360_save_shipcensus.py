#!/usr/bin/env python3
"""r360_save_shipcensus.py — t360 SAVE-SIDE ship-array census (parser ground truth).

Mirrors scripts/r1_slot.py laws (READ ONLY, no behavior change):
  * slot ZIP 'Memory' member == guest RAM; base B via unanimous anchor vote
    (r1_sav_scan.py, OQ-001/011 CLOSED laws).
  * ship array: member offset B + 0x82bb0 + 0x3a095, stride 0x162,
    live count = u32[B+0x82bb0+0x43489]>>16, cap 0x6b (pership-spec.md A1/S3).
  * turn gate u32[B+0x82bb0+0x12e10] in 1..4000 before trusting (r335 law).
Census goals (ground truth for the C++ parser test t360):
  - owner attribution law: (u32@+0x54)>>16 == byte@+0x56 on LIVE rows (t273)
  - dead-slot representation: u32@+0x54 == 0xffffffff count
  - live kind set subset {1..5} (A4)
  - inventory cap/filled law: filled(+0x15e) == count(cidx!=0xFF over slots
    0..cap INCLUSIVE) (ships.md §18 PHANTOM-SLOT)
Exit 0 measured, 1 negative, 2 harness error.
"""
import os, struct, sys, zipfile, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import r1_sav_scan as SS
import r1_slot as RS

OFF = 0x82BB0
SHIP_X = 0x3A095
COUNT_X = 0x43489
TURN_X = 0x12E10
STRIDE = 0x162
CAP_SLOTS = 0x6B
RING_OFF = 0xAB
FILLED = 0x15E


def main():
    pay = RS.load_payload(ROOT)
    anch = RS.anchors_cached(ROOT, pay)
    savedir = os.path.join(ROOT, "work", "r1", "playcap", "save")
    slots = sorted(f for f in os.listdir(savedir) if f.endswith(".sav"))
    n_ok = n_rej = 0
    kind_hist = collections.Counter()
    owner_hist = collections.Counter()
    attr_ok = attr_bad = 0
    dead_rows = live_rows = 0
    cap_hist = collections.Counter()
    phantom_rows = 0
    filled_vs_ring = collections.Counter()
    examples = []
    per_save = []
    for f in slots:
        try:
            mem = zipfile.ZipFile(os.path.join(savedir, f)).read("Memory")
        except Exception as e:
            print(f"{f}: read failed {e!r}")
            continue
        B = RS.base_of(mem, anch)
        if B is None:
            print(f"{f}: no base vote")
            n_rej += 1
            continue
        turn = struct.unpack_from("<I", mem, B + OFF + TURN_X)[0]
        if not (1 <= turn <= 4000):
            print(f"{f}: turn {turn} out of gate — rejected (title slot?)")
            n_rej += 1
            continue
        n_ok += 1
        base = B + OFF + SHIP_X
        n = struct.unpack_from("<I", mem, B + OFF + COUNT_X)[0] >> 16
        n = min(n, CAP_SLOTS)
        s_live = s_dead = 0
        for k in range(n):
            r = base + k * STRIDE
            own32 = struct.unpack_from("<I", mem, r + 0x54)[0]
            race = mem[r + 0x56]
            kind = mem[r + 0x58]
            cap = struct.unpack_from("<I", mem, r + 0x15A)[0]
            filled = struct.unpack_from("<I", mem, r + FILLED)[0]
            if own32 == 0xFFFFFFFF:
                dead_rows += 1
                s_dead += 1
                continue
            live_rows += 1
            s_live += 1
            kind_hist[kind] += 1
            owner_hist[race] += 1
            if (own32 >> 16) == race:
                attr_ok += 1
            else:
                attr_bad += 1
                if len(examples) < 5:
                    examples.append((f, k, hex(own32), race))
            if cap <= 64:
                occ = sum(1 for i in range(cap + 1)
                          if mem[r + RING_OFF + 7 * i] != 0xFF)
                occ_excl = sum(1 for i in range(cap)
                               if mem[r + RING_OFF + 7 * i] != 0xFF)
                filled_vs_ring["incl_ok" if occ == filled else
                               ("excl_ok" if occ_excl == filled else "NEITHER")] += 1
                if occ != occ_excl:
                    phantom_rows += 1
                cap_hist[cap] += 1
        per_save.append((f, turn, n, s_live, s_dead))
    print(f"slots_ok={n_ok} rejected={n_rej}")
    print(f"live_rows={live_rows} dead_rows={dead_rows}")
    print(f"attr_ok=(owner>>16==+0x56) {attr_ok} attr_bad={attr_bad} ex={examples}")
    print(f"kind_hist={dict(sorted(kind_hist.items()))}")
    print(f"owner_hist={dict(sorted(owner_hist.items()))}")
    print(f"cap_hist={dict(sorted(cap_hist.items()))}")
    print(f"phantom_rows(idx==cap occupied)={phantom_rows}")
    print(f"filled_vs_ring={dict(filled_vs_ring)}")
    print("--- per save (file turn n live dead) ---")
    for p in per_save:
        print(" ", *p)
    return 0 if n_ok and attr_bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
