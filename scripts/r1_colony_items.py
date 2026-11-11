#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r1_colony_items.py — COLONISED-PLANET INITIAL ITEMS (STATE next action
after t40). QUESTION: when an UNOWNED planet becomes owned, does the
original put a Colony Base on it in the SAME turn, or nothing (ownership
flip only)? The corpus has ZERO owned records with no active item, so a
static first-save census cannot answer it — this harness diffs
turn-adjacent saves (dt == 1 on the banked u16 clock 0x254E10 H-mapped
through image base 0x1BF450) and reports, for every planet whose owner
byte (+0x57) changes 0xFF -> empire, the item set that appears.

Also reports the CELL the arriving Colony Base lands on (rank over
non-rock cells) so the t40 home-cell envelope can be compared against
colonised planets: if the RANK law differs (e.g. always lowest free), the
placement law is per-context, not per-item.

Exit codes (loop contract): 0 = law decided, 1 = inconclusive but
recorded, 2 = harness defect.
"""
import sys, os, glob, struct as st, zipfile, collections, argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base
import r1_income_law as IL

TURN_PHYS, IMAGE_MAP_BASE = 0x254E10, 0x1BF450


def turn_of(m, base):
    """u16 turn clock phys 0x254E10 mapped via H = base - 0x1BF450
    (r1_pros_growth.py / r1_record_census.py law: offset ADDS H)."""
    off = TURN_PHYS + (base - IMAGE_MAP_BASE)
    if not (0 <= off and off + 2 <= len(m)):
        return None
    t = st.unpack_from("<H", m, off)[0]
    return t if t < 20000 else None


def planet_view(m, base, items):
    """(name, row) keyed view: owner, active items [(cell, name)], cells."""
    out = {}
    for rec in IL.find_records(m):
        rb = rec[0]
        name = m[rb + 0x24:m.index(b"\x00", rb + 0x24)].decode("cp437", "replace")
        arr = st.unpack_from("<I", m, rb + 0x10)[0] + 0x88
        cells = st.unpack_from("<H", m, rb + 0x18)[0]
        act = []
        for k in range(cells + 10):
            it = m[arr + 4 * k + 1]
            if it == 0xFF or it >= IL.N_ITEMS:
                continue
            if st.unpack_from("<H", m, arr + 4 * k + 2)[0] & 1:
                act.append((k, items[it]["name"]))
        out[(name, cells)] = dict(
            rb=rb, owner=m[rb + 0x57], act=act, cells=cells,
            pop=st.unpack_from("<H", m, rb + 0x42)[0],
            cap=st.unpack_from("<H", m, rb + 0x4a)[0],
            seed=st.unpack_from("<H", m, rb + 0x55)[0],
            classes=[m[arr + 4 * k] for k in range(cells)],
            f66=m[rb + 0x66])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="work/r1/*")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()

    pay = open("work/ascend_payload.bin", "rb").read()
    anch = build_anchors(pay)

    # PRIMARY METHOD (dt==1 turn-clock diffs): the R1 corpus saves are too
    # coarse — full-corpus dt==1 pairs contain zero flips (T41 run:
    # 24 dt-pairs / 437). SECONDARY METHOD resolves it: for each run, take
    # the run's FIRST save as baseline and record, for every planet that was
    # UNOWNED there and becomes owned later, its item set at the EARLIEST
    # owned observation. Colonisation cannot partially place a CB, so the
    # earliest observation equals the arrival state unless a same-turn
    # extra build landed (would show >1 items; reported separately).
    n_pairs = n_dt1 = n_flip = 0
    n_col = 0
    itemsets = collections.Counter()
    pop_at = collections.Counter()
    caplaw = collections.Counter()
    cb_rank = collections.Counter()

    for run in sorted(glob.glob(a.runs)):
        if not os.path.isdir(run):
            continue
        files = sorted(glob.glob(run + "/save/*.sav"), key=os.path.getmtime)
        first = None
        prev = None
        seen = set()
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
            cur = planet_view(m, base, items)
            t = turn_of(m, base)
            if first is None:
                first = cur
                prev = (cur, t)
                continue
            pview, pt = prev
            n_pairs += 1
            if t is not None and pt is not None and t - pt == 1:
                n_dt1 += 1
                for key, c in cur.items():
                    p = pview.get(key)
                    if p is None or p["owner"] != 0xFF or c["owner"] == 0xFF:
                        continue
                    n_flip += 1
            for name, c in cur.items():
                p = first.get(name)
                if p is None or p["owner"] != 0xFF or c["owner"] == 0xFF:
                    continue
                if name in seen:
                    continue
                seen.add(name)
                n_col += 1
                names = tuple(sorted(set(nm for _, nm in c["act"])))
                itemsets[names] += 1
                pop_at[c["pop"]] += 1
                cb = 2 if "Colony Base" in names else 0
                caplaw["exact" if c["cap"] == c["seed"] + cb else
                       f'{c["cap"]}v{c["seed"]}+{cb}'] += 1
                for k, nm2 in c["act"]:
                    if nm2 != "Colony Base":
                        continue
                    nr = [i for i, cl in enumerate(c["classes"]) if not (cl & 8)]
                    cb_rank[nr.index(k) if k in nr else -1] += 1
                if a.verbose:
                    print(f"  COL {os.path.basename(run)} {os.path.basename(f)} "
                          f"{name:15s} own={c['owner']} pop={c['pop']} items={c['act']}")
            prev = (cur, t)

    print(f"consecutive save pairs: {n_pairs}   dt==1: {n_dt1}   dt-flips: {n_flip}")
    print(f"in-run colonisations (earliest-owned observations): {n_col}")
    print("item set at arrival:")
    for k, c in itemsets.most_common(8):
        print(f"   {c:4d} x {k}")
    print(f"pop at arrival: {dict(sorted(pop_at.items()))}")
    print(f"cap == seed + CB MPOP(2): {dict(caplaw.most_common(5))}")
    print(f"arriving-CB buildable-cell RANK hist: {dict(sorted(cb_rank.items()))}")

    if n_col == 0:
        print("VERDICT NODATA")
        return 1
    if itemsets.most_common(1)[0] == (("Colony Base",), n_col):
        print("VERDICT CB — colonised planets arrive with exactly one Colony Base")
        return 0
    print("VERDICT MIXED/OTHER — see histogram")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
