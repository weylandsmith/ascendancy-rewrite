#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r1_cell_choice_census.py — t42 evidence census for the CB/built-item cell
law (picker FUN_0003875c uniform-among-legal-empty).

Three questions in one pass:
 (Q1) NON-CB active items on class-0 (barren) cells anywhere in the corpus?
      Decides the FUN_0003830c rule-B polarity question and re-checks the
      t25 "items on barren at terrain rate" note post-t33 (+0x88 array).
 (Q2) Home CBs at game-start worlds (earliest-save turn <= 2):
      cell index, first-buildable index, rank over buildable. Tests the
      t40 "rank 0/1 zero" envelope and whether cell 0/1 were even buildable.
 (Q3) First-save CB population split: world-start homes vs mid-game worlds
      (turn > 2 — colonies placed pre-capture), with class + rank stats per
      population. The 41 class-0 CBs from r1_cb_picker_law.py: which side?
"""
import sys, os, glob, struct as st, zipfile, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base
import r1_income_law as IL

TURN_PHYS, IMAGE_MAP_BASE = 0x254E10, 0x1BF450  # banked H-map law (r1_pros_growth)


def rec_iter(m):
    for rec in IL.find_records(m):
        rb = rec[0]
        if m[rb + 0x57] == 0xFF:
            continue
        ptr = st.unpack_from("<I", m, rb + 0x10)[0] + 0x88
        surf = st.unpack_from("<H", m, rb + 0x18)[0]
        capw = st.unpack_from("<H", m, rb + 0x1a)[0]
        yield rb, ptr, surf, capw


def main():
    pay = open("work/ascend_payload.bin", "rb").read()
    anch = build_anchors(pay)

    worlds = {}   # wid -> (path, mtime, turn)
    q1 = collections.Counter()          # (is_cb, cls_bucket) mid+first saves
    q2_rows = []
    for run in sorted(glob.glob("work/r1/*")):
        if not os.path.isdir(run):
            continue
        for f in sorted(glob.glob(run + "/save/*.sav"), key=os.path.getmtime):
            try:
                z = zipfile.ZipFile(f)
                m = z.read("Memory")
            except Exception:
                continue
            votes, _ = find_base(m, anch)
            if not votes:
                continue
            base = votes.most_common(1)[0][0]
            items = IL.item_table(m, base)
            if items is None or not IL.names_ok(items):
                continue
            ids = []
            for rb, ptr, surf, capw in rec_iter(m):
                name = m[rb + 0x24:m.index(b"\x00", rb + 0x24)].decode("cp437", "replace")
                ids.append((name, st.unpack_from("<H", m, rb + 0x16)[0], capw))
            if not ids:
                continue
            wid = tuple(ids)
            # banked turn-clock H-map law (r1_pros_growth.turn_of):
            # member index = phys + (base - 0x1BF450)
            try:
                turn = st.unpack_from("<H", m, TURN_PHYS + (base - IMAGE_MAP_BASE))[0]
            except Exception:
                turn = 999
            # Q1: scan EVERY save's items once per (world,save-file) dedup=none
            for rb, ptr, surf, capw in rec_iter(m):
                for k in range(min(capw, 200)):
                    it = m[ptr + 4 * k + 1]
                    if it == 0xFF or it >= IL.N_ITEMS:
                        continue
                    if not (st.unpack_from("<H", m, ptr + 4 * k + 2)[0] & 1):
                        continue
                    cls = m[ptr + 4 * k]
                    bucket = "rock" if cls & 8 else cls
                    nm = items[it]["name"]
                    q1[(nm == "Colony Base", bucket, k >= surf)] += 1
                    if nm == "Colony Base" and bucket == 0 and k < surf:
                        pass
            if wid not in worlds or os.path.getmtime(f) < worlds[wid][1]:
                worlds[wid] = (f, os.path.getmtime(f), turn)

    print(f"Q1 active items by (CB?, class, orbital) across ALL saves:")
    for key in sorted(q1, key=str):
        print(f"   cb={key[0]} cls={key[1]} orb={key[2]}  {q1[key]}")

    n_ws = sum(1 for _, _, t in worlds.values() if t <= 2)
    n_mid = len(worlds) - n_ws
    print(f"\nworlds: {len(worlds)}  (game-start turn<=2: {n_ws}, mid-game first-save: {n_mid})")

    cls_pop = collections.Counter()
    rank_rows = {"start": [], "mid": []}
    cell0_hist = collections.Counter()
    for wid, (f, mt, turn) in worlds.items():
        m = zipfile.ZipFile(f).read("Memory")
        pop_tag = "start" if turn <= 2 else "mid"
        for rb, ptr, surf, capw in rec_iter(m):
            cbk = [k for k in range(min(capw, 200))
                   if m[ptr + 4 * k + 1] == 5
                   and (st.unpack_from("<H", m, ptr + 4 * k + 2)[0] & 1)]
            if not cbk:
                continue
            if turn <= 2:
                # Q2: this is THE home (exactly one owned per empire at t0)
                sur = [m[ptr + 4 * k] for k in range(surf)]
                build = [i for i, c in enumerate(sur) if c != 0 and not (c & 8)]
                for k in cbk:
                    rank = build.index(k) if k in build else -1
                    rank_rows[pop_tag].append((k, len(build), rank))
                    cell0_hist[(f"cell0_buildable={0 in build}",
                                f"cell1_buildable={1 in build}",
                                f"cb_at={k}")] += 1
            for k in cbk:
                cls = m[ptr + 4 * k]
                cls_pop[(pop_tag, "rock" if cls & 8 else cls, k >= surf)] += 1
    print("\nQ3 CB class by population (turn<=2 home vs mid-game):")
    for key in sorted(cls_pop, key=str):
        print(f"   {key}: {cls_pop[key]}")
    print("\nQ2 home-CB cell/rank rows (turn<=2 worlds):")
    for (k, nb, rank) in sorted(rank_rows["start"]):
        print(f"   cell={k:3d} nb={nb:3d} rank={rank}")
    print("\nQ2 cell0/1 buildable cross-tab:")
    for key, v in sorted(cell0_hist.items(), key=lambda kv: -kv[1])[:14]:
        print(f"   {key}: {v}")
    # aggregate: homes where cell 0 IS buildable — where did the CB go?
    agg = [r for r in rank_rows["start"]]
    if agg:
        ranks = [r for _, _, r in agg if r >= 0]
        hist = collections.Counter(min(r, 5) for r in ranks)
        print(f"\nhome rank hist (capped 5): {dict(sorted(hist.items()))} n={len(ranks)}")
        on0 = sum(1 for k, nb, r in agg if k == 0)
        c0b = sum(1 for wid, (f, mt, turn) in worlds.items() if turn <= 2)
        print(f"home CBs sitting on cell index 0: {on0}")


main()
