#!/usr/bin/env python3
"""r255d_persession.py — OQ-021: V=DAT_482fb change classification with
PER-SESSION trust (the global watermark law of r1_stream wrongly drops every
row of a campaign re-loaded at a LOWER turn — which is exactly what happened
on Nov-1 (t251 drive from t1086 after the Oct-28 sitting reached 1335);
r1_stream's own docstring caveat says such rewinds are real).

Pipeline: dedup (file, mtime_ns) -> split sessions on mtime gap > 600 s ->
per-session stale-echo watermark -> classify each consecutive trusted pair:
  TURN-CHANGE  turn advanced, V changed
  MID-TURN     same turn, V changed          <-- the screen-open signature
  V=0 rows are reported separately (title/title-like slot class).
"""
import sys, datetime
from collections import defaultdict
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
    if j < 0:
        return None
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
        if turn is None or mt is None:
            continue
        if (fn, mt) in seen:
            continue
        seen.add((fn, mt))
        rows.append((mt, fn, turn,
                     get_int(head, '"score_stars": '),
                     get_int(head, '"selector_byte": '),
                     get_int(tail, '"systems_any": '),
                     get_int(tail, '"systems_full": '),
                     get_int(tail, '"planets_mine": ')))
rows.sort()
print(f"unique_rows={len(rows)}")

# sessions by mtime gap
sessions = []
prev = None
for r in rows:
    if prev is not None and (r[0] - prev[0]) / 1e9 > 600:
        sessions.append([])
    if not sessions:
        sessions.append([])
    sessions[-1].append(r)
    prev = r

grand_mid = []
grand_turn = []
for k, s in enumerate(sessions):
    # per-session stale-echo law (stale-instance autosaves lag within a sitting)
    trusted, wm2, nstale = [], 0, 0
    for r in s:
        if r[2] <= 0:
            continue
        if r[2] < wm2:
            nstale += 1
            continue
        wm2 = max(wm2, r[2])
        trusted.append(r)
    d0 = datetime.datetime.fromtimestamp(s[0][0]/1e9)
    d1 = datetime.datetime.fromtimestamp(s[-1][0]/1e9)
    z = [r for r in trusted if r[3] == 0]
    nz = [r for r in trusted if r[3]]
    mid, tch = [], []
    prevT = None
    for r in nz:
        if prevT is not None and r[3] != prevT[3]:
            rec = (r[2], prevT[3], r[3], r[1], prevT[1], r[5], r[6])
            (mid if r[2] == prevT[2] else tch).append(rec)
        prevT = r
    grand_mid += [(k,) + m for m in mid]
    grand_turn += [(k,) + m for m in tch]
    sel = [r for r in trusted if r[4]]
    hi = [r for r in trusted if r[3] and r[3] >= 25]
    print(f"S{k:02d} {d0:%m-%d %H:%M}..{d1:%m-%d %H:%M} turns {s[0][2]}..{s[-1][2]} "
          f"n={len(s)} trusted={len(trusted)} stale={nstale} Vrange="
          f"{min(r[3] for r in nz) if nz else '-'}..{max(r[3] for r in nz) if nz else '-'} "
          f"zero_rows={len(z)}(turns {sorted({r[2] for r in z})[:8]}) "
          f"MIDTURN={len(mid)} TURNCHG={len(tch)} sel>0={len(sel)} V>=25={len(hi)}")
    for m in mid[:12]:
        print("   MID:", m)

print(f"\nTOTAL MIDTURN={len(grand_mid)} TURNCHG={len(grand_turn)}")
print("\nALL MID-TURN CHANGES (turn, prevV, V, file, prevfile, any, full):")
for m in grand_mid:
    print("  ", m)

# cross-session same-turn V disagreement (per-session trusted)
per = defaultdict(dict)
for k, s in enumerate(sessions):
    wm2 = 0
    for r in s:
        if r[2] <= 0 or r[2] < wm2:
            continue
        wm2 = max(wm2, r[2])
        if r[3]:
            per[r[2]].setdefault(k, set()).add(r[3])
dis = {t: {k: sorted(v) for k, v in d.items()}
       for t, d in per.items() if len(set().union(*d.values())) > 1}
print(f"\nturns where sessions DISAGREE on V: {len(dis)}")
for t in sorted(dis)[:40]:
    print("  t", t, dis[t])
