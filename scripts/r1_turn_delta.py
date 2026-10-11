#!/usr/bin/env python3
"""r1_turn_delta.py — OQ-016 income-APPLICATION law from turn bracket.

Reads the ck/ timeline of an r1ad run whose driver advanced turns (turns.log
'slot turn N'). For consecutive DISTINCT turns t -> t+1 and every owned
record: report channel words +0x44/+0x46/+0x48 (stored IND/RES/PROS),
+0x42 pop, +0x4e growth counter, +0x1c/+0x1e, pending item word (+0x52..
+0x54 region banked t39) and the stockpile hint (global ind word if found).
Output is a per-planet per-turn delta table: the raw material for fitting
the application law (accum -> stored) at ONE-turn resolution.

Usage: r1_turn_delta.py <run-dir>
"""
import os, struct, struct as st, sys, zipfile, collections

R = "/home/hrethric/projects/ascendancy"
sys.path.insert(0, R + "/scripts")
from r1_sav_scan import build_anchors, find_base

FIELDS = {"ind": 0x44, "res": 0x46, "pros": 0x48, "pop": 0x42,
          "gcnt": 0x4e, "cap": 0x4a, "c1c": 0x1c, "c1e": 0x1e}

def owned_view(mem, pay):
    v, _ = find_base(mem, build_anchors(pay))
    if not v:
        return None
    H = v.most_common(1)[0][0] - 0x1BF450
    base = 0x26d07b + H - 0x24
    out = {}
    for i in range(151):
        b = base + 123 * i
        owner = mem[b + 0x57]
        if owner == 0xFF:
            continue
        name = mem[b + 0x24:b + 0x24 + 13].split(b"\x00")[0].decode("cp437", "replace")
        rec = {k: st.unpack_from("<H", mem, b + o)[0] for k, o in FIELDS.items()}
        rec["owner"] = owner
        # pending item: +0x52 word (0xFFFF idle per t39 census)
        rec["pend"] = st.unpack_from("<H", mem, b + 0x52)[0]
        out[name] = rec
    return out

def main():
    run = sys.argv[1]
    pay = open(R + "/work/ascend_payload.bin", "rb").read()
    # map turn -> ck file via turns.log (slot names; ck.log maps slot->ck)
    slot2ck = {}
    for line in open(os.path.join(run, "ck.log")):
        s, _, c = line.partition(" -> ")
        slot2ck[s.strip()] = c.strip().replace(".sav", "")
    turn_lines = []
    for line in open(os.path.join(run, "turns.log")):
        parts = line.split()
        if len(parts) >= 3 and parts[1] == "turn":
            try:
                turn_lines.append((int(parts[2]), os.path.basename(parts[0])))
            except ValueError:
                pass  # TORN / NOBASE lines
    views = {}
    for t, slot in sorted(turn_lines):
        ckn = slot2ck.get(slot)
        if not ckn:
            continue
        f = os.path.join(run, "ck", ckn + ".sav")
        if not os.path.exists(f):
            continue
        try:
            mem = zipfile.ZipFile(f).read("Memory")
        except Exception:
            print(ckn, "TORN"); continue
        ov = owned_view(mem, pay)
        if ov is None:
            print(ckn, "NOBASE"); continue
        views.setdefault(t, ov)  # first ck per turn wins
    ts = sorted(views)
    print("turns captured:", ts)
    for a, b in zip(ts, ts[1:]):
        print(f"--- turn {a} -> {b} ---")
        for name in sorted(set(views[a]) | set(views[b])):
            ra, rb = views[a].get(name), views[b].get(name)
            if ra is None:
                print(f"  +{name} NEW owner {rb['owner']:#x} pop {rb['pop']} cap {rb['cap']} ch {rb['ind']},{rb['res']},{rb['pros']}")
                continue
            if rb is None:
                print(f"  -{name} LOST")
                continue
            d = {k: rb[k] - ra[k] for k in FIELDS}
            chg = {k: (ra[k], rb[k]) for k in FIELDS if d[k]}
            pend = (f"pend {ra['pend']:#x}->{rb['pend']:#x}"
                    if ra["pend"] != rb["pend"] else "")
            if chg or pend:
                print(f"  {name} owner {rb['owner']:#x}", chg, pend)
        # global: owner-count and total pop
        ta = sum(r["pop"] for r in views[a].values())
        tb = sum(r["pop"] for r in views[b].values())
        print(f"  TOTAL pop {ta} -> {tb}; owned {len(views[a])} -> {len(views[b])}")

if __name__ == "__main__":
    main()
