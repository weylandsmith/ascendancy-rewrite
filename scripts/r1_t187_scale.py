#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t187: OQ-019 sugar-cube SCALE from the live flying sitting.

Turn-boundary law hunt: for each ship slot, snapshot position at the FIRST
trusted row of each turn; displacement between consecutive turn snapshots =
per-day travel. Pair it with the ship's own budget words read from the same
raw window (laws: MOVES [ship+0x94] re-granted to drive-sum, POWER/FUEL
[ship+0x88], state/kind byte [+0x58], order kind [+0x59], ETA [+0x52]).
Also dumps mid-turn walk interpolation for one busy slot to see the
per-resolver-call step pattern (t183 law: steps = round(walk), each step
(walk/steps)*160 world units along unit_dir).
Usage: r1_t187_scale.py <run_dir> <T0>
"""
import sys, struct, collections
sys.path.insert(0, "/home/hrethric/projects/ascendancy/scripts")
import r1_stream

RUN, T0 = sys.argv[1], int(sys.argv[2])
first = {}        # turn -> {slot: (xyz, state, moves, power, design, eta, k59, owner)}
last = {}
seq = collections.defaultdict(list)   # slot -> [(turn, xyz, state)] per FIRST-row
stat = {}

def snap(j):
    out = {}
    owners = {int(s["slot"]): s["owner"] for s in (j.get("ships") or [])}
    raw = j.get("ship_raw") or {}
    for k, w in raw.items():
        sl = int(k)
        if len(w) != 177:
            continue
        b = struct.pack("<177H", *w)
        state = b[0x58]
        if state == 0:
            continue
        s = owners.get(sl, -1)
        if s == 65535 or s < 0:
            continue
        xyz = struct.unpack_from("<3f", b, 0x9e)
        moves = struct.unpack_from("<I", b, 0x94)[0]
        power = struct.unpack_from("<I", b, 0x88)[0]
        design = struct.unpack_from("<I", b, 0x10)[0]
        eta = struct.unpack_from("<I", b, 0x52)[0]
        out[sl] = (xyz, state, moves, power, design, eta, b[0x59], s)
    return out

for j in r1_stream.observations(RUN, trust=True, stats=stat):
    t = j["turn"]
    if t < T0:
        continue
    s = snap(j)
    if t not in first:
        first[t] = s
    last[t] = s

turns = sorted(first)
print(f"turns {turns[0]}..{turns[-1]} ({len(turns)}) from {RUN}")
print("\n== per-day displacement at FIRST-row snapshots (moving slots only) ==")
ddist = collections.Counter()
for a, b in zip(turns, turns[1:]):
    if b != a + 1:
        continue
    for sl, v in last[a].items():
        w = first[b].get(sl)
        if w is None:
            print(f"  t{a}->{b} slot={sl} VANISHED (was state={v[1]} own={v[7]})")
            continue
        dx = w[0][0]-v[0][0]; dy = w[0][1]-v[0][1]; dz = w[0][2]-v[0][2]
        d2 = (dx*dx+dy*dy)**0.5
        if d2 < 1e-3 and abs(dz) < 1e-3:
            continue
        xy = round(d2, 2)
        ddist[(v[7], xy)] += 1
        print(f"  t{a}->{b} slot={sl:<3} own={v[7]} st {v[1]}->{w[1]} d=({dx:9.2f},{dy:9.2f},dz={dz:7.2f}) "
              f"|@t{a}: MOVES={v[2]} POW={v[3]} des={v[4]} ETA={v[5]} k59={v[6]} "
              f"|@t{b}: MOVES={w[2]} POW={w[3]} ETA={w[5]} k59={w[6]}")
print("\n== per-day |dxy| histogram (owner, value) ==")
for (own, xy), c in sorted(ddist.items()):
    print(f"   own={own} |d|={xy}: x{c}")

# mid-turn interpolation: pick slot with most first-row movement
busy = collections.Counter()
for a, b in zip(turns, turns[1:]):
    if b != a + 1:
        continue
    for sl, v in last[a].items():
        w = first[b].get(sl)
        if w and ((w[0][0]-v[0][0])**2+(w[0][1]-v[0][1])**2)**0.5 > 1e-3:
            busy[sl] += 1
print(f"\nbusiest moving slots: {busy.most_common(5)}")
print("\n== FULL position series (ALL trusted rows) for busiest slot, t>=T0 ==")
if busy:
    sl = busy.most_common(1)[0][0]
    prev = None
    for j in r1_stream.observations(RUN, trust=True, stats={}):
        t = j["turn"]
        if t < T0:
            continue
        w = (j.get("ship_raw") or {}).get(str(sl))
        if w is None or len(w) != 177:
            continue
        b2 = struct.pack("<177H", *w)
        if b2[0x58] == 0:
            continue
        x, y, z = struct.unpack_from("<3f", b2, 0x9e)
        mv = struct.unpack_from("<I", b2, 0x94)[0]
        pw = struct.unpack_from("<I", b2, 0x88)[0]
        line = f"t={t} st={b2[0x58]} k59={b2[0x59]} xy=({x:.3f},{y:.3f}) z={z:.1f} MOVES={mv} POW={pw}"
        if prev is not None:
            d = ((x-prev[0])**2+(y-prev[1])**2)**0.5
            line += f" step={d:.4f}"
        print("  " + line)
        prev = (x, y)
