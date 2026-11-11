#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r1_rock_convention.py — T38 tie-breaker: does capBase (+0x55 seed word)
count the rock-marked cell NON-barren (pre-mark count: '|=' preserves the
base class) or BARREN (post-mark count: bit-3 masks the class)? Only raw-8
(barren|rock) planets, or non-barren-rock planets where //3 differs, are
discriminating. Also: does +0x55 move when a MID-GAME rock event appears?
Usage: r1_rock_convention.py  (corpus work/r1/*)"""
import sys, glob, os, struct as st, zipfile, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from r1_sav_scan import build_anchors, find_base
import r1_income_law as IL

pay = open("work/ascend_payload.bin", "rb").read()
anch = build_anchors(pay)

first_convent = collections.Counter()
first_ex = collections.defaultdict(list)
event_55 = collections.Counter()
event_n = 0
rock_nb_delta = collections.Counter()  # raw 10..12 planets: capBase vs pre/post

for run in sorted(glob.glob("work/r1/*")):
    if not os.path.isdir(run):
        continue
    names_seen = set()
    prev_state = None
    files = sorted(glob.glob(run + "/save/*.sav"), key=os.path.getmtime)
    seen, order = {}, []
    for f in files:
        n = os.path.basename(f)
        if n not in seen:
            order.append(n)
        seen[n] = f
    for n in order:
        try:
            m = zipfile.ZipFile(seen[n]).read("Memory")
        except Exception:
            prev_state = None
            continue
        votes, _ = find_base(m, anch)
        if not votes:
            prev_state = None
            continue
        base = votes.most_common(1)[0][0]
        items = IL.item_table(m, base)
        if items is None or not IL.names_ok(items):
            prev_state = None
            continue
        cur = {}
        for rec in IL.find_records(m):
            rb = rec[0]
            if m[rb + 0x12] == 0xFF:
                continue
            ptr = st.unpack_from("<I", m, rb + 0x10)[0] + 0x88
            surf = st.unpack_from("<H", m, rb + 0x18)[0]
            capw = st.unpack_from("<H", m, rb + 0x1a)[0]
            if not (0 <= ptr and ptr + capw * 4 <= len(m)):
                continue
            cls = [m[ptr + 4 * k] for k in range(capw)]
            sur = cls[:surf]
            rocks = [c for c in sur if c & 8]
            nb_pre = sum(1 for c in sur if c != 0 and c != 8)
            nb_post = sum(1 for c in sur if c != 0)
            name = m[rb + 0x24:m.index(b"\x00", rb + 0x24)].decode("cp437", "replace")
            s55 = st.unpack_from("<H", m, rb + 0x55)[0]
            cur[name] = (s55, nb_pre, nb_post, bool(rocks))
            if rocks and (run, name) not in names_seen:
                names_seen.add((run, name))
                va, vb = nb_pre // 3 + 5, nb_post // 3 + 5
                if va == vb:
                    first_convent["tied (non-discerning)"] += 1
                elif s55 == va and s55 != vb:
                    first_convent["pre-mark wins"] += 1
                    if len(first_ex["pre"]) < 5:
                        first_ex["pre"].append((run.split("/")[-1], n, name, s55, va, vb))
                elif s55 == vb and s55 != va:
                    first_convent["post-mark wins"] += 1
                    if len(first_ex["post"]) < 5:
                        first_ex["post"].append((run.split("/")[-1], n, name, s55, va, vb))
                else:
                    first_convent["neither"] += 1
                    rock_nb_delta[(s55 - va, s55 - vb)] += 1
        if prev_state is not None:
            for name, (s55, a, b, has8) in cur.items():
                p = prev_state.get(name)
                if p is None:
                    continue
                ps55, _, _, phas8 = p
                if has8 and not phas8:
                    event_n += 1
                    event_55[s55 - ps55] += 1
        prev_state = cur

print("first-save rock-planet seed-word convention:", dict(first_convent))
for k, v in first_ex.items():
    for e in v:
        print(f"  {k}: {e}")
print("mid-game rock-APPEARANCE transitions:", event_n,
      " +0x55 delta histogram:", dict(event_55))
