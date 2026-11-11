#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t85c focused pass: testimony-vs-ring adjudication. Output -> stdout (small)."""
import sys
sys.path.insert(0, "/home/hrethric/projects/ascendancy/scripts")
import r1_stream

run = "/home/hrethric/projects/ascendancy/work/r1/playcap"
L = []
def p(*a):
    L.append(" ".join(str(x) for x in a))

prev = None
prev_t = None
transitions = []          # (turn, i, j, old, jname/i-name)
att_orfa = []             # (turn, att[0][1], att[1][0], state[0][1])
score_traj = []           # (turn, score, any, full)
ship_events = []          # (turn, slot, kind, detail)
present = {}              # slot -> (owner, state, xyz) last-known PRESENT view
n_rows = 0

for j in r1_stream.observations(run, trust=True, stats={}):
    t = j["turn"]
    if t == prev_t:
        continue
    prev_t = t
    n_rows += 1
    rel = j.get("relation") or None
    if rel and prev and rel.get("names") == prev.get("names") \
       and len(rel["states"]) == len(prev["states"]):
        nm = rel["names"]
        for i in range(len(nm)):
            for k in range(len(nm)):
                o, w = prev["states"][i][k], rel["states"][i][k]
                if o != w:
                    transitions.append((t, nm[i], nm[k], o, w))
    if rel:
        try:
            att_orfa.append((t, rel["atts"][0][1], rel["atts"][1][0],
                             rel["states"][0][1]))
        except Exception:
            pass
    if n_rows % 12 == 1:
        score_traj.append((t, j.get("score_stars"), j.get("systems_any"),
                           j.get("systems_full")))
    # ship presence per law: record present iff state byte nonzero OR xyz nonzero
    for s in j.get("ships") or []:
        sl = s["slot"]
        has = (s["state"] != 0) or any(abs(c) > 1e-6 for c in s["xyz"])
        o = s["owner"]
        cur = present.get(sl)
        if has:
            if cur is None or cur[0] != o:
                ship_events.append((t, sl, "appear" if cur is None else
                                    "owner-change",
                                    f"{cur} -> owner={o} state={s['state']}"))
            present[sl] = (o, s["state"])
        else:
            if cur is not None:
                ship_events.append((t, sl, "vanish", f"was owner={cur[0]} state={cur[1]}"))
                present.pop(sl, None)
    prev = rel

p(f"turn-change rows: {n_rows}")
p("\n== state transitions (whole capture) ==")
for x in transitions:
    p("  t=%-5d %s->%s  %d->%d" % x)
p("\n== Chamachies<->Orfa (att self->orfa, att orfa->self, state cell) sampled ==")
last = None
for t, a01, a10, s01 in att_orfa:
    if (t, a01, a10, s01) != last and (last is None or abs(t - last[0]) >= 20 or s01 != last[3] or a01 != last[1]):
        p(f"  t={t:<5d} att01={a01:<5d} att10={a10:<5d} state01={s01}")
        last = (t, a01, a10, s01)
p(f"  FINAL: t={att_orfa[-1][0]} att01={att_orfa[-1][1]} att10={att_orfa[-1][2]} state01={att_orfa[-1][3]}")
p("\n== score/progress trajectory ==")
for t, sc, an, fu in score_traj:
    p(f"  t={t:<5d} score={sc} any={an} full={fu}")
p(f"\n== ship events ({len(ship_events)}) ==")
for e in ship_events[:60]:
    p("  t=%-5d slot=%-3d %-14s %s" % e)
if len(ship_events) > 60:
    p(f"  ... {len(ship_events)-60} more")
sys.stdout.write("\n".join(L) + "\n")
