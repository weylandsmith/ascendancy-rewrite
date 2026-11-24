#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tPL-D1b — owner-index -> RACE identity join on the earliest save of each
lineage, then home-world size/nb/capBase per race.

Laws (all banked):
 - STATE race rows: STATE = DS+0x12e10 (t441); row stride 0x1ee; row+0x07
   specnum (race id, t270 race-row table data 0x12e1d + race*0x1ee is the
   same table keyed by specnum); row home-star pointer (t270/t441: lands at
   the star record base = STATE+0xd8d+0x60*j).
 - member addr = B + 0x82bb0 + X (pointer law OQ-011).
 - race id -> name: extracted/ascend00/raceNN.dip first comment line.
 - home planet = the race's owned planet at the earliest in-game save
   (HOMESET-OK validated in tpld1_homecap_census).
RC=0 always unless no lineage parses.
"""
import os, os.path as op, re, struct, sys, zipfile
from collections import defaultdict
ROOT = op.dirname(op.dirname(op.abspath(__file__)))
sys.path.insert(0, op.join(ROOT, "scripts"))
import r1_slot as S
sys.path.insert(0, op.join(ROOT, "scripts"))
from tpld1_homecap_census import planets

OFF = 0x82bb0

def dip_names():
    names = {}
    d = op.join(ROOT, "extracted", "ascend00")
    if not op.isdir(d):
        return names
    for f in os.listdir(d):
        m = re.match(r"race(\d+)\.dip$", f)
        if not m:
            continue
        try:
            txt = open(op.join(d, f), "rb").read(4000).decode("cp437", "replace")
        except OSError:
            continue
        mm = re.search(r"Diplomacy text for (?:the )?([A-Za-z]+)", txt)
        if mm:
            names[int(m.group(1))] = mm.group(1)
    return names

def analyze(path, names):
    mem = zipfile.ZipFile(path).read("Memory")
    pay = S.load_payload("."); anch = S.anchors_cached(".", pay)
    B = S.base_of(mem, anch)
    def X(Xoff, n):
        return mem[B + OFF + Xoff: B + OFF + Xoff + n]
    turn = struct.unpack_from("<I", X(0x12e10, 4))[0]
    nstars = struct.unpack_from("<I", X(0x16143, 4))[0] >> 16
    rows = []
    for r in range(8):
        row = X(0x12e10 + r * 0x1ee, 0x1ee)
        if len(row) < 0x20:
            break
        specnum = row[0x07]
        colour = row[0x08]
        home_ptr = struct.unpack_from("<I", row, 0x0d)[0]
        star_idx = None
        if home_ptr:
            # star base = STATE+0xd8d+0x60*j  (t441)
            rel = home_ptr - (0x12e10 + 0xd8d)
            if rel >= 0 and rel % 0x60 == 0:
                star_idx = rel // 0x60
        rows.append((r, specnum, colour, home_ptr, star_idx))
    P = planets(mem)
    owned = [p for p in P.values() if p["owner"] != 0xFF]
    by_owner = defaultdict(list)
    for p in owned:
        by_owner[p["owner"]].append(p)
    print(f"== {path} turn={turn} nstars={nstars} records={len(P)} owned={len(owned)}")
    for (r, specnum, colour, home_ptr, star_idx) in rows:
        nm = names.get(specnum, f"?{specnum}")
        pv = by_owner.get(r, [])
        if len(pv) == 1:
            p = pv[0]
            pred = p["nb"] // 3 + 5
            print(f"  row{r} spec={specnum:2d}({nm:12s}) col={colour} home_star={star_idx} "
                  f"planet={p['name']!r} cells={p['cells']} nb={p['nb']} cap55={p['cap55']} "
                  f"pred={pred} delta={p['cap55']-pred:+d} row16hist=")
        else:
            print(f"  row{r} spec={specnum:2d}({nm:12s}) col={colour} home_star={star_idx} owned_here={len(pv)}")

if __name__ == "__main__":
    names = dip_names()
    print("dip names:", dict(sorted(names.items())))
    r1 = op.join(ROOT, "work/r1")
    dirs = sys.argv[1:]
    if not dirs:
        dirs = []
        for d in sorted(os.listdir(r1)):
            if not (d.startswith(("r1ad-", "r1deep-")) and op.isdir(op.join(r1, d))):
                continue
            sub = op.join(r1, d, "save")
            dirs.append(sub if op.isdir(sub) else op.join(r1, d))
    ok = 0
    for d in dirs:
        files = sorted(f for f in os.listdir(d) if f.endswith((".sav", ".SAV")))
        if not files:
            continue
        try:
            analyze(op.join(d, files[0]), names)
            ok += 1
        except Exception as e:
            print(f"== {d}: SKIP {e}")
    print(f"\nparsed {ok}/{len(dirs)} lineages")
