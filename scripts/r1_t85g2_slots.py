#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t85g2: per-slot offset trace through the t1253/1254 engagement.
Tracks every u16 that changes per ship slot t>=1244, with turn and
(owner,state) context, plus the FULL 1253->1254 relation diff."""
import sys
sys.path.insert(0, "/home/hrethric/projects/ascendancy/scripts")
import r1_stream

RUN = "/home/hrethric/projects/ascendancy/work/r1/playcap"
TARGETS = [2, 4, 11, 12, 15, 19, 21, 23]          # Ungooma slots that died
PLAYER_SLOTS = list(range(32, 41))

first_at = {}
rows = []          # (turn, wall, slot, off, old, new, owner_before, state_before)
prev = None        # (turn, raw, owners, states, designs)

for j in r1_stream.observations(RUN, trust=True, stats={}):
    t = j["turn"]
    raw = j.get("ship_raw") or {}
    ships = {s["slot"]: s for s in j.get("ships") or []}
    owners = {k: v["owner"] for k, v in ships.items()}
    states = {k: v["state"] for k, v in ships.items()}
    designs = {k: v["design"] for k, v in ships.items()}
    if t >= 1250 and t not in first_at:
        rel = j.get("relation") or None
        if rel:
            first_at[t] = rel
    if t >= 1244 and prev is not None:
        for slot_s, w in raw.items():
            sl = int(slot_s)
            if sl not in TARGETS and sl not in PLAYER_SLOTS:
                continue
            pw = prev[1].get(slot_s)
            if pw is None or len(pw) != len(w):
                continue
            for k in range(len(w)):
                if w[k] != pw[k]:
                    rows.append((t, j.get("wall", ""), sl, 2 * k, pw[k], w[k],
                                 prev[2].get(sl), prev[3].get(sl)))
    prev = (t, raw, owners, states, designs)

nm = first_at.get(1254, {}).get("names", "?")
print("== FULL relation diff 1253 -> 1254 (states or |att|>=5 change) ==")
s53, a53 = first_at[1253]["states"], first_at[1253]["atts"]
s54, a54 = first_at[1254]["states"], first_at[1254]["atts"]
for i in range(len(nm)):
    for k in range(len(nm)):
        if i == k:
            continue
        msg = ""
        if s53[i][k] != s54[i][k]:
            msg += f" STATE {s53[i][k]}->{s54[i][k]}"
        if abs(a54[i][k] - a53[i][k]) >= 5:
            msg += f" att {a53[i][k]}->{a54[i][k]}"
        if msg:
            print(f"  {nm[i]:>10s} -> {nm[k]:<10s}{msg}")

print("\n== per-slot u16 changes t>=1244 (slot, off, old->new, owner_before, state_before) ==")
cur = None
for t, wall, sl, off, o, n, own, st in rows:
    if (t, sl) != cur:
        cur = (t, sl)
        print(f"\n  -- t={t} slot={sl} (owner_before={own} state_before={st}) --")
    print(f"     +0x{off:02x}: {o} -> {n}")
