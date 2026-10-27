#!/usr/bin/env python3
"""t104c: CONTINUITY-GATED order-completion drain census.

t104b lesson: raw P>0->0 transitions count death/recycle artifacts. This
pass only reports a DRAIN when the record is CONTINUOUS across the pair:
same owner, same design (+0x10), state present in ships[] both sides
(state != 0), and INTEGRITY NOT restored-to-max from a sub-max value
(a restored-to-20 after <20 = rebuild). The completion-leg signature
(aicode S7.4, static 0x41ded..0x41e19):
  P>0 -> P==0, b5d (byte +0x5d, hi byte of word 46) CLEARED to 0,
  ETA (+0x52 word 41) re-stamped; MOVES may zero or be re-granted.
Report classes:
  FULL  : P->0 AND b5d n->0 AND continuous          (the F8b observation)
  PART  : P->0 continuous, b5d unchanged            (burn/firing family)
Follow each FULL through ALL later samples of that slot: persistence,
next boundary power, ETA-vs-T. Prints raw rows for adjudication.
"""
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_stream  # noqa: E402

RUN = "/home/hrethric/projects/ascendancy/work/r1/playcap"
PW, INTG, MOV, ETA, OSW, DSG = 68, 70, 74, 41, 46, 8  # +0x10/2

prev = {}          # slot -> window
prev_m = {}        # slot -> (turn, owner, state, design)
full = []
part = Counter()
follow = {}        # slot -> list of "day:P:b5d:ETA" tail after a FULL

for j in r1_stream.observations(RUN, trust=True, stats={}):
    raw = j.get("ship_raw")
    if not raw:
        continue
    turn = j["turn"]
    smap = {s["slot"]: s for s in (j.get("ships") or [])}
    for slot_s, w in raw.items():
        slot = int(slot_s)
        p = prev.get(slot)
        m = smap.get(slot)
        if p is not None and m is not None:
            pm = prev_m.get(slot)
            cont = (pm and m["owner"] == pm[1] and m["state"] != 0
                    and pm[2] != 0 and m["design"] == pm[3])
            if slot in follow:
                follow[slot].append(
                    f"t{turn} P{w[PW]} b5d{hex(w[OSW] >> 8)}"
                    f" ETA{w[ETA]} own{m['owner']}")
            if p[PW] > 0 and w[PW] == 0 and cont:
                b5d_p, b5d_c = p[OSW] >> 8, w[OSW] >> 8
                if b5d_p != 0 and b5d_c == 0:
                    rec = (f"FULL {pm[0]}->{turn} slot{slot} own{m['owner']}"
                           f" dsg{m['design']} P{p[PW]}->0 "
                           f"I{p[INTG]}->{w[INTG]} M{p[MOV]}->{w[MOV]} "
                           f"ETA{p[ETA]}->{w[ETA]} b5d{hex(b5d_p)}->0")
                    full.append(rec)
                    follow[slot] = [rec.split()[1] + " P0 b5d0x0"
                                    f" ETA{w[ETA]} own{m['owner']}"]
                else:
                    part[(b5d_p, turn == pm[0])] += 1
        prev[slot] = w
        prev_m[slot] = (turn, m["owner"] if m else -1,
                        m["state"] if m else -1,
                        m["design"] if m else -1)

print(f"FULL (P->0 with order-state CLEARED, continuous record): "
      f"{len(full)}")
seen = set()
for r in full[:60]:
    key = r.split("slot")[1].split()[0] + r.split("->")[-1]
    slot = int(r.split("slot")[1].split()[0])
    if key in seen:
        continue
    seen.add(key)
    print(r)
    tail = follow.get(slot, [])
    # summary instead of raw head: days where P first returns >0, and the
    # P0 run's day-span (does the zero cross a turn boundary?)
    days0 = []
    first_back = None
    for t in tail[1:]:
        d = int(t.split()[0].lstrip("t"))
        p = int(t.split("P")[1].split()[0])
        if p == 0:
            days0.append(d)
        elif first_back is None:
            first_back = t
    span = f"P0 days {min(days0)}..{max(days0)}" if days0 else "no P0 tail"
    print(f"      SUMMARY {span}; first return>0: "
          f"{first_back or 'never in stream'}")
print(f"\nPART (P->0 continuous, b5d unchanged) by (b5d_before, same_day):")
for k in sorted(part):
    print(f"  b5d={hex(k[0])} same_day={k[1]}: {part[k]}")
