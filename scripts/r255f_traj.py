#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r255f_traj.py — per-session per-turn trajectory: turn, V, systems_any,
systems_full, planets, nships. Tests whether V equals a TERRITORY SNAPSHOT
taken at some earlier turn (the "recompute-at-event" family) by checking, for
each V-change a->b, whether b equals any/full/planets AT that turn or at any
turn in the session's PAST (lag search).
"""
import sys
from collections import OrderedDict
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
        si = head.find('"ships": [')
        ei = line.find('], "ship_raw"', si) if si >= 0 else -1
        nsh = line.count('"slot": ', si, ei) if ei > 0 else None
        rows.append((mt, fn, turn, get_int(head, '"score_stars": '), nsh,
                     get_int(tail, '"systems_any": '),
                     get_int(tail, '"systems_full": '),
                     get_int(tail, '"planets_mine": ')))
rows.sort()
sessions, prev = [], None
for r in rows:
    if prev is not None and (r[0] - prev[0]) / 1e9 > 600:
        sessions.append([])
    if not sessions:
        sessions.append([])
    sessions[-1].append(r)
    prev = r

for k, s in enumerate(sessions):
    wm = 0
    traj = OrderedDict()
    for r in s:
        if r[2] <= 0 or r[2] < wm:
            continue
        wm = max(wm, r[2])
        if r[2] not in traj or (traj[r[2]][1] is None and r[3] is not None):
            traj[r[2]] = (r[3], r[3], r[5], r[6], r[7], r[4])
    if len(traj) < 3:
        continue
    print(f"--- S{k:02d} n_turns={len(traj)} (turn:V/any/full/planets/ships)")
    items = list(traj.items())
    prevV = None
    lags = []
    for idx, (t, (V, _, a, fu, pl, sh)) in enumerate(items):
        if V != prevV:
            # search the session's PAST (and this turn) for a==V / fu==V / pl==V
            hit = None
            for j in range(0, idx + 1):
                tj, (_, _, aj, fj, pj, _) = items[j]
                if aj == V:
                    hit = f"any@{tj}"
                    break
                if fj == V:
                    hit = f"full@{tj}"
                    break
                if pj == V:
                    hit = f"planets@{tj}"
                    break
            lags.append((t, prevV, V, hit))
            print(f"  t{t} V:{prevV}->{V} any={a} full={fu} pl={pl} ships={sh} past-match={hit}")
        prevV = V
    nhit = sum(1 for x in lags if x[3])
    print(f"  S{k:02d}: V-changes={len(lags)} with_past_match={nhit}")
