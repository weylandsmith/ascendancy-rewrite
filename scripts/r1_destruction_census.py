#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r1_destruction_census.py — NUKE-EVENT hunt (OQ: Phase Bomb gizmo 70
destroys surface structures per gizhelp.txt). METHOD: whole-record diff
across turn-adjacent saves (u16 clock 0x254e10 H-mapped, dt==1): surface
item SETS that SHRANK without owner change (abandon/conquer would change
+0x12). Item decreases on unchanged owners = destruction candidates
(Phase Bomb AI or player). Bank the effect shape: which item ids died,
prefix compaction behavior, +0x66/class changes. Corpus work/r1/*."""
import sys, glob, os, struct as st, zipfile, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base
import r1_income_law as IL

TURN_PHYS, IMAGE_MAP_BASE = 0x254E10, 0x1BF450


def turn_of(m, base):
    off = TURN_PHYS + (base - IMAGE_MAP_BASE)
    if not (0 <= off and off + 2 <= len(m)):
        return None
    t = st.unpack_from("<H", m, off)[0]
    return t if t < 20000 else None


def state(m):
    out = {}
    for rec in IL.find_records(m):
        rb = rec[0]
        owner = m[rb + 0x12]
        if owner == 0xFF:
            continue
        ptr = st.unpack_from("<I", m, rb + 0x10)[0] + 0x88
        surf = st.unpack_from("<H", m, rb + 0x18)[0]
        capw = st.unpack_from("<H", m, rb + 0x1a)[0]
        if not (0 <= ptr and ptr + capw * 4 <= len(m)):
            continue
        items = [(k, m[ptr + 4 * k], m[ptr + 4 * k + 1],
                  st.unpack_from("<H", m, ptr + 4 * k + 2)[0])
                 for k in range(capw) if m[ptr + 4 * k + 1] != 0xFF]
        name = m[rb + 0x24:m.index(b"\x00", rb + 0x24)].decode("cp437", "replace")
        out[name] = dict(owner=owner, items=items, surf=surf,
                         f66=m[rb + 0x66], pop=st.unpack_from("<H", m, rb + 0x42)[0],
                         cap=st.unpack_from("<H", m, rb + 0x4a)[0])
    return out


def main():
    pay = open("work/ascend_payload.bin", "rb").read()
    anch = build_anchors(pay)
    shrink_events = []
    n_trans = 0
    dead_ids = collections.Counter()
    for run in sorted(glob.glob("work/r1/*")):
        if not os.path.isdir(run):
            continue
        runname = run.split("/")[-1]
        files = sorted(glob.glob(run + "/save/*.sav"), key=os.path.getmtime)
        seen, order = {}, []
        for f in files:
            n = os.path.basename(f)
            if n not in seen:
                order.append(n)
            seen[n] = f
        prev = None
        for n in order:
            try:
                m = zipfile.ZipFile(seen[n]).read("Memory")
            except Exception:
                prev = None
                continue
            votes, _ = find_base(m, anch)
            if not votes:
                prev = None
                continue
            base = votes.most_common(1)[0][0]
            items = IL.item_table(m, base)
            if items is None or not IL.names_ok(items):
                prev = None
                continue
            cur = state(m)
            if prev is not None:
                for name, c in cur.items():
                    p = prev.get(name)
                    if p is None or p["owner"] != c["owner"]:
                        continue
                    if p["surf"] != c["surf"]:
                        # WORLD-RESTART ARTIFACT (verified Hannibal III /
                        # Xerxes I 51->52.sav: +0x16 row AND +0x18 size AND
                        # most class bytes change at turn 0 -> the .sav set
                        # resumed/restarted a NEW world; same planet names are
                        # different planets. Not destruction evidence.
                        continue
                    pi = [x for x in p["items"]]
                    ci = [x for x in c["items"]]
                    if len(ci) < len(pi):
                        n_trans += 1
                        gone = [x for x in pi
                                if not any(x[2] == y[2] for y in ci)]
                        for g in gone:
                            dead_ids[items[g[2]]["name"] if g[2] < IL.N_ITEMS else g[2]] += 1
                        shrink_events.append(
                            (runname, n, name,
                             [items[x[2]]["name"] if x[2] < IL.N_ITEMS else x[2] for x in pi],
                             [items[x[2]]["name"] if x[2] < IL.N_ITEMS else x[2] for x in ci],
                             p["f66"], c["f66"], (p["pop"], c["pop"])))
            prev = cur
    print("shrink transitions (owner unchanged):", n_trans)
    print("dead item ids:", dict(dead_ids))
    for e in shrink_events[:20]:
        print("  ", e)


if __name__ == "__main__":
    main()
