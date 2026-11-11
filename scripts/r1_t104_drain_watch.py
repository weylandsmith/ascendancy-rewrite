#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t104: F8b ORDER-COMPLETION POWER-BOUNDARY CENSUS over the banked playcap.

Closure target (docs/re/aicode.md S7.4): the static completion leg
0x41ded..0x41e19 zeroes WORD [ship+0x88] (POWER) and WORD [ship+0x94]
(MOVES), folding the delta into a stack budget; the arrival leg 0x41d80
decls [ship+0x88]. Attribution is cited statically; strict-close demands
the OBSERVATION: a tracked record showing POWER>0 -> POWER==0 across
consecutive captured samples.

Method (r1_stream laws: trusted order, dedup, stale-drop). Per ship slot
we track the five words that matter (u16 index = byte offset / 2):
  68 POWER (+0x88)   70 INTEGRITY (+0x8c)   74 MOVES (+0x94)
  41 ETA (+0x52)     46 ORDER byte: +0x5d state (lo) / +0x5c (hi)
Every consecutive trusted pair (prev -> cur) is classified boundary
(turn+1) / same-turn / jump. For EACH SLOT a drain (P>0 -> P==0) is
followed on the NEXT pair involving that slot:
  persisted   still P==0 (post-recharge drain — the static 59/60 rows'
              signature: zero survives the per-turn recharge pass)
  refilled    P>0 again (drain then recharge/restock between samples)
Prints counts by owner x pair-kind x persistence and the first raw
tuples for manual adjudication. READ-ONLY stream pass.
"""
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_stream  # noqa: E402

RUN = "/home/hrethric/projects/ascendancy/work/r1/playcap"
PW, INTG, MOV, ETA, OSW = 68, 70, 74, 41, 46

prev = {}            # slot -> (turn, P, I, M, ETA, b5d, b5c, owner)
awaiting = {}        # slot -> drain record (kind, tuple_prev, tuple_cur)
owners = {}
drain_res = Counter()   # (owner, kind, persisted|refilled) -> n
drain_unres = Counter()
refill = Counter()      # (owner, kind) -> power==0 -> power>0 transitions
persist_samples = []
sample_counts = {}
samples = []
pairs = Counter()
zero_slots_at_boundary = Counter()   # owner -> slots observed P==0 b-day rows
rows = 0

for j in r1_stream.observations(RUN, trust=True, stats={}):
    raw = j.get("ship_raw")
    if not raw:
        continue
    rows += 1
    turn = j["turn"]
    for s in (j.get("ships") or []):
        owners[s["slot"]] = s["owner"]
    for slot_s, w in raw.items():
        slot = int(slot_s)
        p = prev.get(slot)
        cur = (turn, w[PW], w[INTG], w[MOV], w[ETA], w[OSW] & 0xFF,
               w[OSW] >> 8, owners.get(slot, -1))
        if p is not None:
            kind = ("boundary" if turn == p[0] + 1 else
                    "same" if turn == p[0] else "jump")
            pairs[kind] += 1
            if kind == "boundary" and cur[1] == 0:
                zero_slots_at_boundary[cur[7]] += 1
            aw = awaiting.get(slot)
            if aw is not None:
                # resolve the pending drain on THIS pair
                r = "persisted" if cur[1] == 0 else "refilled"
                drain_res[(aw[2][7], aw[0], r)] += 1
                if r == "persisted" and len(persist_samples) < 40:
                    persist_samples.append(
                        f"{aw[0]} drain day{aw[2][0]}->{aw[2][0]+1} slot{slot}"
                        f" still0 at day{cur[0]} M={cur[3]} ETA={cur[4]}"
                        f"(T{'+ahead' if cur[4] > cur[0] else '<='})"
                        f" b5d={cur[6]:#x}")
                awaiting.pop(slot)
            if p[1] > 0 and cur[1] == 0 and kind in ("boundary", "same"):
                awaiting[slot] = (kind, p, cur)
                bkey = (cur[7], kind)
                kept = sample_counts.get(bkey, 0)
                if kept < 12 and len(samples) < 200:
                    sample_counts[bkey] = kept + 1
                    samples.append(
                        f"{kind} day{p[0]}->{cur[0]} slot{slot} own{cur[7]} "
                        f"P{p[1]}->0 I{p[2]}->{cur[2]} M{p[3]}->{cur[3]} "
                        f"ETA{p[4]}->{cur[4]} "
                        f"b5c{p[5]:#x}->{cur[5]:#x} b5d{p[6]:#x}->{cur[6]:#x}")
            elif p[1] == 0 and cur[1] > 0:
                refill[(cur[7], kind)] += 1
        prev[slot] = cur

print(f"rows with ship_raw: {rows}")
print(f"pair kinds: {dict(pairs)}")
print("\n== DRAIN power>0 -> power==0, resolution on next sample ==")
if not drain_res and not drain_unres:
    print("NONE")
for k in sorted(drain_res):
    print(f"  owner={k[0]} {k[1]:9s} next-sample={k[2]}: {drain_res[k]}")
for k in sorted(drain_unres):
    print(f"  owner={k[0]} {k[1]:9s} UNRESOLVED: {drain_unres[k]}")
print("\ndrain samples (raw tuples):")
for s in samples:
    print("  " + s)
print("\ndrain -> PERSISTED samples (zero survives recharge — static "
      "59/60.sav signature):")
for s in persist_samples:
    print("  " + s)
print("\n== REFILL power==0 -> power>0 ==")
for k in sorted(refill):
    print(f"  owner={k[0]} {k[1]}: {refill[k]}")
print("\nslots observed at POWER==0 on boundary pairs, by owner:")
for k in sorted(zero_slots_at_boundary):
    print(f"  owner {k}: {zero_slots_at_boundary[k]}")
