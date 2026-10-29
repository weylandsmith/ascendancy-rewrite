#!/usr/bin/env python3
"""t187: adjudicate the 2026-10-28/29 play session (t1253..end) from the ring.

Answers, with cited frame numbers:
 1. score_stars (DAT_482fb) trajectory vs systems_full/systems_any  (player
    reported the 'c' STARS CONTROLLED drifting 14 -> 21 while 'planets' showed 36)
 2. Orfa attitude cells BOTH orientations (atts[0][i] and atts[i][0]) + relation
    states: find the first 2->1 (WAR->PEACE?) transition == the reported alliance
    acceptance at disposition 605 (refusals at 590/595).
 3. ship flights: continuous xyz deltas between consecutive frames for the same
    slot+owner == OQ-019 flight-delta evidence (the missing sub-residue).
Streaming; trust=True skips poisoned frames. Small stdout.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_stream

RUN = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "work/r1/playcap")
T0 = 1253

prev_t = None
frames = 0
score_rows = []          # (turn, score_stars, any, full)
orfa_rows = []           # (turn, att0i, atti0, st0i, sti0)
names_seen = None
ship_prev = {}           # slot -> (owner, x, y, z, turn)
flights = []             # (turn, slot, owner, dx, dy, dz) distinct deltas
delta_hist = {}          # (slot) -> counter of rounded speed per frame-step

for j in r1_stream.observations(RUN, trust=True, stats={}):
    t = j.get("turn")
    if t is None or t < T0:
        continue
    rel = j.get("relation") or {}
    names = rel.get("names") or []
    if names and names_seen is None:
        names_seen = names
    score_rows.append((t, j.get("score_stars"), j.get("systems_any"),
                       j.get("systems_full")))
    if "Orfa" in names and rel.get("atts"):
        i = names.index("Orfa")
        try:
            a0i = rel["atts"][0][i]
            ai0 = rel["atts"][i][0]
        except Exception:
            a0i = ai0 = None
        try:
            s0i = rel["states"][0][i]
            si0 = rel["states"][i][0]
        except Exception:
            s0i = si0 = None
        orfa_rows.append((t, a0i, ai0, s0i, si0))
    # ship flight deltas (per-frame; same-slot same-owner continuous coords)
    for s in j.get("ships") or []:
        sl = s["slot"]
        own = s["owner"]
        x, y, z = s["xyz"]
        cur = ship_prev.get(sl)
        if cur and cur[0] == own and t != cur[4]:
            dx, dy, dz = x - cur[1], y - cur[2], z - cur[3]
            if abs(dx) > 1e-6 or abs(dy) > 1e-6 or abs(dz) > 1e-6:
                flights.append((t, sl, own, round(dx, 3), round(dy, 3),
                                round(dz, 3)))
        ship_prev[sl] = (own, x, y, z, t)
    if t != prev_t:
        prev_t = t
        frames += 1

print("NAMES:", names_seen)
print("distinct turns t>=%d: %d   last turn: %s" % (T0, frames, score_rows[-1][0] if score_rows else None))

print("\n== score_stars / systems_any / systems_full trajectory (deduped) ==")
seen = set()
for t, sc, an, fu in score_rows:
    k = (sc, an, fu)
    if k in seen:
        continue
    seen.add(k)
    print("  t=%s score_stars=%s any=%s full=%s" % (t, sc, an, fu))

print("\n== Orfa cells trajectory (deduped) ==")
seen = set()
for t, a0i, ai0, s0i, si0 in orfa_rows:
    k = (a0i, ai0, s0i, si0)
    if k in seen:
        continue
    seen.add(k)
    print("  t=%s att0i=%s atti0=%s state0i=%s statei0=%s" % (t, a0i, ai0, s0i, si0))

print("\n== relation-state transition events (any pair, deduped cells) ==")
# re-walk states for transitions across ALL pairs (cheap: reuse stored rows? no,
# states matrix not stored; do a second streaming pass confined to states)

print("\n== ship flight deltas (first 40) ==")
for f in flights[:40]:
    print("  t=%s slot=%s owner=%s d=(%s,%s,%s)" % f)
print("flight-delta frames total:", len(flights))
