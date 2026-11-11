#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t188 arbiter: state-3 cells + proposal frames, RAW per-row (not first-per-turn).

t187_delta said zero state-3 in t1255..1335; r1_t187_session (deduped dump over
ALL rows) saw states [3,3] at t=1335 with att bump +10. Difference hypothesis:
the sitting scripts take only the FIRST row of each turn, so mid-turn writes
(alliance made mid-turn-1335, mid-autosave) are invisible to them. This pass
walks EVERY trusted row and reports any frame with a 3 cell, plus the frames
where att0i/atti0 changed (proposal bumps), with wall-clock timestamps.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_stream

RUN = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "work/r1/playcap")

n3 = 0
prev_att = None
for j in r1_stream.observations(RUN, trust=True, stats={}):
    t = j.get("turn")
    if t is None or t < 1300:
        continue
    rel = j.get("relation") or {}
    names = rel.get("names") or []
    if "Orfa" not in names:
        continue
    i = names.index("Orfa")
    st = rel.get("states") or []
    flat = [c for row in st for c in row]
    wall = j.get("wall", "")
    if 3 in flat:
        n3 += 1
        if n3 <= 6 or n3 % 50 == 0:
            print("STATE3 t=%s wall=%s cell0i=%s celli0=%s flat3count=%d" %
                  (t, wall, st[0][i] if st else None,
                   st[i][0] if len(st) > i else None, flat.count(3)))
    att = rel.get("atts") or []
    try:
        cur = (att[0][i], att[i][0])
    except Exception:
        cur = None
    if cur and cur != prev_att:
        print("ATT-CHANGE t=%s wall=%s att0i=%s atti0=%s state0i=%s" %
              (t, wall, cur[0], cur[1], st[0][i] if st else None))
        prev_att = cur
print("total trusted rows t>=1300 with any 3-cell:", n3)
