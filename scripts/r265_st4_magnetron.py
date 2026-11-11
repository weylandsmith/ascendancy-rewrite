#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t265 — OQ-019 live mining on the t261 DRIVE corpus (one pass).

Corpus law (measured at t265 intake): production :9 drove turns 1086->1236 on
2026-11-01 21:24 .. 2026-11-02 01:27; live-timeline.jsonl carries the rows.
Selection = file_mtime_ns inside the drive epoch (the ONLY robust selector:
wall collides across days, the global r1_stream watermark drops the whole
session because older corpus rows reach t=1335 — t251 rewind caveat), dedup
by (file, file_mtime_ns) (orphan-watcher law t259), in_game AND turn>0.
OOM law: bounded tail region via seek, json.loads ONE row at a time.

Two witnesses in one pass:

W1 st4 MID-TURN DISPLACEMENT (the t193 premise re-test). t193's 2238 st4
   samples had zero displacement but the turn NEVER advanced. Here: for every
   pair of consecutive trusted rows WITHIN THE SAME TURN, and separately at
   turn boundaries, measure st4 ([+0x58]==4) ship displacement from [+0x9e]
   f32 xyz. Also census on-grid (x,z exact multiples of 32, S21 quantizer law)
   vs off-grid st4 positions — off-grid st4 is the magnetron-placed signature
   (0x21f58 adds rng%200 jitter; P(both offsets %32==0) ~ 2.5%), on-grid is
   the walk/system-grid signature.

W2 MAGNETRON USE FRAMES. Magnetron = cidx 60 (ships.md S19 T1). Use-site law
   (S19 T3, 0x4cd5c case 0x3c): [+0x58]:=5, [+0x59]:=star ptr, placement
   0x21f58 (y := y-200.0 exactly; other two axes += rng%200), then the ship
   continues as st4. Frame signature between consecutive rows (any turn
   relation): slot st->5 with a big displacement (>300u, S21 big-mover bound)
   AND after-state y in [-200.0, 0.0) (the -200.0 offset + jitter can never
   reach 0 or go below -200) AND after-state x/z NOT both on the 32-grid.
   Lane-march st5 rows (y exactly 0/1, z on-grid, step<=56) are the control
   class and are counted separately, never reported as W2.

