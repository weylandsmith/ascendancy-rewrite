#!/usr/bin/env python3
"""r345_gate_word_census.py — RUNTIME item-table gate-word census (t345).

Question: FUN_00038f68's completion marker block is gated on the item-record
FLAG word bit 0x8 (0x3923b `mov ax,WORD[eax*8+0x73e46]` / 0x39245 `and al,0x8`
/ 0x3924c je 0x39290 skip). Which items actually take the marker path? The
static image bytes at Ghidra 0x73e40 are CODE-SHAPED (t74 law: the live table
is a heap copy), so the census must read LIVE RAM via the pointer law.

Layout (income-law.md S8 + retractions.md): item record stride 0x28 at save
member index B + 0x82BB0 + 0x73E40; FLAGS word at +6, COST word at +8.

Also prints the full 39-row flag census so the rewrite's threat-bit reading
(campaign.h shieldThreatFor flags&8 == {18,19,26,27}, orbitalThreatFor
flags&4 == {17,28,29,30}) can be checked against the runtime table verbatim.

Exit codes: 0 = census ran AND bit8 set EXACTLY on {18,19,26,27} AND every row
stable across all sampled saves; 1 = ran but premise violated (print verdict);
2 = harness error (no captures / no base vote).
"""
import argparse, glob, os, struct, sys, zipfile, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base

ITEM_BASE = 0x73E40
STRIDE = 0x28
NROWS = 39
POOLS = 0x82BB0
EXPECT_BIT8 = {18, 19, 26, 27}
EXPECT_BIT4 = {17, 28, 29, 30}


def sav_paths(run):
    return sorted(glob.glob(os.path.join(run, "save", "*.sav"))) + \
           sorted(glob.glob(os.path.join(run, "ring-final", "*.sav")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", action="append", default=None)
    ap.add_argument("--per-run", type=int, default=3)
    args = ap.parse_args()
    runs = args.run_dir or sorted(glob.glob("work/r1/r1deep-*")) + \
           ["work/r1/t340-shieldc-20261108-014705"]
    needle = open("work/ascend_payload.bin", "rb").read()
    anch = build_anchors(needle)

    votes = collections.defaultdict(collections.Counter)
    nsaves = 0
    for run in runs:
        for p in sav_paths(run)[: args.per_run]:
            try:
                mem = zipfile.ZipFile(p).read("Memory")
            except Exception:
                continue  # torn copy (autosave rewrite-in-place; STATE.md law)
            v, _ = find_base(mem, anch)
            if not v:
                continue
            B, _w = v.most_common(1)[0]
            nsaves += 1
            for idx in range(NROWS):
                off = B + POOLS + ITEM_BASE + STRIDE * idx
                if off + 8 > len(mem):
                    continue
                votes[idx][struct.unpack_from("<H", mem, off + 6)[0]] += 1

    if nsaves == 0:
        print("harness-error: no sampled save yielded a base vote")
        return 2

    print(f"saves sampled: {nsaves}")
    unstable = []
    bit8, bit4 = set(), set()
    for idx in range(NROWS):
        c = votes[idx]
        if len(c) != 1:
            unstable.append((idx, dict(c)))
            continue
        f = next(iter(c))
        if f & 0x8:
            bit8.add(idx)
        if f & 0x4:
            bit4.add(idx)
        print(f"item {idx:2d} flags=0x{f:04x} bit8={'SET' if f & 0x8 else '   '} "
              f"bit4={'SET' if f & 0x4 else '   '}")

    ok = True
    if unstable:
        ok = False
        print("UNSTABLE rows across saves:", unstable)
    if bit8 != EXPECT_BIT8:
        ok = False
        print(f"VERDICT: bit8 set on {sorted(bit8)}, expected {sorted(EXPECT_BIT8)}")
    else:
        print(f"VERDICT: marker path (gate bit8) = items {sorted(bit8)} "
              f"across {nsaves} saves (stable)")
    if bit4 != EXPECT_BIT4:
        ok = False
        print(f"VERDICT: bit4 set on {sorted(bit4)}, expected {sorted(EXPECT_BIT4)}")
    else:
        print(f"VERDICT: orbital-defence bit4 = items {sorted(bit4)} "
              f"(matches rewrite orbitalThreatFor)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
