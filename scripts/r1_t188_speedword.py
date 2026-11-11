#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t188: speed-word hunt — why does slot 13 march 14/day while owner-1
slots 17/20/29 march 14/3/day at IDENTICAL MOVES=4 POW~10-12 des=4?

JSONL-only (no zip reads). For each turn's FIRST trusted row t in
[1255,1335]: record raw windows of the four lane slots (10,13,16,17) and
position series to 4 decimals. Then:
  (1) diff slot-13 vs slot-17 raw windows: offsets CONSTANT over turns
      within each slot but DIFFERENT between the two speed classes are
      speed-word candidates. Report every candidate with both values and
      any exact 3:1 / 1:3 ratio hit.
  (2) exact per-day displacement of slot 17 (is it 4.6667=14/3 or 4.67?).
"""
import sys, struct, math, collections
sys.path.insert(0, "/home/hrethric/projects/ascendancy/scripts")
import r1_stream

RUN = "/home/hrethric/projects/ascendancy/work/r1/playcap"
SLOTS = [10, 13, 16, 17]
first = {}                 # (turn,slot) -> bytes window
series = collections.defaultdict(list)
stat = {}
for j in r1_stream.observations(RUN, trust=True, stats=stat):
    t = j["turn"]
    if t < 1255 or t > 1335:
        continue
    raw = j.get("ship_raw") or {}
    for sl in SLOTS:
        w = raw.get(str(sl))
        if w and len(w) == 177:
            b = struct.pack("<177H", *w)
            first.setdefault((t, sl), b)
            x, y, z = struct.unpack_from("<3f", b, 0x9e)
            series[sl].append((t, x, y, z, b[0x58]))

turns = sorted({k[0] for k in first})
print(f"turns present: {len(turns)}  ({turns[0]}..{turns[-1]})")

# (2) exact displacement series
for sl in SLOTS:
    seq = [(t, x, y, z, st) for (t, x, y, z, st) in series[sl] if st == 5]
    # dedupe same-turn repeats (keep first per turn)
    seen, s2 = set(), []
    for r in seq:
        if r[0] not in seen:
            seen.add(r[0]); s2.append(r)
    print(f"\n-- slot {sl} state5 first-row series (4 dp) --")
    prev = None
    for (t, x, y, z, stv) in s2:
        line = f"  t{t} x={x:.4f} y={y:.4f} z={z:.4f}"
        if prev and t == prev[0] + 1:
            line += f"  stepx={x-prev[1]:.4f}"
        prev = (t, x)
        print(line)

# (1) within-slot stability + between-class diff
stable = {}
for sl in SLOTS:
    wins = [first[(t, sl)] for t in turns if (t, sl) in first]
    if not wins: continue
    stab = [all(w[o] == wins[0][o] and w[o+1] == wins[0][o+1] for w in wins) for o in range(0, 352, 2)]
    stable[sl] = (wins[0], stab)
print("\n-- candidate words: stable across turns in BOTH 13 and 17, but differ 13 vs 17 --")
if 13 in stable and 17 in stable:
    b13, s13 = stable[13]; b17, s17 = stable[17]
    for o in range(0, 352, 2):
        if s13[o // 2] and s17[o // 2] and b13[o:o+2] != b17[o:o+2]:
            v13 = struct.unpack_from("<H", b13, o)[0]
            v17 = struct.unpack_from("<H", b17, o)[0]
            f13 = struct.unpack_from("<f", b13, o)[0]
            r = ""
            if v17 and abs(v13 / v17 - 3) < 1e-9: r = "  <= 3:1 u16"
            if v13 and abs(v17 / v13 - 3) < 1e-9: r = "  <= 1:3 u16"
            try:
                if f13 == f13 and f13 != 0:
                    f17 = struct.unpack_from("<f", b17, o)[0]
                    if f17 == f17 and f17 != 0 and abs(f13 / f17 - 3) < 1e-6: r += "  <= 3:1 f32"
            except Exception:
                pass
            print(f"  +0x{o:02x}: slot13={v13} (0x{v13:04x}) slot17={v17} (0x{v17:04x}){r}")
