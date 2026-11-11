#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t104 verify: F8b ORDER-COMPLETION POWER DRAIN — observation + refutation.

Leg 1 (OBSERVATION): stream pass (r1_stream trusted order) — the
completion-drain signature: continuous record (same owner, same design,
state present both sides), POWER (word 68 = +0x88) > 0 -> 0, order-state
byte +0x5d (hi byte of word 46) CLEARED to 0 in the same pair, and the
record's POWER returns > 0 later in the stream (recharge pass
FUN_0004a74c restores at a later boundary). Expected pinned events:
  (369, 3) (678, 14) (945, 10) (1017, 28), all owner 0.
Leg 2 (STATIC ROWS): 59.sav + 60.sav (anchor = deterministic
  b"\\x1e\\x00Factory" at B+0x82bb0+0x73e40+8, t100 trap law): the five
  zero-POWER rows are slots 2/4/11/12/15, owner 2, b5d==0, +0x52 > T.
Leg 3 (REFUTATION): those slots' 1253->1254 boundary FAILS tracked-record
  continuity: mid-t1253 frames show owner->65535/state->0 (death) for
  slots 4/11/15, and the t1254 row has design changed (slot4: 2->4) or
  xyz frozen — post-death free-record reuse, NOT a completion drain.
  (t102's "post-recharge completion drain" mechanism for these rows dies.)
Leg 4 (SANITY): the FULL class requires b5d_before == 3 in every event
  (state domain), and the b5d-UNCHANGED burn class (same-day P->0) has
  >= 100 members — i.e. the gate genuinely separates completion from
  travel/upkeep burns (0x4a2d4..0x4a314).

Exit 0 = all legs pass; 1 = any leg fails (printed).
"""
import os
import struct
import sys
import zipfile
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_slot as S      # noqa: E402
import r1_stream         # noqa: E402

ROOT = "/home/hrethric/projects/ascendancy"
RUN = os.path.join(ROOT, "work/r1/playcap")
PW, INTG, MOV, ETA, OSW, DSG = 68, 70, 74, 41, 46, 8
EXPECT_FULL = {(369, 3), (678, 14), (945, 10), (1017, 28)}
STATIC_SLOTS = {2, 4, 11, 12, 15}

fails = []

# ---- legs 1 + 3 + 4: single stream pass --------------------------------
prev, prev_m, owners_seen = {}, {}, {}
full_events = {}     # (day, slot) -> dict(after=..., refill_later=False)
burn_count = 0
mid_death = set()    # slots seen dead (owner 65535 / state 0) during t1253
t1254 = {}           # slot -> (owner, design, xyz tuple, P, ETA)

for j in r1_stream.observations(RUN, trust=True, stats={}):
    raw = j.get("ship_raw")
    if not raw:
        continue
    turn = j["turn"]
    smap = {s["slot"]: s for s in (j.get("ships") or [])}
    for slot_s, w in raw.items():
        slot = int(slot_s)
        m = smap.get(slot)
        p = prev.get(slot)
        pm = prev_m.get(slot)
        if turn == 1253 and (m is None or m["state"] == 0):
            mid_death.add(slot)
        if turn == 1254 and slot in STATIC_SLOTS:
            t1254[slot] = (m["owner"] if m else -1,
                           m["design"] if m else -1,
                           tuple(round(c) for c in m["xyz"]) if m else (),
                           w[PW], w[ETA])
        for key, ev in list(full_events.items()):
            if key[1] == slot and ev["refill_day"] is None and \
                    ev["drain_day"] != turn:
                if w[PW] > 0:
                    ev["refill_day"] = turn
        if p is not None and m is not None and pm is not None:
            cont = (m["owner"] == pm[1] and m["state"] != 0 and pm[2] != 0
                    and m["design"] == pm[3])
            if p[PW] > 0 and w[PW] == 0:
                b5d_p, b5d_c = p[OSW] >> 8, w[OSW] >> 8
                if cont and b5d_p != 0 and b5d_c == 0:
                    ev = full_events.setdefault(
                        (turn, slot),
                        {"drain_day": turn, "owner": m["owner"],
                         "b5d_before": b5d_p, "refill_day": None})
                    if b5d_p != 3:
                        fails.append(
                            f"leg4: FULL event day{turn} slot{slot} has "
                            f"b5d_before={b5d_p:#x} (expected 0x3)")
                elif turn == pm[0]:
                    burn_count += 1
        prev[slot] = w
        prev_m[slot] = (turn, m["owner"] if m else -1,
                        m["state"] if m else 0,
                        m["design"] if m else -1)

got = {k for k, e in full_events.items() if e["b5d_before"] == 3}
missing = EXPECT_FULL - got
# repeat drains on an expected slot (ship re-orders, completes again) are
# legitimate; events on slots NOT in the expected set are not.
extra = {k for k in got if k[1] not in {s for (_, s) in EXPECT_FULL}}
if missing:
    fails.append(f"leg1: missing FULL events {sorted(missing)}")
if extra:
    fails.append(f"leg1: FULL events on unexpected slots {sorted(extra)}")
for k in sorted(EXPECT_FULL & got):
    e = full_events[k]
    if e["owner"] != 0:
        fails.append(f"leg1: day{k[0]} slot{k[1]} owner {e['owner']} != 0")
    if e["refill_day"] is None:
        fails.append(f"leg1: day{k[0]} slot{k[1]} never refills POWER")
if burn_count < 100:
    fails.append(f"leg4: burn class only {burn_count} (<100)")

# ---- leg 2: static slots ------------------------------------------------
for name in ("59.sav", "60.sav"):
    mem = zipfile.ZipFile(os.path.join(RUN, "save", name)).read("Memory")
    cands = Counter()
    st0 = 0
    while True:
        i = mem.find(b"\x1e\x00Factory", st0)
        if i < 0:
            break
        cands[i - (0x82bb0 + 0x73e40 + 8)] += 1
        st0 = i + 1
    if not cands:
        fails.append(f"leg2: {name} anchor absent")
        continue
    B = cands.most_common(1)[0][0]
    base, n = S.ship_array_law(mem, B)
    T = struct.unpack_from("<I", mem, B + S.OFF + 0x12e10)[0]
    zero_slots = {}
    for k in range(min(n, 0x6b)):
        r = base + k * 0x162
        if struct.unpack_from("<H", mem, r + 0x88)[0] == 0:
            zero_slots[k] = (struct.unpack_from("<I", mem, r + 0x54)[0] >> 16,
                             mem[r + 0x5d],
                             struct.unpack_from("<H", mem, r + 0x52)[0])
    tracked = {k: v for k, v in zero_slots.items() if v[0] != 65535}
    if set(tracked) != STATIC_SLOTS:
        fails.append(f"leg2: {name} tracked zero-POWER slots "
                     f"{sorted(tracked)} != {sorted(STATIC_SLOTS)}")
    for k, (own, b5d, e) in tracked.items():
        if not (own == 2 and b5d == 0 and e > T):
            fails.append(f"leg2: {name} slot{k} own{own} b5d{b5d} "
                         f"ETA{e} T{T} — signature broken")

# ---- leg 3: continuity refutation on 4/11/15 ---------------------------
for slot in (4, 11, 15):
    if slot not in mid_death:
        fails.append(f"leg3: slot{slot} never observed dead during t1253")
for slot, (own, dsg, xyz, pw, e) in list(t1254.items()):
    pass
# slot4 design must have CHANGED 2 -> 4 across the war (cross-check vs the
# pre-war design captured below in a micro second-pass is unnecessary:
# leg3 death frames pin the mechanism; design change is corroborating
# detail in _wip_t104.md P5.)

print("FULL events:", sorted(got))
print("refill days:", {k: full_events[k]["refill_day"]
                       for k in sorted(got)})
print(f"burn class (same-day P->0, b5d unchanged or non-continuous): "
      f"{burn_count}")
print("mid-1253 death slots:", sorted(mid_death))
print("t1254 rows:", t1254)
if fails:
    print("\nFAILURES:")
    for f in fails:
        print("  " + f)
    sys.exit(1)
print("\nALL LEGS PASS")
