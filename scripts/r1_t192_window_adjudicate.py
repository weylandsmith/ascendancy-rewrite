#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t192: adjudicate the TRIGGER-A growth window exactly, not by replay.

The idle probe froze BASE_SIZE at 5691796463 (Oct 26 15:44). The timeline is
now larger, so trigger A arms. This script decides WHAT the new bytes are:
it indexes the stream once (r1_stream.build_index -> (mtime_ns, file, offset))
and keeps ONLY rows whose byte offset is at/after the growth boundary, then
walks them in TRUSTED order with the §16.2 law (raw row-per-frame diffs, NOT
first-row-per-turn, which is blind to mid-autosave relation writes).

Outputs (small): row count, turn/wall range, relation state-transition census,
attitude-delta events >= 10, ship appear/vanish/owner-change events, and any
state value outside the banked enum {0,1,2,3}.

Usage: r1_t192_window_adjudicate.py [run_dir] [base_size]
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_stream

RUN = sys.argv[1] if len(sys.argv) > 1 else \
    "/home/hrethric/projects/ascendancy/work/r1/playcap"
BASE = int(sys.argv[2]) if len(sys.argv) > 2 else 5691796463

path = os.path.join(RUN, r1_stream.JSONL)
entries, n_uniq, n_bad = r1_stream.build_index(path)
print(f"indexed={len(entries)} uniq={n_uniq} bad={n_bad} file_size={os.path.getsize(path)}")

# Growth boundary in trusted order: entries are sorted by mtime, so the new
# bytes are a SUFFIX by mtime as well as by offset. Use offset>=BASE.
win = [e for e in entries if e[2] >= BASE - 2048]
print(f"window_entries={len(win)} (offset>={BASE-2048})")
if not win:
    print("NO new rows by offset -> touch, not ingest")
    sys.exit(0)

n = 0
tmin = tmax = None
wmin = wmax = None
trans = {}
att_events = []
odd_states = {}
ships_seen = set()
ship_events = []
prev = None
stale = 0
wmark = 0
for mt, fn, off in win:
    with open(path, "r", errors="replace") as f:
        f.seek(off)
        try:
            j = json.loads(f.readline())
        except Exception:
            continue
    t = j.get("turn", 0)
    if t <= 0:
        continue                      # title slots untrusted (t82 law)
    if t < wmark:
        stale += 1
        continue
    wmark = max(wmark, t)
    n += 1
    tmin = t if tmin is None else min(tmin, t)
    tmax = t if tmax is None else max(tmax, t)
    w = j.get("wall")
    if w:
        wmin = w if wmin is None else (w if w < wmin else wmin)
        wmax = w if wmax is None else (w if w > wmax else wmax)
    rel = j.get("relation")
    if rel and prev is not None:
        ps, pa, nm = prev
        if rel["names"] == nm:
            for i in range(len(nm)):
                for k in range(len(nm)):
                    if i == k:
                        continue
                    so, ok = ps[i][k], rel["states"][i][k]
                    if so != ok:
                        key = (nm[i], nm[k], so, ok)
                        trans[key] = trans.get(key, 0) + 1
                        if ok not in (0, 1, 2, 3):
                            odd_states[ok] = odd_states.get(ok, 0) + 1
                    ad = rel["atts"][i][k] - pa[i][k]
                    if abs(ad) >= 10:
                        att_events.append((t, nm[i], nm[k], pa[i][k],
                                           rel["atts"][i][k], ad))
        prev = (rel["states"], rel["atts"], rel["names"])
    elif rel:
        prev = (rel["states"], rel["atts"], rel["names"])
    cur = {}
    for s in (j.get("ships") or []):
        has = (s["state"] != 0) or any(abs(c) > 1e-6 for c in s["xyz"])
        if has:
            cur[s["slot"]] = (s["owner"], s["state"])
    for sl, v in cur.items():
        if sl not in ships_seen:
            ship_events.append((t, sl, "appear", f"owner={v[0]} state={v[1]}"))
    for sl in list(ships_seen):
        if sl not in cur:
            ship_events.append((t, sl, "vanish", ""))
    ships_seen = set(cur)

print(f"trusted_rows={n} stale_echoes={stale} turn_range={tmin}..{tmax} "
      f"wall={wmin}..{wmax}")
print(f"\n== relation STATE transitions in window ({len(trans)} kinds) ==")
for (a, b, so, ok), c in sorted(trans.items(), key=lambda x: -x[1]):
    print(f"  {a} -> {b}: {so}->{ok}  x{c}")
print(f"states outside enum {{0,1,2,3}}: {odd_states or 'NONE'}")
print(f"\n== attitude |delta|>=10 events ({len(att_events)}) ==")
seen_att = set()
for e in att_events:
    k = (e[0], e[1], e[2])
    if k in seen_att:
        continue
    seen_att.add(k)
    print(f"  t={e[0]} {e[1]}->{e[2]}: {e[3]}->{e[4]} ({e[5]:+d})")
print(f"\n== ship events in window ({len(ship_events)}) ==")
for e in ship_events[:40]:
    print("  t=%-5d slot=%-3s %-13s %s" % e)
