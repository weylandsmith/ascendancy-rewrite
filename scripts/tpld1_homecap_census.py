#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tPL-D1 — HOME-PLANET capBase + terrain-vs-size-class census per race.

D26 complaint: "started a game with the Chamachies, and the home planet is
wrong - wrong art, wrong max population." Cheap corpus leg BEFORE any
debugger leg (STATE.md ordering): does the vendor home world carry a
DIFFERENT seeded capBase than the corpus law nb/3+5, and does its surface
look like the ordinary preset draw?

Laws used (all banked):
 - planet record stride 123, name@+0x24 (find_records via r1_income_law);
   owner byte +0x57 (0xFF unowned), capBase word +0x55, display cap +0x4a,
   surface cells word +0x18 (7/11/23/45/73), slot array = dword(+0x10)+0x88
   (t33), slot u32 {byte0 class, byte1 item}; nonbarren = raw!=0 && raw!=8
   over i < cells.
 - home law (t270): race-row dword[data 0x12e1d + race*0x1ee] == phys of the
   home STAR base; the race's own planet (owner==race) inside that star.
   Here we use the equivalent cheap join: owned planets at the EARLIEST save
   of a lineage == the home worlds (one per owner), validated by
   owned-count == Nowners.

RC=0 always unless no save parses. Prints per-lineage home rows + aggregate
verdict: home capBase vs nb/3+5, and home size-class + barren share vs the
non-home distribution.
"""
import os, os.path as op, re, struct, sys, zipfile
from collections import defaultdict

ROOT = op.dirname(op.dirname(op.abspath(__file__)))
sys.path.insert(0, op.join(ROOT, "scripts"))
REC = 123
NAME_AT = 0x24
CELLS = {7, 11, 23, 45, 73}

def load_memory(path):
    return zipfile.ZipFile(path).read("Memory")

def planets(m):
    """Return list of dicts for every record whose shape laws hold."""
    out = {}
    pos = 0
    starts = []
    NAME_RE = re.compile(rb"[A-Za-z0-9 '^_.-]{3,20}\x00")
    while True:
        mm = NAME_RE.search(m, pos)
        if not mm:
            break
        starts.append(mm.start())
        pos = mm.start() + 1
    for n in starts:
        base = n - NAME_AT
        if base < 0 or base + REC > len(m):
            continue
        cells = struct.unpack_from("<H", m, base + 0x18)[0]
        capword = struct.unpack_from("<H", m, base + 0x1a)[0]
        if cells not in CELLS or capword != cells + 10:
            continue
        ptr = struct.unpack_from("<I", m, base + 0x10)[0]
        arr = ptr + 0x88
        if not (0 <= arr and arr + capword * 4 <= len(m)):
            continue
        items = [m[arr + i * 4 + 1] for i in range(capword)]
        if not all(it == 0xFF or it < 39 for it in items):
            continue
        owner = m[base + 0x57]
        raws = [m[arr + i * 4] for i in range(cells)]
        nb = sum(1 for r in raws if r != 0 and r != 8)
        barren = sum(1 for r in raws if r == 0)
        name = m[base + NAME_AT:base + NAME_AT + 20].split(b"\x00")[0].decode("cp437", "replace")
        cap55 = struct.unpack_from("<H", m, base + 0x55)[0]
        cap4a = struct.unpack_from("<H", m, base + 0x4a)[0]
        out[base] = dict(base=base, name=name, owner=owner, cells=cells,
                         nb=nb, barren=barren, cap55=cap55, cap4a=cap4a,
                         raws=raws)
    return out

def savs_in(d):
    return sorted(f for f in os.listdir(d) if f.endswith((".sav", ".SAV")))

def main(dirs):
    home_rows, nonhome_rows = [], []
    per_race_all = {}
    lineages = 0
    for d in dirs:
        files = savs_in(d)
        if not files:
            continue
        m = load_memory(op.join(d, files[0]))
        P = planets(m)
        if not P:
            continue
        owners = {p["owner"] for p in P.values()}
        owned = [p for p in P.values() if p["owner"] != 0xFF]
        # home set = exactly one owned planet per owner at the earliest save
        by_owner = defaultdict(list)
        for p in owned:
            by_owner[p["owner"]].append(p)
        ok_lineage = all(len(v) == 1 for v in by_owner.values())
        tag = "HOMESET-OK" if ok_lineage else f"MULTI({{ {', '.join(str(len(v)) for v in by_owner.values())} }})"
        print(f"== {op.basename(d)}/{files[0]}  records={len(P)} owned={len(owned)} owners={sorted(owners)} {tag}")
        for o, v in sorted(by_owner.items()):
            if len(v) != 1:
                continue
            p = v[0]
            pred = p["nb"] // 3 + 5
            delta = p["cap55"] - pred
            hist = defaultdict(int)
            for r in p["raws"]:
                hist[r] += 1
            print(f"   race{o}: {p['name']:14s} cells={p['cells']:2d} nb={p['nb']:2d} "
                  f"cap55={p['cap55']:3d} pred(nb/3+5)={pred:3d} delta={delta:+d} "
                  f"cap4a={p['cap4a']:3d} rawhist={dict(sorted(hist.items()))}")
            home_rows.append((p["cells"], p["nb"], p["cap55"], pred, delta, p["barren"]))
            per_race_all.setdefault(o, []).append((p["cells"], p["cap55"], pred, delta))
        for p in P.values():
            if p["owner"] == 0xFF:
                pred = p["nb"] // 3 + 5
                nonhome_rows.append((p["cells"], p["nb"], p["cap55"], pred, p["cap55"] - pred, p["barren"]))
        lineages += 1

    print(f"\n=== AGGREGATE over {lineages} lineages ===")
    def summarize(rows, label):
        n = len(rows)
        if not n:
            return
        exact = sum(1 for r in rows if r[4] == 0)
        deltas = defaultdict(int)
        for r in rows:
            deltas[r[4] if len(r) == 6 else 0] += 1
        size_hist = defaultdict(int)
        for r in rows:
            size_hist[r[0]] += 1
        barren_pct = 100.0 * sum(r[5] for r in rows) / sum(r[0] for r in rows)
        print(f"{label}: n={n} cap55==nb/3+5 {exact}/{n} ({100*exact/n:.1f}%) "
              f"delta-hist={dict(sorted(deltas.items()))}")
        print(f"   size-class hist={dict(sorted(size_hist.items()))} barren share={barren_pct:.1f}%")
    summarize(home_rows, "HOME worlds   ")
    summarize(nonhome_rows, "NONHOME worlds")

    # per-race home rows (identity check: which race ids appear and how often)
    print("\nper-race home rows (raceId: n, deltas, sizes):")
    for o in sorted(per_race_all):
        rs = per_race_all[o]
        print(f"  race{o}: n={len(rs)} deltas={sorted(r[3] for r in rs)} sizes={sorted(r[0] for r in rs)}")

if __name__ == "__main__":
    dirs = sys.argv[1:]
    if not dirs:
        # default corpus: independent fresh lineages + production banks
        r1 = op.join(ROOT, "work/r1")
        dirs = []
        for d in sorted(os.listdir(r1)):
            if not (d.startswith(("r1ad-", "r1deep-")) and op.isdir(op.join(r1, d))):
                continue
            sub = op.join(r1, d, "save")
            dirs.append(sub if op.isdir(sub) else op.join(r1, d))
    main(dirs)
