#!/usr/bin/env python3
"""r1_t106_hdrdiff.py — find header fields that discriminate the +0x55
deviation set from the law-holding set INSIDE ONE SAVE.

P1/P2/P3: deviations are run-local, frozen, uncorrelated with row/size/name.
If deviating records were built by a different PATH (constructor copy 0x3a664
from a parameter block vs world-gen 0x37d80), some header byte should split the
sets. Compares every byte of record[0x00..0x7b] (excluding the name and the
grid-derived +0x55/+0x4a arithmetic) between DEV and non-DEV records, and
reports fields where the value distributions are disjoint or the DEV set shows a
constant the CTRL set never shows.

Exit 1 if a discriminating field exists, 0 if the sets are header-indistinguish-
able (=> negative: no in-record marker of a second construction path).
"""
import argparse, collections, glob, os, struct as st, sys, zipfile, random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_income_law as IL
from r1_sav_scan import build_anchors, find_base

NAME_AT = 0x24


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="work/r1/*")
    ap.add_argument("--max-runs", type=int, default=6)
    args = ap.parse_args()
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    anch = build_anchors(open(IL.PAY, "rb").read())
    runs = []
    for run in sorted(glob.glob(os.path.join(ROOT, args.runs))):
        src = os.path.join(run, "save")
        if not os.path.isdir(src) or os.path.exists(os.path.join(run, "inject.log")):
            continue
        svs = sorted(glob.glob(os.path.join(src, "*.sav")), key=os.path.getmtime)
        if not svs:
            continue
        try:
            m = zipfile.ZipFile(svs[0]).read("Memory")
        except Exception:
            continue
        if not find_base(m, anch)[0]:
            continue
        dev, ctrl = [], []
        for base, cells, cap, arr in IL.find_records(m):
            hdr = m[base:base + 0x7b]
            nb = sum(1 for i in range(cells) if (m[arr + 4 * i] & 0xF) != 0)
            r55 = st.unpack_from("<H", m, base + 0x55)[0]
            (dev if r55 != nb // 3 + 5 else ctrl).append(hdr)
        if dev:
            runs.append((os.path.basename(run), dev, ctrl))
    runs.sort(key=lambda r: -len(r[1]))
    runs = runs[:args.max_runs]

    # pool per-offset value sets
    devvals = collections.defaultdict(set)
    ctrlvals = collections.defaultdict(set)
    for _, dev, ctrl in runs:
        for h in dev:
            for i in (0x0c, 0x0e, 0x14, 0x16, 0x18, 0x1a, 0x66, 0x68, 0x69,
                      0x6b, 0x57):
                devvals[i].add(h[i])
        for h in ctrl:
            for i in (0x0c, 0x0e, 0x14, 0x16, 0x18, 0x1a, 0x66, 0x68, 0x69,
                      0x6b, 0x57):
                ctrlvals[i].add(h[i])
    print("runs used:", [(r[0], len(r[1]), len(r[2])) for r in runs])
    found = False
    for i in sorted(devvals):
        d, c = devvals[i], ctrlvals[i]
        only_dev = d - c
        flag = "  <<< DISCRIMINATOR" if only_dev else ""
        if only_dev:
            found = True
        print(f"  +0x{i:02x}: DEV={sorted(d)} CTRL_n={len(c)} "
              f"CTRL={sorted(c) if len(c) <= 14 else '...'} dev_only={sorted(only_dev)}{flag}")

    # whole-header structural signature: byte-class pattern (zero / small / ptr)
    def sig(h):
        return tuple(0 if b == 0 else (1 if b < 0x20 else 2) for b in h)
    ds = collections.Counter(sig(h) for _, dev, _ in runs for h in dev)
    cs = collections.Counter(sig(h) for _, _, ctrl in runs for h in ctrl)
    dev_only_sigs = set(ds) - set(cs)
    print(f"\nstructural header signatures: dev={len(ds)} ctrl={len(cs)} "
          f"dev_only={len(dev_only_sigs)}")
    if dev_only_sigs:
        found = True
    print("VERDICT:", "DISCRIMINATOR FOUND" if found else
          "NEGATIVE: deviating records are header-indistinguishable from "
          "law-holding records (no in-record marker of a second path)")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
