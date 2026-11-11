#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t249b S2: day-counter dword census.

Leg A: in work/r1/bank-t1254/*.sav (all 20 slots, all turn 1254), find every
4-aligned dword == VALUE (default 1254) and INTERSECT offsets across slots.
A real game-state field lives at a stable member offset in every slot; heap
noise does not survive intersection.

Leg B (cross-session correlation, decisive): data-segment offsets X are stable
across SESSIONS (obj1 data is part of the relocated image, guest index
B+0x82bb0+X — pointer law OQ-011 CLOSED). So for each surviving candidate X,
read X in the LIVE ring (turn ~1086): a day counter must read ~1086 there, the
turn field reads its own session's turn. A candidate constant across sessions
is not a counter.

Exit 0 = candidates found (print list); 1 = none; 2 = harness error.
"""
import os, struct, sys, zipfile, glob, json, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_slot as S

OFF = S.OFF  # 0x82bb0
BANK = "work/r1/bank-t1254"
LIVE = "work/r1/playcap/save"


def load(root):
    pay = S.load_payload(root)
    return S.anchors_cached(root, pay)


def slot_mem(path, anch):
    try:
        mem = zipfile.ZipFile(path).read("Memory")
    except Exception:
        return None, None
    if len(mem) < 0x90000:
        return None, None
    B = S.base_of(mem, anch)
    return (mem, B) if B else (None, None)


def main():
    root = os.getcwd()
    val = int(sys.argv[1]) if len(sys.argv) > 1 else 1254
    anch = load(root)

    paths = sorted(glob.glob(os.path.join(BANK, "*.sav")), key=os.path.getmtime)
    sets = []
    turns = []
    mems = {}
    for p in paths:
        mem, B = slot_mem(p, anch)
        if mem is None:
            print(f"  skip {os.path.basename(p)}", file=sys.stderr)
            continue
        turns.append(struct.unpack_from("<I", mem, B + OFF + 0x12e10)[0])
        # dword scan over the WHOLE member at 4-alignment relative to member start
        hits = set()
        n = len(mem) - 3
        for i in range(0, n, 4):
            if struct.unpack_from("<I", mem, i)[0] == val:
                hits.add(i)
        sets.append(hits)
        mems[p] = (mem, B)
    if not sets:
        print("no readable slots")
        return 2
    inter = set.intersection(*sets)
    print(f"slots={len(sets)} turns={sorted(set(turns))} value={val}")
    print(f"per-slot hit counts: min={min(len(s) for s in sets)} "
          f"max={max(len(s) for s in sets)} intersection={len(inter)}")

    # member offset -> image data offset X when inside the data window
    B0 = mems[paths[0]][1][0] if False else None
    Bref = mems[paths[0]][1]
    cands = []
    for m in sorted(inter):
        X = m - (Bref + OFF)
        region = "DATA" if 0 <= X < 0xa0d3 else ("LOW" if m < Bref + OFF else "HIGH")
        cands.append((m, X, region))
    print(f"stable candidates ({len(cands)}):")
    for m, X, region in cands:
        print(f"  member {hex(m)}  X={hex(X) if X>=0 else X}  {region}")

    # Leg B: read candidates in live ring slots
    live = sorted(glob.glob(os.path.join(LIVE, "*.sav")), key=os.path.getmtime)[-6:]
    live_rows = []
    for p in live:
        mem, B = slot_mem(p, anch)
        if mem is None:
            continue
        t = struct.unpack_from("<I", mem, B + OFF + 0x12e10)[0]
        row = {"file": os.path.basename(p), "turn": t}
        for m, X, region in cands:
            if region == "DATA":
                row[f"X{hex(X)}"] = struct.unpack_from("<I", mem, B + OFF + X)[0]
        live_rows.append(row)
    print("live ring reads (DATA candidates only):")
    for r in live_rows:
        print(" ", json.dumps(r))
    return 0 if cands else 1


if __name__ == "__main__":
    sys.exit(main())
