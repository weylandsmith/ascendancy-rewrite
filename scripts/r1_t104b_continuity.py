#!/usr/bin/env python3
"""t104b: per-slot CONTINUITY probe around the four boundary drains.

Slots/days: (4,11,15) days 1245..1255 and (24) days 775..785. Prints, per
observed row touching the slot, the full tuple (file, turn, owner, state,
design, xyz, POWER, INTEGRITY, MOVES, ETA, b5c, b5d) plus which words of
the 177-word window CHANGED vs the previous row for that slot. A single
ship's continuity (same owner+design, moving xyz) across the drain edge
rules out free-record recycling wearing the drain signature.
"""
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_stream  # noqa: E402

RUN = "/home/hrethric/projects/ascendancy/work/r1/playcap"
PW, INTG, MOV, ETA, OSW = 68, 70, 74, 41, 46
TARGETS = {4: (1245, 1255), 11: (1245, 1255), 15: (1245, 1255),
           24: (772, 786)}

prev = {}       # slot -> window list
prev_meta = {}  # slot -> (turn, owner, state, design, xyz)
changed = Counter()

IMPORT = {PW, INTG, MOV, ETA, OSW, 0x10 // 2}  # +0x10//2 not meaningful
IMPORT = {PW, INTG, MOV, ETA, OSW}
FIRST_SEEN_TURN = set()

for j in r1_stream.observations(RUN, trust=True, stats={}):
    raw = j.get("ship_raw")
    turn = j["turn"]
    if not raw:
        continue
    if not any(lo <= turn <= hi for lo, hi in TARGETS.values()):
        continue
    smap = {s["slot"]: s for s in (j.get("ships") or [])}
    for slot_s, w in raw.items():
        slot = int(slot_s)
        if slot not in TARGETS:
            continue
        lo, hi = TARGETS[slot]
        p = prev.get(slot)
        if p is not None and lo <= turn <= hi:
            diffs = [k for k in range(177) if w[k] != p[k]]
            m = smap.get(slot)
            tk = (slot, turn)
            interesting = any(k in IMPORT for k in diffs)
            first = tk not in FIRST_SEEN_TURN
            if (interesting or first) and m is not None:
                FIRST_SEEN_TURN.add(tk)
                print(f"{j['file']} t{turn} slot{slot} own{m['owner']} "
                      f"st{m['state']} dsg{m['design']} "
                      f"xyz{[round(c) for c in m['xyz']]} "
                      f"P{w[PW]} I{w[INTG]} M{w[MOV]} ETA{w[ETA]} "
                      f"b5{hex(w[OSW])}"
                      + ("" if first else
                         f"  <-chg{[hex(k) for k in diffs[:12]]}"))
            elif first and m is None:
                FIRST_SEEN_TURN.add(tk)
                print(f"{j['file']} t{turn} slot{slot} ABSENT(state0)"
                      f" P{w[PW]} I{w[INTG]} M{w[MOV]} ETA{w[ETA]} "
                      f"b5{hex(w[OSW])}")
        prev[slot] = w
