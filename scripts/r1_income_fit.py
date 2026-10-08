#!/usr/bin/env python3
"""r1_income_fit.py — candidate-model scoring for the colony income law
(OQ-016 income half) against guest RAM. Companion to r1_income_law.py.

Disassembly baseline (work/ascend_restored.bin, FUN_00038ba4 @0x38ba4,
full-function dump 2026-10-07, byte-authoritative):
planet record stride 123, base = NAME - 0x24; slot array = u32 at [rec+0x10]
RAW (0x38c8b uses [EBX+0x10]+4*i directly); slot dword {byte0 terrain class
(+0x8 impassable bit), byte1 itemIdx (0xff empty), u16 flags @+2 bit0
ACTIVE bit1 skip}. item table stride 0x28 at Ghidra 0x73e40 -> B+0x82BB0+
0x73e40: byte0 IND, byte1 RES, byte2 PROS, byte4 -> orbital channel.

Accumulation (active slots only, 0x38cbe..0x38d1f):
  A += item.b0, +1 if slot cls==2   (IND channel)
  P += item.b2, +1 if slot cls==3   (PROS channel)
  R += item.b1, +1 if slot cls==4   (RES channel, NEVER pow-compressed)
  O += item.b4 (orbital; governor 0x23 adds byte@0x743b9)
Slot flags word @item+6: bit2 -> extra per-slot scan (+0x58 count), bit3 ->
+0x59 counter; itemIdx==0x17 (Ship) skips orbital sub-branch.

Doubling @0x38d3f..0x38df0: FUN_0003958c finds FIRST slot with itemIdx==k
(k=12 IND, 13 PROS, 14 RES); caller requires that slot's ACTIVE bit; v +=
v>>1 once.
Governor byte @+0x54: 0x21 P+=A>>2 ; 0x22 R+=A>>2 ; 0x23 O+=byte@0x743b9.
Compression @0x38e2d/0x38e5e: A and P only, V!=0 -> V = trunc((V+1)^0.85)
(FILD/pow/RET/FISTP; t18b verified chop semantics).
Upkeep i16 @+0x42: P = max(0, P - (|upk| >> 2))  [0x38e8d..0x38eb0].
Stores: +0x44=A +0x46=R +0x48=P ; +0x1c=buildable-empty +0x20=zero-class
+0x1e=beyond-cells counts (ONLY meaningful after recalc ran; fresh
placements write these from setup code with different semantics).
Clamps @0x38f01..: +0x4a in [0,100], +0x42>=0, +0x4c<=+0x42.

Exit 0 only if a model hits >=95% IND+PROS+RES equality on fitted records.
"""
import argparse, math, os, re, struct as st, sys, zipfile
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAY = os.path.join(ROOT, "work", "ascend_payload.bin")
ITEM_STRIDE, N_ITEMS = 0x28, 39
REC = 123
NAME_AT = 0x24
CELLS = {7, 11, 23, 45, 73}
RUNS = sorted(os.path.join(ROOT, "work", "r1", x)
              for x in os.listdir(os.path.join(ROOT, "work", "r1"))
              if os.path.isdir(os.path.join(ROOT, "work", "r1", x, "save")))


def trunc85(v):
    """RET at 0x76e08 = trunc (0x78954 is RINT; verified disasm 2026-10-07)."""
    return int(v ** 0.85)


def item_table(m, B):
    idx = B + 0x82BB0 + 0x73E40
    if idx <= 0 or idx + N_ITEMS * ITEM_STRIDE > len(m):
        return None
    rows = []
    for k in range(N_ITEMS):
        b = idx + k * ITEM_STRIDE
        rows.append({
            "name": m[b + 10:b + 40].split(b"\x00")[0].decode("cp437", "replace").strip(),
            "ind": st.unpack_from("<b", m, b + 0)[0],
            "res": st.unpack_from("<b", m, b + 1)[0],
            "pros": st.unpack_from("<b", m, b + 2)[0],
            "orb": st.unpack_from("<B", m, b + 4)[0],
            "flags": st.unpack_from("<H", m, b + 6)[0],
        })
    return rows


def names_ok(rows):
    want = {22: "Shipyard", 23: "Ship", 24: "Orbital Docks",
            12: "Hyperpower Plant", 13: "Fertilization Plant", 14: "Internet"}
    return all(rows[k]["name"] == v for k, v in want.items())


NAME_RE = re.compile(rb"[A-Za-z0-9 '^_.-]{3,20}\x00")


def find_records(m):
    starts = defaultdict(list)
    pos = 0
    while True:
        mm = NAME_RE.search(m, pos)
        if not mm:
            break
        starts[mm.start() % REC].append(mm.start())
        pos = mm.start() + 1

    def cells_ok(base):
        cells = st.unpack_from("<H", m, base + 0x18)[0]
        cap = st.unpack_from("<H", m, base + 0x1a)[0]
        return cells in CELLS and cap == cells + 10

    best = []
    for mod, s in starts.items():
        s = sorted(s)
        chain, cur = [], [s[0]]
        for a, b in zip(s, s[1:]):
            if b - a == REC:
                cur.append(b)
            else:
                if len(cur) > len(chain):
                    chain = cur
                cur = [b]
        if len(cur) > len(chain):
            chain = cur
        if sum(1 for n in chain if cells_ok(n - NAME_AT)) > \
           sum(1 for n in best if cells_ok(n - NAME_AT)):
            best = chain
    return [n - NAME_AT for n in best if cells_ok(n - NAME_AT)]


