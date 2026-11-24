#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tPL-D1c — DECISIVE: per-spec home size constancy + race-row field hunt.

Legs:
 L1 per-spec home size class across turn>=1 earliest saves (trust law:
    in-game iff t>0 OR score>=1; template saves = t270 name set -> excluded).
 L2 race-row byte-offset scan: offsets whose byte == the race's home size
    CLASS INDEX (cells->idx in 7/11/23/45/73) for EVERY participating race
    in EVERY lineage. Same for u16 == cells.
 L3 static template: payload data segment — the template planet records
    (t270 names) give each spec's TEMPLATE home cells; print alongside.
"""
import os, os.path as op, re, struct, sys, zipfile
from collections import defaultdict
ROOT = op.dirname(op.dirname(op.abspath(__file__)))
sys.path.insert(0, op.join(ROOT, "scripts"))
import r1_slot as S
from tpld1_homecap_census import planets

OFF = 0x82bb0
CELLS = [7, 11, 23, 45, 73]
TEMPLATE_NAMES = {"Xerxes I", "Stavern I", "Hannibal III", "Gasball V",
                  "Burphee III", "Hurble I", "Vishnu IV"}

def dip_names():
    names = {}
    d = op.join(ROOT, "extracted", "ascend00")
    for f in os.listdir(d):
        m = re.match(r"race(\d+)\.dip$", f)
        if not m:
            continue
        txt = open(op.join(d, f), "rb").read(4000).decode("cp437", "replace")
        mm = re.search(r"Diplomacy text for (?:the )?([A-Za-z]+)", txt)
        if mm:
            names[int(m.group(1))] = mm.group(1)
    return names

def lineage(path, names):
    mem = zipfile.ZipFile(path).read("Memory")
    pay = S.load_payload("."); anch = S.anchors_cached(".", pay)
    B = S.base_of(mem, anch)
    assert B is not None, "anchor failed"
    def X(off, n):
        return mem[B + OFF + off: B + OFF + off + n]
    turn = struct.unpack_from("<I", X(0x12e10, 4))[0]
    P = planets(mem)
    owned = [p for p in P.values() if p["owner"] != 0xFF]
    if not owned:
        return None
    if any(p["name"] in TEMPLATE_NAMES for p in owned):
        return ("template", turn)
    by_owner = defaultdict(list)
    for p in owned:
        by_owner[p["owner"]].append(p)
    specs = []
    for r in range(8):
        row = X(0x12e10 + r * 0x1ee, 0x1ee)
        spec = row[0x07]
        if spec == 255:
            break
        if len(by_owner.get(r, [])) == 1:
            specs.append((r, spec, by_owner[r][0]))
        elif len(by_owner.get(r, [])) > 1:
            return ("multi", turn)
    return ("ok", turn, specs, mem, B)

def main():
    names = dip_names()
    r1 = op.join(ROOT, "work/r1")
    dirs = []
    for d in sorted(os.listdir(r1)):
        if not (d.startswith(("r1ad-", "r1deep-")) and op.isdir(op.join(r1, d))):
            continue
        sub = op.join(r1, d, "save")
        dirs.append(sub if op.isdir(sub) else op.join(r1, d))

    per_spec = defaultdict(list)          # L1
    idx_votes = defaultdict(int)          # L2 byte offset -> lineages all-match
    idx_detail = defaultdict(lambda: defaultdict(set))
    u16_votes = defaultdict(int)
    n_ok = 0
    for d in dirs:
        files = sorted(f for f in os.listdir(d) if f.endswith((".sav", ".SAV")))
        if not files:
            continue
        res = lineage(op.join(d, files[0]), names)
        if not res or res[0] != "ok":
            print(f"{op.basename(d)}: {res[0] if res else 'empty'} turn={res[1] if res else '-'}")
            continue
        _, turn, specs, mem, B = res
        n_ok += 1
        print(f"{op.basename(d)} turn={turn}: " + " ".join(
            f"{names.get(s,'?'+str(s))}={p['cells']}" for _, s, p in specs))
        for _, spec, p in specs:
            per_spec[spec].append((p["cells"], p["name"], p["nb"], p["cap55"]))
        # L2: per lineage, which byte offsets match home size idx for all races
        ok_idx_offsets = None
        ok_u16_offsets = None
        for r, spec, p in specs:
            row = mem[B + OFF + 0x12e10 + r * 0x1ee: B + OFF + 0x12e10 + r * 0x1ee + 0x1ee]
            ci = CELLS.index(p["cells"]) if p["cells"] in CELLS else None
            if ci is None:
                ok_idx_offsets = set()
                break
            hits = {bo for bo, v in enumerate(row) if v == ci}
            ok_idx_offsets = hits if ok_idx_offsets is None else (ok_idx_offsets & hits)
            hits16 = {bo for bo in range(0, 0x1ec) if struct.unpack_from("<H", row, bo)[0] == p["cells"]}
            ok_u16_offsets = hits16 if ok_u16_offsets is None else (ok_u16_offsets & hits16)
        for o in (ok_idx_offsets or set()):
            idx_votes[o] += 1
            for _, spec, p in specs:
                idx_detail[o][spec].add(p["cells"])
        for o in (ok_u16_offsets or set()):
            u16_votes[o] += 1

    print(f"\n== L1 per-spec home cells (turn>=1 lineages, n_ok={n_ok}) ==")
    for spec in sorted(per_spec):
        rows = per_spec[spec]
        sizes = sorted({r[0] for r in rows})
        const = "CONSTANT" if len(sizes) == 1 else "VARIES"
        print(f"  spec{spec:2d} {names.get(spec,'?'):12s} n={len(rows):2d} sizes={sizes} {const}")
        if len(sizes) > 1:
            for r in rows:
                print(f"      {r[1]:16s} cells={r[0]} nb={r[2]} cap55={r[3]}")

    print("\n== L2 byte offsets matching home-size-idx in ALL lineages ==")
    for o in sorted(idx_votes, key=lambda x: -idx_votes[x]):
        if idx_votes[o] >= max(2, n_ok // 3):
            det = {s: sorted(v) for s, v in sorted(idx_detail[o].items())}
            print(f"  row+0x{o:02x}: all-match {idx_votes[o]}/{n_ok} detail={det}")
    print("== L2 u16 offsets matching home cells in ALL lineages ==")
    for o in sorted(u16_votes, key=lambda x: -u16_votes[x]):
        if u16_votes[o] >= max(2, n_ok // 3):
            print(f"  row+0x{o:02x}: all-match {u16_votes[o]}/{n_ok}")

if __name__ == "__main__":
    main()
