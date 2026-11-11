#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r284_deref.py — classify what ship+0x59 points AT (t284 contest-test law).

The producer compares ship(+0x59) against a LANE-POOL record pointer, so the
question is whether +0x59 holds lane records (or something containing one).
r284_contest_census.py found targets in the DATA SEGMENT but not congruent to
0x16147 mod 0x27, so dereference and look for the lane record SHAPE: a lane
record's first two dwords are STAR RECORD pointers (t190/t191: stride 0x27; the
race-list law proves the pool holds lane records; star records are 0x13bc5
stride 0x60 with self-handle dword@+2 >>16 == own index, t205).

Prints: distinct target -> (rel, congruence facts, first 0x27 bytes as dwords
with per-dword class annotation), and a histogram of target classes.
"""
import os, struct, sys, glob, zipfile, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_slot as SL

ROOT = "/home/hrethric/projects/ascendancy"
OFF = 0x82bb0
STAR_X, STAR_S = 0x13bc5, 0x60
LANE_X, LANE_S = 0x16147, 0x27
RACE_X, RACE_S = 0x12e16, 0x1ee


def cls(mem, B, p):
    """Classify a guest-linear pointer (POINTER LAW: X = p-(B-0x88+OFF);
    the original B+OFF version here was the t284 0x88 trap — fixed)."""
    if p == 0:
        return "null"
    rel = p - (B - 0x88 + OFF)
    if rel < 0 or rel >= 0x8cc83:
        return f"heap/other(0x{p:08x})"
    if (rel - STAR_X) % STAR_S == 0 and rel >= STAR_X:
        idx = (rel - STAR_X) // STAR_S
        sr = B + OFF + STAR_X + idx * STAR_S
        selfh = struct.unpack_from("<I", mem, sr + 2)[0] >> 16 if sr + 6 <= len(mem) else -9
        return f"STAR[{idx}]" + ("" if selfh == idx else f"!selfh{selfh}")
    if (rel - LANE_X) % LANE_S == 0 and rel >= LANE_X:
        return f"LANE[{(rel - LANE_X) // LANE_S}]"
    if (rel - RACE_X) % RACE_S == 0 and rel >= RACE_X:
        return f"RACE[{(rel - RACE_X) // RACE_S}]"
    return f"data?0x{rel:x}"


def main():
    saves = sorted(glob.glob(os.path.join(ROOT, "work/r1/playcap/save/*.sav")),
                   key=os.path.getmtime)[-4:]
    pay = SL.load_payload(ROOT)
    anchors = SL.anchors_cached(ROOT, pay)
    shapes = collections.Counter()
    shown = 0
    for path in saves:
        mem = zipfile.ZipFile(path).read("Memory")
        B = SL.base_of(mem, anchors)
        if B is None:
            continue
        base = B + OFF + SL.SHIP["x"]
        seen_t = set()
        for k in range(0x6b):
            r = base + k * SL.SHIP["stride"]
            owner = struct.unpack_from("<I", mem, r + 0x54)[0] >> 16
            if owner == 0xffffffff:
                continue
            kind = mem[r + 0x58]
            tgt = struct.unpack_from("<I", mem, r + 0x59)[0]
            if tgt == 0 or tgt in seen_t:
                continue
            seen_t.add(tgt)
            rel = tgt - (B + OFF)
            d = struct.unpack_from("<9I", mem, tgt)
            ann = [cls(mem, B, x) for x in d]
            mod_lane = (rel - LANE_X) % LANE_S
            key = (kind, tuple(a.split("[")[0] for a in ann[:4]))
            shapes[key] += 1
            if shown < 14:
                shown += 1
                print(f"{os.path.basename(path)} slot{k} own{owner} kind{kind} "
                      f"tgt=0x{tgt:08x} rel=0x{rel:x} mod39={mod_lane}")
                for i, (v, a) in enumerate(zip(d, ann)):
                    print(f"    +{i*4:<3d} 0x{v:08x}  {a}")
    print("\n== target shape histogram (kind, classes of first 4 dwords) ==")
    for k, v in shapes.most_common():
        print(f"  {v:4d}  kind={k[0]}  {k[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
