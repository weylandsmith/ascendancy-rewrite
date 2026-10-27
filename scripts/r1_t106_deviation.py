#!/usr/bin/env python3
"""r1_t106_deviation.py — census the +0x55 SEED-LAW deviation set (OQ-016).

Seed law [CLOSED law, income-law.md S10/T33]:
    WORD[rec+0x55] == NONBARREN(surface cells)//3 + 5
holds 71070/72066 (98.62%) on the corrected +0x88 slot array; residual is
signed -17..+7 and attributed "[inferred] scenario/preset-row path".

This tool characterises the residual so the attribution can be adjudicated:
  L1 per-(run,save,planet) row: d = r55 - (nb//3+5) with the SAVE's own cell
     count, plus generator inputs the save DOES keep (+0x14 size class,
     +0x18 cells, +0x1a slot capacity, +0x16 weight row, owner +0x57).
  L2 deviation-set shape: is it a fixed world-NAME set (authored scenario) or
     spread across names (per-planet draw)? Correlate with +0x16 row.
  L3 count-convention sweep on the deviating subset: does d fall out of
     counting a different cell set (barren cells later rock-bit |8 @0x37f4d,
     ring cells forced class 1 @0x37f0e, capacity-window cells) rather than
     from a preset source?

Exit 0 always (measurement tool, not a threshold gate).
Usage: r1_t106_deviation.py [--runs 'work/r1/*'] [--all-saves] [--out TSV]
"""
import argparse, collections, glob, os, struct as st, sys, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_income_law as IL
from r1_sav_scan import build_anchors, find_base

NAME_AT = 0x24
# 11 preset weight rows measured at runtime 0x744f4 (income-law S10)
ROWS = [[100, 0, 0, 0], [50, 2, 2, 2], [20, 3, 5, 3], [0, 3, 20, 3],
        [40, 10, 2, 2], [20, 20, 2, 2], [40, 2, 2, 10], [20, 3, 3, 20],
        [40, 10, 10, 10], [20, 15, 15, 15], [0, 33, 34, 33]]


