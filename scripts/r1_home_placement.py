#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r1_home_placement.py — OQ-016 home-placement sub-law (T40).
METHOD: earliest-mtime save per DISTINCT world (world identity = tuple of
planet name+row+cap from find_records; t31 law that a game's slot ring
shares one world). For every owned planet in that first save (owner byte
+0x12 != 0xFF): active surface/orbital item ids, pop, cap (+0x4a),
capBase seed (+0x55) vs (nonbarren//3+5), terrain row +0x16. Output:
per-world home item lists to diff against rewrite ctor seeding
(campaign.cpp Factory+Laboratory+Shipyard documented default)."""
import sys, glob, os, struct as st, zipfile, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base
import r1_income_law as IL


def world_state(m):
    """(name, row, capword) tuple tuple = world identity (t31 law)."""
    ids = []
    for rec in IL.find_records(m):
        rb = rec[0]
        name = m[rb + 0x24:m.index(b"\x00", rb + 0x24)].decode("cp437", "replace")
        row = st.unpack_from("<H", m, rb + 0x16)[0]
        cap = st.unpack_from("<H", m, rb + 0x1a)[0]
        ids.append((name, row, cap))
    return tuple(ids)


def snap_first(m, items):
    out = []
    for rec in IL.find_records(m):
        rb = rec[0]
        owner = m[rb + 0x57]  # banked OWNER byte (t40 fix: +0x12 was a stale guess and matched almost nothing)
        if owner == 0xFF:
            continue
        ptr = st.unpack_from("<I", m, rb + 0x10)[0] + 0x88
        surf = st.unpack_from("<H", m, rb + 0x18)[0]
        capw = st.unpack_from("<H", m, rb + 0x1a)[0]
        if not (0 <= ptr and ptr + capw * 4 <= len(m)):
            continue
        act = []
        for k in range(capw):
            it = m[ptr + 4 * k + 1]
            if it == 0xFF or it >= IL.N_ITEMS:
                continue
            if st.unpack_from("<H", m, ptr + 4 * k + 2)[0] & 1:
                nm = items[it]["name"]
                kind = "surf" if k < surf else "orb"
                act.append((k, it, nm, kind))
        cap = st.unpack_from("<H", m, rb + 0x4a)[0]
        sur = [m[ptr + 4 * k] for k in range(surf)]
        nb = sum(1 for c in sur if c != 0 and c != 8)
        first_nr = next((i for i, c in enumerate(sur) if c not in (0, 8)), -1)
        cb_slots = [k for (k, it, nm, kd) in act if nm == "Colony Base"]
        name = m[rb + 0x24:m.index(b"\x00", rb + 0x24)].decode("cp437", "replace")
        out.append(dict(
            owner=owner, name=name, cells=surf, buildable=nb,
            cb_slots=cb_slots, cb_cell=[sur[k] for k in cb_slots if k < surf],
            cb_orb=sum(1 for k in cb_slots if k >= surf), first_nr=first_nr,
            pop=st.unpack_from("<H", m, rb + 0x42)[0],
            cap=st.unpack_from("<H", m, rb + 0x4a)[0],
            seed=st.unpack_from("<H", m, rb + 0x55)[0],
            seedlaw=nb // 3 + 5,
            row=st.unpack_from("<H", m, rb + 0x16)[0],
            surf=surf, items=act, f66=m[rb + 0x66]))
    return out


def main():
    pay = open("work/ascend_payload.bin", "rb").read()
    anch = build_anchors(pay)
    worlds = {}
    for run in sorted(glob.glob("work/r1/*")):
        if not os.path.isdir(run):
            continue
        files = sorted(glob.glob(run + "/save/*.sav"), key=os.path.getmtime)
        for f in files:
            try:
                m = zipfile.ZipFile(f).read("Memory")
            except Exception:
                continue
            votes, _ = find_base(m, anch)
            if not votes:
                continue
            base = votes.most_common(1)[0][0]
            items = IL.item_table(m, base)
            if items is None or not IL.names_ok(items):
                continue
            wid = world_state(m)
            if not wid:
                continue
            # keep EARLIEST save per world identity across the corpus
            if wid not in worlds or os.path.getmtime(f) < worlds[wid][1]:
                worlds[wid] = ((run, f), os.path.getmtime(f), items)
    print(f"distinct worlds: {len(worlds)}")
    home_item_sets = collections.Counter()
    n_home = 0
    for wid, ((run, f), _, items) in sorted(worlds.items(), key=lambda kv: kv[1][0][0]):
        m = zipfile.ZipFile(f).read("Memory")
        homes = snap_first(m, items)
        rows = []
        for h in homes:
            n_home += 1
            names = tuple(sorted(set(nm for _, _, nm, _ in h["items"])))
            home_item_sets[names] += 1
            ok = "OK" if h["pop"] <= h["cap"] else "!"
            seedok = "seed==" if h["seed"] == h["seedlaw"] else f"seed{h['seed']}vs{h['seedlaw']}"
            rows.append(f"    {h['name']:16s} own={h['owner']} pop={h['pop']} cap={h['cap']} "
                        f"{ok} {seedok} cells={h['cells']} bld={h['buildable']} fnr={h['first_nr']} "
                        f"cb={h['cb_slots']} cbcell={h['cb_cell']} cborb={h['cb_orb']} "
                        f"items={[(k, nm, kd) for k, _, nm, kd in h['items']]}")
        print(f"  {os.path.basename(run)} {os.path.basename(f)} ({len(homes)} owned)")
        for r in rows:
            print(r)
    print("\nhome count per (world, owner):")
    per = collections.Counter()
    cb_idx_ratio = []
    cb_on_barren = collections.Counter()
    for wid, ((run, f), _, items) in worlds.items():
        m = zipfile.ZipFile(f).read("Memory")
        for h in snap_first(m, items):
            per[(wid, h["owner"])] += 1
            for k in h["cb_slots"]:
                cb_idx_ratio.append((k, h["cells"], h["buildable"]))
    hist = collections.Counter(per.values())
    print(f"  homes-per-owner histogram: {dict(hist)}  (world,owner) pairs: {len(per)}")
    ks = [k for k, c, b in cb_idx_ratio if k < c]
    print(f"  CB surface slots n={len(ks)} orbital={len(cb_idx_ratio)-len(ks)}")
    if ks:
        import statistics
        print(f"  CB slot index: min={min(ks)} max={max(ks)} mean={statistics.mean(ks):.1f}")
        r = [k / c for (k, c, b) in cb_idx_ratio if k < c and c]
        print(f"  CB slot / cells ratio: min={min(r):.3f} max={max(r):.3f} mean={statistics.mean(r):.3f}")
        # where does the CB cell sit relative to the first non-rock cell?
        off = [k - h["first_nr"] for wid, ((run, f), _, items) in worlds.items()
               for h in snap_first(zipfile.ZipFile(f).read("Memory"), items)
               for k in h["cb_slots"] if k < h["cells"]]
        print(f"  CB slot - first-non-rock offset hist: {dict(sorted(collections.Counter(off).items()))}")
        cls = collections.Counter(c for wid, ((run, f), _, items) in worlds.items()
                                  for h in snap_first(zipfile.ZipFile(f).read("Memory"), items)
                                  for c in h["cb_cell"])
        print(f"  CB cell class hist: {dict(sorted(cls.items()))}")
    print("\nhome item-name set histogram:")
    for names, c in home_item_sets.most_common():
        print(f"  {c:3d} x {names}")


if __name__ == "__main__":
    main()
