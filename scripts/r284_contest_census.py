#!/usr/bin/env python3
"""r284_contest_census.py — t284: what pointer CLASS does ship+0x59 hold?

Why this matters: the Ghidra-decoded producer FUN_00024274 (docs/re/_wip_t284.md)
tests, per candidate lane,

    ship(+0x59) == lane  &&  owner != player  &&  relation[player][owner] != 3
        -> lane CONTESTED -> V does not grow and the subtree is pruned.

That is only a lane-contest test if ship+0x59 can hold a LANE-POOL pointer.
Banked alternatives say +0x59 is an ORDER TARGET that holds star records
(0x4cd19) or planet records (ships.md:240). Measure, don't guess.

Pointer law (OQ-011 CLOSED): member addr = B + 0x82bb0 + X for data offset X.
Record bases/strides (all cited):
  star   : 0x13bc5 stride 0x60  (r1-savestate STAR TABLE LAW; +0x2 self-handle
                                  dword >>16 == own star index, t205 20/20)
  lane   : 0x16147 stride 0x27  (_wip_t190/t191; t192: 220/220 race-list
                                  pointers congruent mod 39 to this base)
  planet : 0x13bc5 + 0x60*k + ... -> ships.md:240 says a planet RECORD; the
                                  planet pool is the per-star record block, so
                                  a planet pointer is ALSO star-congruent. We
                                  therefore report star-congruent hits with the
                                  decoded star index, and count how many point
                                  at the ship's CURRENT star vs elsewhere.

Output (stdout, small): per-save classification histogram of live ships' +0x59,
plus star-index agreement stats. Exit 0 = ran with findings, 1 = no live ships.
"""
import os, struct, sys, glob, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_slot as SL

ROOT = "/home/hrethric/projects/ascendancy"
OFF = 0x82bb0
SHIP_STRIDE = 0x162
SHIP_BASE_X = 0x3a095          # r1_slot.SHIP["x"]
F_OWNER = 0x54                 # u32, owner = >>16 (t273 law)
F_ORDER = 0x59                 # the order-target dword the producer compares
F_KIND = 0x58                  # order kind byte (ships.md:903)
STAR_X, STAR_STRIDE = 0x13bc5, 0x60
LANE_X, LANE_STRIDE = 0x16147, 0x27
CAP = 0x6b


def main():
    saves = sorted(glob.glob(os.path.join(ROOT, "work/r1/playcap/save/*.sav")),
                   key=os.path.getmtime)
    if not saves:
        print("no saves"); return 1
    pay = SL.load_payload(ROOT)
    anchors = SL.anchors_cached(ROOT, pay)
    hist = collections.Counter()
    kind_hist = collections.Counter()
    star_idx_self = 0          # +0x59 -> star record of the ship's own star?
    star_total = 0
    lane_examples = []
    for path in saves[-12:]:
        try:
            import zipfile
            mem = zipfile.ZipFile(path).read("Memory")
        except Exception as e:
            print(f"skip {os.path.basename(path)}: {e}")
            continue
        B = SL.base_of(mem, anchors)
        if B is None:
            print(f"skip {os.path.basename(path)}: no base vote")
            continue
        base = B + OFF + SHIP_BASE_X
        cnt = struct.unpack_from("<I", mem, B + OFF + 0x43489)[0] >> 16
        n_live = 0
        for k in range(CAP):
            r = base + k * SHIP_STRIDE
            if r + 0x60 > len(mem):
                break
            owner = struct.unpack_from("<I", mem, r + F_OWNER)[0] >> 16
            if owner == 0xffffffff:
                continue
            n_live += 1
            kind = mem[r + F_KIND]
            kind_hist[kind] += 1
            tgt = struct.unpack_from("<I", mem, r + F_ORDER)[0]
            if tgt == 0:
                hist["null"] += 1
                continue
            # POINTER LAW (t284, docs/REFUTED-ROUTES.md): stored u32s decode as
            # X = p - (B - 0x88 + OFF). The original version of this script used
            # B + OFF and produced a FALSE "congruent to neither pool" negative.
            rel = tgt - (B - 0x88 + OFF)
            if STAR_STRIDE and (rel - STAR_X) % STAR_STRIDE == 0 and rel >= STAR_X:
                idx = (rel - STAR_X) // STAR_STRIDE
                hist["star-congruent"] += 1
                star_total += 1
                # self-handle law: dword[star_record + 2] >> 16 == star index
                sr = B + OFF + STAR_X + idx * STAR_STRIDE
                if sr + 6 <= len(mem):
                    selfh = struct.unpack_from("<I", mem, sr + 2)[0] >> 16
                    if selfh == idx:
                        star_idx_self += 1
            elif (rel - LANE_X) % LANE_STRIDE == 0 and rel >= LANE_X:
                hist["LANE-congruent"] += 1
                if len(lane_examples) < 8:
                    lane_examples.append((os.path.basename(path), k, owner, kind,
                                          f"0x{tgt:08x}", (rel - LANE_X) // LANE_STRIDE))
            else:
                hist["other"] += 1
                if hist["other"] <= 6:
                    print(f"  other: {os.path.basename(path)} slot{k} owner{owner} "
                          f"kind{kind} tgt=0x{tgt:08x} rel=0x{rel:x}")
        print(f"{os.path.basename(path)} live_count_word={cnt} scanned_live={n_live}")
    print("\n== +0x59 POINTER CLASS HISTOGRAM (live ships, last 12 saves) ==")
    for k, v in hist.most_common():
        print(f"  {k:16s} {v}")
    print(f"  order-kind bytes: {dict(sorted(kind_hist.items()))}")
    print(f"  star-congruent self-handle verified: {star_idx_self}/{star_total}")
    if lane_examples:
        print("  LANE-congruent examples (save slot owner kind ptr laneIdx):")
        for e in lane_examples:
            print("   ", e)
    else:
        print("  ZERO lane-congruent pointers in this window.")
    return 0 if hist else 1


if __name__ == "__main__":
    raise SystemExit(main())
