#!/usr/bin/env python3
"""t265 pass 2 — aggregated st4 motion + magnetron hunt on the drive corpus.

Same corpus law as pass 1 (r265_st4_magnetron.py): mtime inside the drive
epoch 2026-11-01 21:20..2026-11-02 01:59, dedup (file, mtime_ns), in_game,
turn>0, bounded tail seek (OOM law), one json per line.

Aggregations (pass-1's 40-row prints hid the distribution):
  A. per-turn mid-turn stats: pairs, st4-moved pairs (the t193 re-test bucketed).
  B. wall-clock span of every st4 MID-TURN move (softlock-window check:
     the t1254<->t1255 oscillation is the known bug window, NOT a drive leg).
  C. st4->st4 TURN-BOUNDARY displacement histogram (the in-system per-turn
     step law candidate; +0x9e f32, exact values).
  D. boundary transition-class histogram (stX->st' with big/small d).
  E. per-turn st4 sample counts (drive legs vs softlock legs).
Exit 0 always. usage: r265_pass2.py
"""
import json, os, struct, sys, time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
JSONL = os.path.join(ROOT, "work/r1/playcap/live-timeline.jsonl")
LO_NS = int(time.mktime(time.strptime("2026-11-01 21:20:00", "%Y-%m-%d %H:%M:%S")) * 1e9)
HI_NS = int(time.mktime(time.strptime("2026-11-02 01:59:00", "%Y-%m-%d %H:%M:%S")) * 1e9)
TAIL_SEEK = 420_000_000
BIG = 300.0


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
    prev = None
    mid_pairs = Counter()          # turn -> same-turn consecutive row pairs
    mid_st4_moved = Counter()      # turn -> st4-moved events within turn
    mid_move_walls = []            # (turn, wall, slot, d)
    hist44 = Counter()             # st4->st4 boundary |d| rounded 2dp
    hist44_axis = Counter()        # (dx,dy,dz) quantised for st4->st4 moves
    trans = Counter()              # (stX, st', big?) boundary transition classes
    st4_turns = Counter()          # turn -> st4 row-level samples
    n_rows = 0
    w2 = []

    def grid32(v):
        q = v / 32.0
        return abs(q - round(q)) < 1e-4

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
            n_rows += 1
            wall = ob.get("wall", "?")
            s = snap(ob)
            for v in s.values():
                if v[0] == 4:
                    st4_turns[turn] += 1
            if prev is not None:
                pturn, pwall, ps = prev
                if turn == pturn:
                    mid_pairs[turn] += 1
                    for sl, v in s.items():
                        pv = ps.get(sl)
                        if pv is None:
                            continue
                        d = ((v[2] - pv[2]) ** 2 + (v[3] - pv[3]) ** 2
                             + (v[4] - pv[4]) ** 2) ** 0.5
                        if d > 1e-3 and (v[0] == 4 or pv[0] == 4):
                            mid_st4_moved[turn] += 1
                            mid_move_walls.append((turn, wall, sl, round(d, 2), pwall))
                elif turn == pturn + 1:
                    for sl, v in s.items():
                        pv = ps.get(sl)
                        if pv is None:
                            continue
                        dx = round(v[2] - pv[2], 2); dy = round(v[3] - pv[3], 2)
                        dz = round(v[4] - pv[4], 2)
                        d = (dx * dx + dy * dy + dz * dz) ** 0.5
                        big = d > BIG
                        trans[(pv[0], v[0], big)] += 1
                        if pv[0] == 4 and v[0] == 4 and d > 1e-3:
                            hist44[round(d, 2)] += 1
                            hist44_axis[(dx, dy, dz)] += 1
                # W2 magnetron frame (any turn relation)
                if prev is not None:
                    pturn0, pwall0, ps0 = prev
                    for sl, v in s.items():
                        pv = ps0.get(sl)
                        if pv is None or v[0] != 5:
                            continue
                        d = ((v[2] - pv[2]) ** 2 + (v[3] - pv[3]) ** 2
                             + (v[4] - pv[4]) ** 2) ** 0.5
                        if (d > BIG and -200.0 <= v[3] < 0.0
                                and not (grid32(v[2]) and grid32(v[4]))):
                            w2.append((turn, wall, sl, round(d, 1)))
            prev = (turn, wall, s)

    print(f"rows={n_rows}")
    print("\n== A. mid-turn pairs vs st4-moved per turn (nonzero-move turns) ==")
    for t in sorted(mid_st4_moved):
        print(f"  t{t}: pairs={mid_pairs[t]} st4_moved={mid_st4_moved[t]}")
    print(f"  (turns with mid-turn pairs: {len(mid_pairs)}; "
          f"total pairs {sum(mid_pairs.values())}; total st4 moves {sum(mid_st4_moved.values())})")
    print("\n== B. st4 mid-move wall timestamps ==")
    for r in mid_move_walls[:60]:
        print(f"  t{r[0]} wall {r[4]} -> {r[1]} slot={r[2]} d={r[3]}")
    print("\n== C. st4->st4 boundary |d| histogram (top 30) ==")
    for d, c in hist44.most_common(30):
        print(f"  |d|={d}: x{c}")
    print("\n== C2. st4->st4 (dx,dy,dz) top 20 ==")
    for a, c in hist44_axis.most_common(20):
        print(f"  {a}: x{c}")
    print("\n== D. boundary transition classes (stX,st',big) ==")
    for k, c in sorted(trans.items()):
        print(f"  {k}: x{c}")
    print("\n== E. st4 samples per turn (top 25) ==")
    for t, c in st4_turns.most_common(25):
        print(f"  t{t}: x{c}")
    print(f"\n== W2 magnetron candidates: {len(w2)} ==")
    for r in w2[:20]:
        print("  " + str(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
