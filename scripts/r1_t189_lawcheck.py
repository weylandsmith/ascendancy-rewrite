#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t189: verify the lane-step law found statically in FUN_0004a74c.

Static law (disasm 0x4a824..0x4a8af): st5 march does
    x := min(x + step, lane_len);  step = float([ship+0x8] + [ship+0xc])
                                    [* moffs0x263b if handle byte +0x23 bit0]
                                    [* moffs0x263f if species row == 0x12]
This script, from the trusted JSONL rows (first per turn, slots 10,13,16,
17,16,22,26,30,34, t 1255..1335):
  (1) per-slot st5 x-series: does consecutive delta == [ship+8]+[ship+0xc]
      EXACTLY (the base law)? report raw values either way.
  (2) slot13 vs slot17: dump +0x8,+0xc,+0x54 (species idx >>16),
      +0x59 handle, and handle u16 at +0x52 (S21's route word).
  (3) species idx equality test between fast (14) and slow (14/3) slots;
      if SLOW slots have row idx whose table col == 0x12 we need the save
      table; otherwise the multiplier is the handle byte.
"""
import sys, struct, collections
sys.path.insert(0, "/home/hrethric/projects/ascendancy/scripts")
import r1_stream

RUN = "/home/hrethric/projects/ascendancy/work/r1/playcap"
SLOTS = [10, 13, 16, 17, 20, 22, 26, 29, 30, 34]

first = {}   # (turn,slot) -> bytes
stat = {}
for j in r1_stream.observations(RUN, trust=True, stats=stat):
    t = j["turn"]
    if t < 1250 or t > 1340:
        continue
    raw = j.get("ship_raw") or {}
    for sl in SLOTS:
        w = raw.get(str(sl))
        if w and len(w) == 177 and (t, sl) not in first:
            first[(t, sl)] = struct.pack("<177H", *w)

def f32(b, o):  return struct.unpack_from("<f", b, o)[0]
def u32(b, o):  return struct.unpack_from("<I", b, o)[0]
def u16(b, o):  return struct.unpack_from("<H", b, o)[0]

# (1)+(2) per-slot series with the law check
law_hits = collections.Counter()
info = {}
for sl in SLOTS:
    turns = sorted(t for (t, s) in first if s == sl)
    rows5 = []
    for t in turns:
        b = first[(t, sl)]
        if b[0x58] == 5:
            rows5.append((t, f32(b, 0x9e), u32(b, 8), u32(b, 0xc),
                          u32(b, 0x54), u32(b, 0x59), u16(b, 0x52)))
    if not rows5:
        print(f"slot {sl}: no st5 rows")
        continue
    info[sl] = rows5
    print(f"-- slot {sl}: {len(rows5)} st5 rows --")
    prev = None
    for (t, x, a, c, sp, h, w52) in rows5[:26]:
        d = None if prev is None else x - prev[1]
        base = float(a + c)
        tag = ""
        if prev is not None and d is not None and t == prev[0] + 1:
            if abs(d - base) < 1e-4: tag = "BASE-LAW-EXACT"
            else: tag = f"delta/base={d/base if base else float('nan'):.6f}"
        print(f"  t{t} x={x:10.4f} d={'' if d is None else f'{d:9.4f}'} "
              f"[+8]={a} [+0c]={c} base={base:8.2f} sp={sp>>16} "
              f"h={h:#x} w52={w52} {tag}")
        prev = (t, x)

# (3) species / handle comparison across speed classes
print("\n-- speed-class comparison (majority step per slot) --")
for sl in SLOTS:
    if sl not in info: continue
    rows = info[sl]
    deltas = collections.Counter()
    for i in range(1, len(rows)):
        if rows[i][0] == rows[i-1][0] + 1:
            deltas[round(rows[i][1]-rows[i-1][1], 4)] += 1
    sp = {r[4] >> 16 for r in rows}
    hs = {r[5] for r in rows}
    w52 = {r[6] for r in rows}
    ba = {(r[2], r[3]) for r in rows}
    print(f"slot {sl}: deltas {dict(deltas)} species {sp} handles { {h&0xffffff:x for h in hs} } w52 {w52} +8/+c {ba}")
print("RC OK")
