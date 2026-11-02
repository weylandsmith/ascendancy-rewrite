#!/usr/bin/env python3
"""t265 pass 3 — CLEAN-drive-only span analysis (drop softlock windows).

Pass-2 lesson: the corpus contains THREE regimes: (i) the healthy drive
21:24->~21:38 (t1086..1111) and 23:07->01:27 (t1112..1236 minus the stuck
presses), (ii) softlock window 1 21:38..~22:20 (RAM profile t1255, turn
reported 1111 then title), (iii) softlock window 2 / oscillation ~23:50..01:27
(t1254<->t1255 rows interleaved INSIDE the mtime window; t1236 x2080 rows =
the parked parked-session tail). Same-turn pairs computed globally were
contaminated by (ii)/(iii) — the 4 "mid-turn moves" all sit at wall
21:41..21:54 = window (ii).

This pass: bucket rows by wall-clock regime FIRST, then per (slot, turn-run)
spans within the clean drive only:
  F. st4 span census: (slot, turn-run) spans with start/end turn, length in
     turns, net displacement over the span, k59 at entry/exit.
     -> measures in-system DWELL time and whether st4 EVER moves in-system.
  G. st5 span entry-x law: first-row x at lane entry (S21 claim x == step).
  H. st5 per-turn delta values (t189 law check: delta == step0 or step0/3).
Regime buckets (wall, from the pass-1/2 evidence + t261 wip):
  DRIVE_A 21:24:00..21:37:59   (t1086..1111 healthy)
  SOFT1   21:38:00..23:06:59   (title/softlock + relaunch gap)
  DRIVE_B 23:07:00..23:49:59   (re-drive healthy until oscillation starts)
  OSC     23:50:00..01:59:00   (t1254<->t1255 interleaving + parked tail)
DRIVE_B's upper bound is [inferred] from t1236's row count; spans crossing it
are reported with the regime tag so the reader can veto.
usage: r265_pass3.py ; exit 0 always
"""
import json, os, struct, sys, time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
JSONL = os.path.join(ROOT, "work/r1/playcap/live-timeline.jsonl")
LO_NS = int(time.mktime(time.strptime("2026-11-01 21:20:00", "%Y-%m-%d %H:%M:%S")) * 1e9)
HI_NS = int(time.mktime(time.strptime("2026-11-02 01:59:00", "%Y-%m-%d %H:%M:%S")) * 1e9)
TAIL_SEEK = 420_000_000

# Regime boundaries as LOCAL DATETIMES (pass-3 first attempt compared wall
# strings lexicographically: "23:07:00" <= "01:59:00" is FALSE, so every row
# after 23:07 fell out of B into OSC. mtime_ns is the trusted clock.)
import datetime as _dt
B_START = _dt.datetime(2026, 11, 1, 23, 7, 0)
S1_START = _dt.datetime(2026, 11, 1, 21, 38, 0)
A_START = _dt.datetime(2026, 11, 1, 21, 24, 0)


def regime(mt):
    d = _dt.datetime.fromtimestamp(mt / 1e9)
    if d >= B_START:
        return "B"
    if d >= S1_START:
        return "S1"
    if d >= A_START:
        return "A"
    return "PRE"


def snap(j):
    out = {}
    for k, w in (j.get("ship_raw") or {}).items():
        if len(w) != 177:
            continue
        b = struct.pack("<177H", *w)
        st = b[0x58]
        if st == 0:
            continue
        x, y, z = struct.unpack_from("<3f", b, 0x9e)
        out[int(k)] = (st, b[0x59], x, y, z, b[0x56])
    return out


