#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tNAME-1 — vendor home-star NAME census across fresh-game lineages.

D33-L3 claim to test against the EXISTING save corpus (no new capture):
"in the original, a different system/planet name each game, with a
particular planet TYPE for the home planet per species".

For every save in the corpus that is a FRESH in-game lineage (turn>=1, not
the t270 template name set), read the player's (owner 0) owned planets via
the pointer law and record the star base name + surface cells. Print:
  - per-lineage owner-0 home (star base, cells)
  - the multiset of distinct star bases seen as owner-0 homes
  - whether the home cells are CONSTANT per spec while the NAME varies
Exit 0 always (census, not gate).
"""
import os, os.path as op, re, struct, sys, zipfile
from collections import defaultdict, Counter
ROOT = op.dirname(op.dirname(op.abspath(__file__)))
sys.path.insert(0, op.join(ROOT, "scripts"))
import r1_slot as S
from tpld1_homecap_census import planets

OFF = 0x82bb0
TEMPLATE_NAMES = {"Xerxes I", "Stavern I", "Hannibal III", "Gasball V",
                  "Burphee III", "Hurble I", "Vishnu IV"}

def scan(path):
    try:
        mem = zipfile.ZipFile(path).read("Memory")
    except Exception:
        return None
    pay = S.load_payload("."); anch = S.anchors_cached(".", pay)
    B = S.base_of(mem, anch)
    if B is None:
        return None
    def X(off, n):
        return mem[B + OFF + off: B + OFF + off + n]
    turn = struct.unpack_from("<I", X(0x12e10, 4))[0]
    P = planets(mem)
    owned0 = [p for p in P.values() if p["owner"] == 0]
    if not owned0 or turn > 2 or len(owned0) > 1:
        return None              # not a fresh lineage snapshot (one home each)
    if any(p["name"] in TEMPLATE_NAMES for p in P.values()):
        return None            # template scenario, not a fresh game
    spec = X(0x12e10 + 0 * 0x1ee, 0x1ee)[0x07]
    # home planet = lowest-orbit owned planet of owner 0
    m = re.match(r"(.+) (I|II|III|IV|V|V)$", owned0[0]["name"])
    base = owned0[0]["name"].rsplit(" ", 1)[0]
    return dict(turn=turn, spec=spec, base=base,
                cells=owned0[0].get("cells"), name=owned0[0]["name"],
                n_owned=len(owned0))

def main(max_dirs=40):
    # Fresh INDEPENDENT lineages only (the tpld1 corpus law): r1ad-/r1deep-/
    # attempt- capture dirs, one earliest parseable save each.
    r1 = op.join(ROOT, "work", "r1")
    dirs = []
    for d in sorted(os.listdir(r1)):
        if not d.startswith(("r1ad-", "r1deep-", "attempt-", "c3-")):
            continue
        p = op.join(r1, d)
        if not op.isdir(p):
            continue
        sub = op.join(p, "save")
        dirs.append(sub if op.isdir(sub) else p)
    rows = []
    for dirpath in dirs[:max_dirs]:
        cands = sorted((f for f in os.listdir(dirpath)
                        if f.lower().endswith((".sav", ".gam"))),
                       key=lambda f: int(op.splitext(f)[0] or 0))
        for f in cands[:2]:       # try up to 2 before giving up on the dir
            d = scan(op.join(dirpath, f))
            if d:
                d["where"] = op.relpath(op.join(dirpath, f), ROOT)
                rows.append(d)
                break
    print(f"fresh-game lineages with owner-0 home: {len(rows)}")
    for d in sorted(rows, key=lambda x: (x["spec"], x["base"])):
        print(f"  spec{d['spec']:2d} t{d['turn']:5d} {d['name']:20s} "
              f"cells={d['cells']} {d['where']}")
    print("\n== distinct star bases as owner-0 home ==")
    for base, n in Counter(d["base"] for d in rows).most_common():
        print(f"  {base:20s} {n}")
    print("\n== per-spec: distinct bases vs distinct cells ==")
    byspec = defaultdict(list)
    for d in rows:
        byspec[d["spec"]].append(d)
    for s in sorted(byspec):
        v = byspec[s]
        bases = {d["base"] for d in v}
        cells = {d["cells"] for d in v}
        verdict = ("NAME VARIES / TYPE CONSTANT"
                   if len(bases) > 1 and len(cells) == 1 else
                   "single lineage sample" if len(v) == 1 else
                   "name constant" if len(bases) == 1 else "both vary")
        print(f"  spec{s:2d} n={len(v):3d} bases={len(bases)} cells={sorted(cells)} -> {verdict}")

if __name__ == "__main__":
    main()