def planet_rows(m):
    """Dict rows via the proven name-anchor walk (IL.find_records)."""
    out = []
    for base, cells, cap, arr in IL.find_records(m):
        name = m[base + NAME_AT:base + NAME_AT + 30].split(b"\x00")[0] \
               .decode("cp437", "replace").strip()
        w = [m[arr + i * 4] for i in range(cap)]
        surf = w[:cells]
        nb = sum(1 for c in surf if (c & 0xF) != 0)
        out.append({
            "name": name, "base": base,
            "size": st.unpack_from("<H", m, base + 0x14)[0],
            "cells": cells, "cap": cap,
            "row": st.unpack_from("<H", m, base + 0x16)[0],
            "owner": m[base + 0x57],
            "r55": st.unpack_from("<H", m, base + 0x55)[0],
            "nb": nb,
            "nb_no8": sum(1 for c in surf if c not in (0, 8)),
            "nb_clean": sum(1 for c in surf if not (c & 8)),
            "nz_cap": sum(1 for c in w if c != 0),
            "one_cap": sum(1 for c in w if c == 1),
            "rock": sum(1 for c in surf if c & 8),
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="work/r1/*")
    ap.add_argument("--all-saves", action="store_true",
                    help="every save in the run (default: first save only)")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    anch = build_anchors(open(IL.PAY, "rb").read())
    rows = []          # dicts + run/save tags
    per_run = []
    for run in sorted(glob.glob(os.path.join(ROOT, args.runs))):
        src = os.path.join(run, "save")
        if not os.path.isdir(src):
            continue
        svs = sorted(glob.glob(os.path.join(src, "*.sav")),
                     key=os.path.getmtime)
        if not svs:
            continue
        use = svs if args.all_saves else svs[:1]
        for f in use:
            try:
                m = zipfile.ZipFile(f).read("Memory")
            except Exception:
                continue
            v, _ = find_base(m, anch)
            if not v:
                continue
            pl = planet_rows(m)
            if not pl:
                continue
            dev = 0
            for p in pl:
                p["run"] = os.path.basename(run)
                p["save"] = os.path.basename(f)
                p["d"] = p["r55"] - (p["nb"] // 3 + 5)
                if p["d"] != 0:
                    dev += 1
                rows.append(p)
            per_run.append((os.path.basename(run), os.path.basename(use[0]),
                            len(pl), dev, len(use)))

    n = len(rows)
    dev = [p for p in rows if p["d"] != 0]
    print(f"samples={n} deviating={len(dev)} "
          f"({100.0*len(dev)/max(1,n):.2f}%)")

    print("\n-- d histogram (deviating only) --")
    h = collections.Counter(p["d"] for p in dev)
    for k in sorted(h):
        print(f"  d={k:+3d}  {h[k]:5d}")

    print("\n-- deviation rate by size class / cells --")
    by = collections.defaultdict(lambda: [0, 0])
    for p in rows:
        by[(p["size"], p["cells"])][0] += 1
        if p["d"]:
            by[(p["size"], p["cells"])][1] += 1
    for k in sorted(by):
        tot, dv = by[k]
        print(f"  size={k[0]} cells={k[1]:3d}  n={tot:6d} dev={dv:5d} "
              f"{100.0*dv/tot:6.2f}%  pred range 5..{k[1]//3+5}")

    print("\n-- deviation rate by recorded +0x16 row --")
    byr = collections.defaultdict(lambda: [0, 0])
    for p in rows:
        byr[p["row"]][0] += 1
        if p["d"]:
            byr[p["row"]][1] += 1
    for k in sorted(byr):
        tot, dv = byr[k]
        w = ROWS[k] if 0 <= k < 11 else None
        print(f"  row={k:3d} n={tot:6d} dev={dv:5d} {100.0*dv/tot:6.2f}%  "
              f"weights={w}")

    print("\n-- deviation rate by owner --")
    byo = collections.defaultdict(lambda: [0, 0])
    for p in rows:
        byo[p["owner"]][0] += 1
        if p["d"]:
            byo[p["owner"]][1] += 1
    for k in sorted(byo):
        tot, dv = byo[k]
        print(f"  owner=0x{k:02x} n={tot:6d} dev={dv:5d} {100.0*dv/tot:6.2f}%")

    print("\n-- per-run (first save): planets, deviating --")
    for r in per_run:
        print(f"  {r[0]:34s} {r[1]:9s} planets={r[2]:4d} dev={r[3]:4d} "
              f"{100.0*r[3]/max(1,r[2]):6.2f}% (nsaves_used={r[4]})")

    names_all = collections.Counter(p["name"] for p in rows)
    names_dev = collections.Counter(p["name"] for p in dev)
    print(f"\n-- name-set shape -- distinct names={len(names_all)} "
          f"names with >=1 deviation={len(names_dev)}")
    always = sorted(k for k, v in names_all.items()
                    if names_dev.get(k, 0) == v and v >= 3)
    never = sorted(k for k in names_all if k not in names_dev)
    print(f"  names deviating in EVERY sample (n>=3): {len(always)}")
    print(f"    {always[:50]}")
    print(f"  names never deviating: {len(never)}  {never[:50]}")
    print("  top deviation-count names (dev/total, d-histogram):")
    for k, v in names_dev.most_common(30):
        ds = collections.Counter(p["d"] for p in dev if p["name"] == k)
        print(f"    {k:22s} {v:5d}/{names_all[k]:5d}  {dict(sorted(ds.items()))}")

    print("\n-- count-convention models: agreement on deviating subset --")
    defs = [
        ("M1 nb surface non-zero (law)", lambda p: p["nb"]),
        ("M2 nb excl word==8 (barren|rock)", lambda p: p["nb_no8"]),
        ("M3 non-zero over full slotcap window", lambda p: p["nz_cap"]),
        ("M4 nb excl any rock-bit cell", lambda p: p["nb_clean"]),
        ("M5 class==1 over full slotcap window", lambda p: p["one_cap"]),
    ]
    for nm, fn in defs:
        agree = sum(1 for p in rows if fn(p) // 3 + 5 == p["r55"])
        agree_d = sum(1 for p in dev if fn(p) // 3 + 5 == p["r55"])
        print(f"  {nm:38s} ALL {agree:6d}/{n:6d}={100.0*agree/max(1,n):6.2f}%  "
              f"DEV-subset {agree_d:5d}/{len(dev):5d}="
              f"{100.0*agree_d/max(1,len(dev)):6.2f}%")

    print("\n-- deviating-planets-per-save histogram --")
    per_save_dev = collections.Counter((p["run"], p["save"]) for p in dev)
    tot_save = collections.Counter((p["run"], p["save"]) for p in rows)
    dist = collections.Counter(per_save_dev.get(k, 0) for k in tot_save)
    print(" ", dict(sorted(dist.items())))

    if args.out:
        cols = ["run", "save", "name", "size", "cells", "cap", "row", "owner",
                "base", "r55", "nb", "d", "rock", "nb_no8", "nb_clean",
                "nz_cap", "one_cap"]
        with open(args.out, "w") as f:
            f.write("\t".join(cols) + "\n")
            for p in rows:
                f.write("\t".join(str(p[c]) for c in cols) + "\n")
        print(f"\nwrote {args.out} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
