#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r255e_semantics.py — what does V=DAT_482fb count? Correlate per trusted
row (per-session trust) with cheap fields: ships count, relation matrix
alive-race census (matrix = 4x4 relation states; states matrix rows per race
pair banked by the watcher), systems_any/full, planets_mine.

Also: title-class check — do V==0 rows carry ships? (title snapshot => no
ships). Relation matrix lives in the row MIDDLE (after "ships"): stream the
line, extract '"matrix": [[...]]' by string ops (rows are ~25 KB; per-line
string ops are fine, NO whole-file load).
"""
import sys
JSONL = sys.argv[1] if len(sys.argv) > 1 else "work/r1/playcap/live-timeline.jsonl"

def get_int(s, key):
    i = s.find(key)
    if i < 0:
        return None
    i += len(key)
    j = s.find(",", i)
    j2 = s.find("}", i)
    if j < 0 or (0 <= j2 < j):
        j = j2
    try:
        return int(s[i:j])
    except Exception:
        return None

def get_file(head):
    i = head.find('"file": "')
    if i < 0:
        return None
    i += 9
    j = head.find(",", i)
    seg = head[i:j]
    q = seg.find('"')
    return None if q < 0 else seg[:q]

rows, seen = [], set()
with open(JSONL, "r", errors="replace") as f:
    while True:
        line = f.readline()
        if not line:
            break
        head, tail = line[:600], line[-260:]
        fn = get_file(head)
        if fn is None:
            continue
        turn = get_int(head, '"turn": ')
        mt = get_int(tail, '"file_mtime_ns": ')
        if turn is None or mt is None or (fn, mt) in seen:
            continue
        seen.add((fn, mt))
        # ship count: count '"slot": ' occurrences in the ships segment
        si = head.find('"ships": [')
        ei = -1
        if si < 0:
            nships = None
        else:
            ei = line.find('], "ship_raw"', si)
            nships = line.count('"slot": ', si, ei) if ei > 0 else None
        # relation matrix
        mi = line.find('"matrix": [[', ei if ei > 0 else si)
        mat = None
        if mi >= 0:
            mi += 10
            mj = line.find("]]", mi)
            try:
                import json as _j
                mat = _j.loads("[" + line[mi:mj] + "]")   # small substring only
            except Exception:
                mat = None
        rows.append((mt, fn, turn, get_int(head, '"score_stars": '),
                     nships, get_int(tail, '"systems_any": '),
                     get_int(tail, '"systems_full": '),
                     get_int(tail, '"planets_mine": '), mat))
rows.sort()

# per-session trust
sessions = []
prev = None
for r in rows:
    if prev is not None and (r[0] - prev[0]) / 1e9 > 600:
        sessions.append([])
    if not sessions:
        sessions.append([])
    sessions[-1].append(r)
    prev = r
trusted = []
for s in sessions:
    wm = 0
    for r in s:
        if r[2] <= 0 or r[2] < wm:
            continue
        wm = max(wm, r[2])
        trusted.append(r)

# 1. title-class check on V==0
z = [r for r in trusted if r[3] == 0]
zs = {}
for r in z:
    zs[r[4]] = zs.get(r[4], 0) + 1
print(f"V==0 trusted rows={len(z)} ship-count histogram={dict(sorted(zs.items(), key=lambda kv: (kv[0] is None, kv[0])))}")
nz0 = z[:5]
print("sample V==0:", [(r[1], r[2], r[4], r[5], r[6]) for r in nz0])

# 2. V vs alive races from matrix (distinct states nonzero count is weak; use
#    count of races appearing? matrix is 4x4 over races with relations) —
#    instead census: number of nonzero cells, and matrix shape variance
mats = [r for r in trusted if r[8]]
print(f"rows_with_matrix={len(mats)}")
from collections import Counter
shapes = Counter(len(m) for m in mats)
print("matrix cell-count hist:", dict(shapes))

# 3. per (turn,V) uniqueness: does V co-determine nships? build V->nships sets
assoc = {}
for r in trusted:
    if r[3] and r[4] is not None:
        assoc.setdefault(r[3], Counter())[r[4]] += 1
for v in sorted(assoc):
    c = assoc[v]
    print(f"V={v:3d} nships: {sorted(c)[:10]}{'...' if len(c)>10 else ''} (distinct {len(c)})")
