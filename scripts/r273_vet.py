#!/usr/bin/env python3
"""t273 — attribution vet for the leg-A hull-decrease hits.

The harvest's `near_own` is the NEAREST other-owner ship, which is not the
attacker. A hull decrease next to a PEACE power is only a witness for OQ-016
(damage against a NON-at-war owner) if NO power that IS at war with the victim
had a ship within engagement scale in the same row. This script re-reads the
exact rows the harvest flagged and prints, per hit, the minimum distance from
the victim slot to (a) any ship of a power at war with the victim and (b) any
ship of a power at peace with the victim.

usage: r273_vet.py            (rows are hard-coded from work/r1/t273_legA.json)
"""
import json
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSONL = os.path.join(ROOT, "work/r1/playcap/live-timeline.jsonl")

HIT_ROWS = [  # (turn, wall, damaged slot)
    (624, "02:12:31", 7),
    (908, "23:41:53", 3),
    (908, "23:42:13", 3),
    (1017, "14:47:32", 0),
    (1253, "00:40:46", 21),
    (1253, "08:31:34", 23),
]
ENGAGE2 = 3600.0 ** 0.5   # t251 engagement-scale bound (unverified, generous)


def race(w):
    b = struct.pack("<177H", *w)[0x56]
    return -1 if b == 0xFF else b


def xyz(w):
    return struct.unpack_from("<3f", struct.pack("<177H", *w), 0x9E)


want = {(t, w): s for t, w, s in HIT_ROWS}
n = 0
for line in open(JSONL, errors="replace"):
    i = line.find('"wall": "')
    if i < 0:
        continue
    key = None
    for (t, w) in want:
        if w == line[i + 9:i + 17] and ('"turn": %s,' % t) in line:
            key = (t, w)
            break
    if key is None:
        continue
    try:
        d = json.loads(line)
    except Exception:
        j = line.find('"ship_raw"')
        d = json.loads(line[:j].rstrip().rstrip(",") + "}")
    rel = d.get("relation")
    raw = d.get("ship_raw")
    if not rel or not raw:
        continue
    sl = want[key]
    w = raw.get(str(sl))
    if w is None:
        continue
    own = race(w)
    if own < 0 or own >= rel["n"]:
        continue
    x, y, z = xyz(w)
    war = [j2 for j2 in range(rel["n"]) if rel["states"][own][j2] == 2]
    peace = [j2 for j2 in range(rel["n"]) if rel["states"][own][j2] == 1]
    dmin_war = None
    dmin_peace = None
    for k2, w2 in raw.items():
        if int(k2) == sl or not any(w2) or all(v == 0xFFFF for v in w2):
            continue
        o2 = race(w2)
        if o2 < 0 or o2 == own:
            continue
        x2, y2, z2 = xyz(w2)
        dd = ((x - x2) ** 2 + (y - y2) ** 2 + (z - z2) ** 2) ** 0.5
        if o2 in war and (dmin_war is None or dd < dmin_war):
            dmin_war = dd
        if o2 in peace and (dmin_peace is None or dd < dmin_peace):
            dmin_peace = dd
    print(f"turn {key[0]} wall {key[1]} slot {sl} victim={rel['names'][own]}")
    print(f"   at war with {[rel['names'][j2] for j2 in war]}  at peace with "
          f"{[rel['names'][j2] for j2 in peace]}")
    print(f"   min dist to a WAR power  : {None if dmin_war is None else round(dmin_war,1)}")
    print(f"   min dist to a PEACE power: {None if dmin_peace is None else round(dmin_peace,1)}")
    verdict = ("MISATTRIBUTION-LIKELY (a hostile power was in reach)"
               if dmin_war is not None and dmin_war <= 60
               else ("NON-WAR DAMAGE CANDIDATE (no hostile power in reach)"
                     if dmin_peace is not None and dmin_peace <= 60
                     else "UNATTRIBUTED (no ship of either class in reach)"))
    print(f"   => {verdict}")
    n += 1
print(f"\nvetted rows: {n} of {len(HIT_ROWS)}")