def main():
    size = os.path.getsize(JSONL)
    seen = set()
    rows = []
    with open(JSONL, "r", errors="replace") as f:
        f.seek(max(0, size - TAIL_SEEK))
        f.readline()
        for line in f:
            i = line.find('"file_mtime_ns": ')
            if i < 0:
                continue
            j = line.find(",", i)
            mt = int(line[i + 17:j])
            if not (LO_NS <= mt <= HI_NS):
                continue
            i = line.find('"turn": ')
            j = line.find(",", i)
            turn = int(line[i + 8:j])
            if '"in_game": true' not in line or turn <= 0:
                continue
            fi = line.find('"file": "')
            fn = line[fi + 8:line.find('"', fi + 8)] if fi >= 0 else "?"
            key = (fn, mt)
            if key in seen:
                continue
            seen.add(key)
            try:
                ob = json.loads(line)
            except Exception:
                continue
            rows.append((mt, turn, ob.get("wall", "?"), snap(ob)))
    rows.sort(key=lambda r: r[0])

    # per-regime turn histograms (validate the bucketing)
    th = defaultdict(Counter)
    for mt, t, w, s in rows:
        th[regime(mt)][t] += 1
    for rg in "AS1B O".replace(" ", ""):
        ts = sorted(th[rg])
        if ts:
            print(f"regime {rg}: {sum(th[rg].values())} rows, turns {ts[0]}..{ts[-1]}, "
                  f"distinct {len(ts)}")

    # spans: per regime, per slot, consecutive rows (any turn) -> state-run
    spans = defaultdict(list)     # (regime, slot) -> list of open/closed runs
    openrun = {}                  # (rg, slot) -> [st, first(mt,t,x,y,z,k59), last(...), n]
    for mt, t, w, s in rows:
        rg = regime(mt)
        for sl, v in s.items():
            k = (rg, sl)
            run = openrun.get(k)
            if run and run[0] == v[0]:
                run[2] = (mt, t, v[2], v[3], v[4], v[1])
                run[3] += 1
                continue
            if run:
                spans[k].append(run)
            openrun[k] = [v[0], (mt, t, v[2], v[3], v[4], v[1]),
                          (mt, t, v[2], v[3], v[4], v[1]), 1]
        # close slots that VANISHED this row (dead/despawn) -> close their runs
        for k in list(openrun):
            if k[0] != rg:
                spans[k].append(openrun.pop(k))
            elif k[1] not in s:
                spans[k].append(openrun.pop(k))
    for k, run in openrun.items():
        spans[k].append(run)

    print("\n== F. st4 runs in DRIVE regimes (rows>=2), net displacement ==")
    n4 = moved4 = 0
    multi_turn_zero = 0
    for (rg, sl), runs in sorted(spans.items()):
        if rg not in "AB":
            continue
        for st, a, b, n in runs:
            if st != 4 or n < 2:
                continue
            n4 += 1
            d = ((b[2] - a[2]) ** 2 + (b[3] - a[3]) ** 2 + (b[4] - a[4]) ** 2) ** 0.5
            tspan = b[1] - a[1]
            if d > 1e-3:
                moved4 += 1
            line = (f"  {rg} slot={sl} t{a[1]}..{b[1]} (tspan={tspan}) rows={n} "
                    f"d={d:.2f} k59 {a[5]}->{b[5]}")
            print(line)
            if tspan >= 1 and d <= 1e-3:
                multi_turn_zero += 1
    print(f"  st4 multi-row runs A+B: {n4}, moved: {moved4}, "
          f"MULTI-TURN-ZERO (spanned >=1 turn advance, no displacement): {multi_turn_zero}")

    print("\n== F2. st4 run LENGTH census (rows) by regime ==")
    lc = defaultdict(Counter)
    for (rg, sl), runs in spans.items():
        for st, a, b, n in runs:
            if st == 4:
                lc[rg][min(n, 50)] += 1
    for rg in "AS1B":
        print(f"  {rg}: {dict(sorted(lc[rg].items()))}")

    print("\n== G/H. st5 runs in DRIVE regimes: entry x + per-row x deltas ==")
    entry_x = Counter()
    xdelta = Counter()
    for (rg, sl), runs in sorted(spans.items()):
        if rg not in "AB":
            continue
        for st, a, b, n in runs:
            if st != 5 or n < 2:
                continue
            entry_x[round(a[2], 4)] += 1
    # per-row deltas need row order within the run; recompute quickly,
    # SPLIT same-turn vs turn-boundary (W1: same-turn delta must be 0 if the
    # march is turn-tail-atomic; boundary delta == step if the st5 law holds)
    openrun2 = {}
    prev_row = None
    xdelta_same = Counter()
    xdelta_bound = Counter()
    for mt, t, w, s in rows:
        rg = regime(mt)
        same_turn = prev_row is not None and prev_row[1] == t
        if rg not in "AB":
            prev_row = (mt, t, s)
            openrun2.clear()
            continue
        for k in list(openrun2):
            if k[0] != rg or k[1] not in s or openrun2[k][0] != s[k[1]][0]:
                openrun2.pop(k)
        for sl, v in s.items():
            if v[0] != 5:
                continue
            k = (rg, sl)
            prev = openrun2.get(k)
            if prev:
                dlt = round(abs(v[2] - prev[1][2]), 4)
                (xdelta_same if same_turn else xdelta_bound)[dlt] += 1
            openrun2[k] = [5, v]
        prev_row = (mt, t, s)
    print(f"  entry-x values (st5 runs>=2 rows, A+B): {dict(entry_x.most_common(15))}")
    print(f"  SAME-turn consecutive x-deltas (st5, A+B): {dict(xdelta_same.most_common(15))}")
    print(f"  TURN-BOUNDARY consecutive x-deltas (st5, A+B): {dict(xdelta_bound.most_common(15))}")

    print("\n== I. S1-window st4 mid-turn moves (bug-class witness for t266) ==")
    prev = None
    seen_osc = Counter()
    for mt, t, w, s in rows:
        if regime(mt) != "S1":
            prev = None
            continue
        if prev is not None and prev[1] == t:
            for sl, v in s.items():
                pv = prev[2].get(sl)
                if pv is None:
                    continue
                d = ((v[2] - pv[2]) ** 2 + (v[3] - pv[3]) ** 2 + (v[4] - pv[4]) ** 2) ** 0.5
                if d > 1e-3 and (v[0] == 4 or pv[0] == 4):
                    seen_osc[(sl, round(d, 1))] += 1
        prev = (mt, t, s)
    print(f"  {dict(seen_osc.most_common(20))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