Exit 0 always (honest negatives are findings). usage: r265_st4_magnetron.py
"""
import json, os, struct, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
JSONL = os.path.join(ROOT, "work/r1/playcap/live-timeline.jsonl")

LO = time.mktime(time.strptime("2026-11-01 21:20:00", "%Y-%m-%d %H:%M:%S"))
HI = time.mktime(time.strptime("2026-11-02 01:59:00", "%Y-%m-%d %H:%M:%S"))
LO_NS, HI_NS = int(LO * 1e9), int(HI * 1e9)
TAIL_SEEK = 420_000_000          # bounded region (OOM law); verified to cover window
BIG = 300.0                       # S21 big-mover bound


def grid(v):
    q = v / 32.0
    return abs(q - round(q)) < 1e-4


def snap(j):
    out = {}
    for k, w in (j.get("ship_raw") or {}).items():
        if len(w) != 177:
            continue
        b = struct.pack("<177H", *w)
        st = b[0x58]
        if st == 0:
            continue
        # owner index byte = ship+0x56 (cite: magnetron case 0x3e ORs
        # 1<<(ship+0x56) into target[+0x17], ships.md S19 T3)
        own = b[0x56]
        if own == 0xFF:
            own = -1
        x, y, z = struct.unpack_from("<3f", b, 0x9e)
        out[int(k)] = (st, b[0x59], x, y, z, own,
                       struct.unpack_from("<I", b, 0x94)[0],
                       struct.unpack_from("<I", b, 0x88)[0])
    return out


def main():
    size = os.path.getsize(JSONL)
    seen = set()
    prev = None                  # (mt, turn, wall, snap)
    n_rows = 0
    st4_seen = set()             # (turn, slot) samples
    mid_pairs = 0                # consecutive SAME-turn row pairs
    mid_moves = []               # (turn, slot, d, from, to)
    bound_moves = []             # turn-boundary st4 displacement
    grid_c = {"on": 0, "off": 0}
    offgrid_samples = []
    w2 = []                      # magnetron-frame candidates
    st5_control = 0              # lane-march st5 rows (y 0/1, on-grid z)
    st5_other = 0
    turn_hist = {}

    with open(JSONL, "r", errors="replace") as f:
        f.seek(max(0, size - TAIL_SEEK))
        f.readline()             # partial line
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
            ig = '"in_game": true' in line
            if not ig or turn <= 0:
                continue
            # dedup key (file, mtime_ns)
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
            turn_hist[turn] = turn_hist.get(turn, 0) + 1
            wall = ob.get("wall", "?")
            s = snap(ob)

            for sl, v in s.items():
                if v[0] == 4:
                    st4_seen.add((turn, sl))
                    on = grid(v[2]) and grid(v[4])
                    grid_c["on" if on else "off"] += 1
                    if not on and len(offgrid_samples) < 12:
                        offgrid_samples.append(
                            f"t{turn} {wall} slot={sl} own={v[5]} "
                            f"xy=({v[2]:.3f},{v[3]:.3f}) z={v[4]:.1f}")
                elif v[0] == 5:
                    if (abs(v[3]) < 1e-4 or abs(v[3] - 1.0) < 1e-4) and grid(v[4]):
                        st5_control += 1
                    else:
                        st5_other += 1

            if prev is not None:
                pmt, pturn, pwall, ps = prev
                same_turn = (turn == pturn)
                if same_turn:
                    mid_pairs += 1
                for sl, v in s.items():
                    pv = ps.get(sl)
                    if pv is None:
                        continue
                    dx = v[2] - pv[2]; dy = v[3] - pv[3]; dz = v[4] - pv[4]
                    d = (dx * dx + dy * dy + dz * dz) ** 0.5
                    # W1: st4 displacement (either endpoint state 4)
                    if v[0] == 4 or pv[0] == 4:
                        if d > 1e-3:
                            rec = (turn, sl, d,
                                   f"t{pturn} st{pv[0]} ({pv[2]:.1f},{pv[3]:.1f},{pv[4]:.0f}) k59={pv[1]} mv={pv[6]}",
                                   f"t{turn} st{v[0]} ({v[2]:.1f},{v[3]:.1f},{v[4]:.0f}) k59={v[1]} mv={v[6]}")
                            (mid_moves if same_turn else bound_moves).append(rec)
                    # W2: magnetron placement frame
                    if v[0] == 5 and d > BIG:
                        y_ok = -200.0 <= v[3] < 0.0
                        off = not (grid(v[2]) and grid(v[4]))
                        if y_ok and off:
                            w2.append((turn, sl, d,
                                       f"t{pturn} st{pv[0]} ({pv[2]:.1f},{pv[3]:.1f},{pv[4]:.0f})",
                                       f"t{turn} st5 ({v[2]:.3f},{v[3]:.3f},{v[4]:.1f}) own={v[5]} k59={v[1]}"))
            prev = (mt, turn, wall, s)

    print(f"rows={n_rows} unique, turns {min(turn_hist)}..{max(turn_hist)}, "
          f"{len(turn_hist)} distinct turns")
    print(f"st4 samples (turn,slot)={len(st4_seen)}  row-level st4 "
          f"on-grid={grid_c['on']} off-grid={grid_c['off']}")
    print(f"st5 row-level: lane-control-class(y in 0/1 & z on-grid)={st5_control} "
          f"other={st5_other}")
    print(f"\n== W1 st4 MID-TURN displacement (same-turn consecutive rows): "
          f"{mid_pairs} pairs, {len(mid_moves)} moved ==")
    for r in mid_moves[:40]:
        print(f"  t{r[0]} slot={r[1]} d={r[2]:.2f}  {r[3]} -> {r[4]}")
    print(f"\n== W1b st4 TURN-BOUNDARY displacement: {len(bound_moves)} moved ==")
    for r in bound_moves[:40]:
        print(f"  t{r[0]} slot={r[1]} d={r[2]:.2f}  {r[3]} -> {r[4]}")
    print("\n== off-grid st4 samples ==")
    for s in offgrid_samples:
        print("  " + s)
    print(f"\n== W2 magnetron-frame candidates: {len(w2)} ==")
    for r in w2[:20]:
        print(f"  t{r[0]} slot={r[1]} d={r[2]:.1f}  {r[3]} -> {r[4]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