def fit_slot_base(m, base):
    cells = st.unpack_from("<H", m, base + 0x18)[0]
    cap = st.unpack_from("<H", m, base + 0x1a)[0]
    ptr = st.unpack_from("<I", m, base + 0x10)[0]
    s1c, s20, s1e = (st.unpack_from("<H", m, base + o)[0] for o in (0x1C, 0x20, 0x1E))
    for d in (0, -4, -8, 4):
        arr = ptr + d
        if not (0 <= arr and arr + cap * 4 <= len(m)):
            continue
        c0 = c8 = c1e = bad = 0
        for i in range(cap):
            w0 = m[arr + i * 4]
            it = m[arr + i * 4 + 1]
            if it == 0xFF:
                if i >= cells:
                    c1e += 1
                elif w0 & 8:
                    pass
                else:
                    c0 += 1
                    if w0 == 0:
                        c8 += 1
            elif it >= N_ITEMS:
                bad = 1
                break
        if not bad and (c0, c8, c1e) == (s1c, s20, s1e):
            return arr
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    pay = open(PAY, "rb").read()
    anch = build_anchors(pay)

    rows = []
    fails = 0
    for run in RUNS:
        src = os.path.join(run, "save")
        for f in sorted(f for f in os.listdir(src) if f.endswith(".sav"))[:1]:
            m = zipfile.ZipFile(os.path.join(src, f)).read("Memory")
            v, _ = find_base(m, anch)
            if not v:
                continue
            B = v.most_common(1)[0][0]
            items = item_table(m, B)
            if items is None or not names_ok(items):
                continue
            for base in find_records(m):
                if m[base + 0x57] == 0xFF:
                    continue
                cap = st.unpack_from("<H", m, base + 0x1a)[0]
                arr = st.unpack_from("<I", m, base + 0x10)[0]
                if not (0 <= arr and arr + cap * 4 <= len(m)):
                    fails += 1
                    continue
                if any(not (m[arr + i * 4 + 1] == 0xFF or m[arr + i * 4 + 1] < N_ITEMS)
                       for i in range(cap)):
                    fails += 1
                    continue
                A = P = R = O = 0
                dbl = {12: False, 13: False, 14: False}
                for i in range(cap):
                    cls = m[arr + i * 4]
                    it = m[arr + i * 4 + 1]
                    fl = st.unpack_from("<H", m, arr + i * 4 + 2)[0]
                    if it == 0xFF or not (fl & 1):
                        continue
                    d = items[it]
                    A += d["ind"] + (1 if cls == 2 else 0)
                    P += d["pros"] + (1 if cls == 3 else 0)
                    R += d["res"] + (1 if cls == 4 else 0)
                    O += d["orb"]
                # per-k first-slot doubling per FUN_0003958c (first slot only)
                first = {}
                for i in range(cap):
                    it = m[arr + i * 4 + 1]
                    if it in (12, 13, 14) and it not in first:
                        fl = st.unpack_from("<H", m, arr + i * 4 + 2)[0]
                        first[it] = bool(fl & 1)
                if first.get(12):
                    A += A >> 1
                if first.get(13):
                    P += P >> 1
                if first.get(14):
                    R += R >> 1
                gov = m[base + 0x54]
                if gov == 0x21:
                    P += A >> 2
                elif gov == 0x22:
                    R += A >> 2
                rows.append((A, P, R, O, gov,
                             st.unpack_from("<h", m, base + 0x42)[0],
                             st.unpack_from("<H", m, base + 0x44)[0],
                             st.unpack_from("<H", m, base + 0x46)[0],
                             st.unpack_from("<H", m, base + 0x48)[0],
                             os.path.basename(run), f, base))
    print(f"records: {len(rows)}, arr-fails: {fails}")

    # per-channel scores: pow shift 0/1; upkeep 0/1; fresh-record init guess IND=1/PROS=1
    for shift in (0, 1):
        for upk in (0, 1):
            ic = pc = rc = 0
            for (A, P, R, O, gov, up, si, sr, sp, rn, f, base) in rows:
                iv = trunc85(A + shift) if (A if shift == 0 else A) else 0
                pv = trunc85(P + shift) if P else 0
                pv = max(0, pv - ((abs(up) >> 2) if upk else 0))
                if iv == si:
                    ic += 1
                if pv == sp:
                    pc += 1
                if R == sr:
                    rc += 1
            print(f"  pow+{shift} upkeep{upk}: IND {ic}/{len(rows)}  "
                  f"PROS {pc}/{len(rows)}  RES {rc}/{len(rows)}")

    # residual dump under pow+0 upkeep1
    n = 0
    for (A, P, R, O, gov, up, si, sr, sp, rn, f, base) in rows:
        iv = trunc85(A) if A else 0
        pv = max(0, (trunc85(P) if P else 0) - (abs(up) >> 2))
        if (iv, pv, R) != (si, sp, sr) and n < 25:
            n += 1
            print(f"  MISS {rn}/{f} base={base:#x} acc A/P/R={A}/{P}/{R} "
                  f"gov={gov:#x} up={up} stored IND/RES/PROS {si}/{sr}/{sp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
