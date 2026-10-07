#!/usr/bin/env python3
"""r1_income_fit.py — candidate-model scoring for the colony income law
(OQ-016 income half) against guest RAM. Companion to r1_income_law.py.

Disassembly baseline (work/ascend_restored.bin, FUN_00038ba4 @0x38ba4):
planet record stride 123, base = NAME - 0x24; slot array = u32[rec+0x10]
(raw, member-walk delta fitted via empty census); slot dword {byte0 cls,
byte1 itemIdx 0xff empty, u16 flags @+2 bit0 ACTIVE}; item record stride
0x28 at Ghidra 0x73e40 -> B+0x82BB0+0x73e40: byte0 IND, +1 RES, +2 PROS,
+3 MPOP, +4 UPOP, word@6 flags.

ACTIVE-slot accumulation @0x38cbe..0x38d1f: IND/PROS/RES += item value plus
+1 when slot cls==2/3/4 respectively (VERIFIED bytes 0x38cce/0x38cf2/0x38d17).
Doubling @0x38d3f+: first slot whose itemIdx==k AND active -> v += v>>1
(k=12 IND, 13 PROS, 14 RES). Governor @+0x54: 0x21 PROS+=IND>>2, 0x22
RES+=IND>>2 (@0x38e05/0x38e10). Compression @0x38e2d..: pow(V+1,0.85) double
(FILD/FSTP/pow/ROUND/FISTP). i16[+0x42] SAR 2 subtracted from PROS only.

OPEN (this battery scores them): pow arg V vs V+1; whether captured stored
values include extra terms (observed IND=1/PROS=1 on facility-free owned
planets in 3 captures — a possible unlocated per-planet base or a stale-value
artefact of these saves).

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


def p85(v, shift):
    x = (v + shift) ** 0.85
    f = math.floor(x)
    d = x - f
    return f if d < 0.5 else (f + 1 if d > 0.5 else (f if f % 2 == 0 else f + 1))


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
            "mpop": st.unpack_from("<b", m, b + 3)[0],
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

    score = defaultdict(int)
    rows = []          # (INDraw, PROSraw, RESraw, dbl, gov, up42, INDs, PROSs, RESs, nindcls)
    fits = fails = 0
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
                if args.verbose:
                    print(f"{os.path.basename(run)}: item table FAIL")
                continue
            for base in find_records(m):
                if m[base + 0x57] == 0xFF:
                    continue
                arr = fit_slot_base(m, base)
                if arr is None:
                    fails += 1
                    continue
                fits += 1
                cap = st.unpack_from("<H", m, base + 0x1a)[0]
                IND = PROS = RES = 0
                nind2 = 0
                dbl = {12: False, 13: False, 14: False}
                for i in range(cap):
                    cls = m[arr + i * 4]
                    it = m[arr + i * 4 + 1]
                    fl = st.unpack_from("<H", m, arr + i * 4 + 2)[0]
                    if it == 0xFF or it >= N_ITEMS or not (fl & 1):
                        continue
                    d = items[it]
                    if d["ind"]:
                        IND += d["ind"]
                        if cls == 2:
                            nind2 += 1
                    if d["pros"]:
                        PROS += d["pros"] + (1 if cls == 3 else 0)
                    if d["res"]:
                        RES += d["res"] + (1 if cls == 4 else 0)
                    if it in dbl:
                        dbl[it] = True
                rows.append((IND, PROS, RES, dbl, m[base + 0x54],
                             st.unpack_from("<h", m, base + 0x42)[0],
                             st.unpack_from("<H", m, base + 0x44)[0],
                             st.unpack_from("<H", m, base + 0x48)[0],
                             st.unpack_from("<H", m, base + 0x46)[0],
                             nind2, os.path.basename(run), f, base))
    print(f"fitted owned records: {fits}, base-fit fails: {fails}")

    # score models: cls-bonus on IND yes/no; pow shift 0/1; constant base 0/1
    for cb in (0, 1):
        for shift in (0, 1):
            for cst in (0, 1):
                good = 0
                for (IND, PROS, RES, dbl, gov, up, si, sp, sr, nind2, rn, f, base) in rows:
                    i0 = IND + (nind2 if cb else 0) + cst
                    p0 = PROS + cst
                    r0 = RES + cst
                    if dbl[12]:
                        i0 += i0 >> 1
                    if dbl[13]:
                        p0 += p0 >> 1
                    if dbl[14]:
                        r0 += r0 >> 1
                    if gov == 0x21:
                        p0 += i0 >> 2
                    elif gov == 0x22:
                        r0 += i0 >> 2
                    iv = p85(i0, shift) if i0 else 0
                    pv = max(0, (p85(p0, shift) if p0 else 0) - (up >> 2))
                    if (iv, pv, r0) == (si, sp, sr):
                        good += 1
                score[f"cls{cb} pow+{shift} cst{cst}"] = good

    for name, sc in sorted(score.items(), key=lambda kv: -kv[1]):
        print(f"  {name:18s} {sc}/{fits}")
    if fits and max(score.values()) >= 0.95 * fits:
        print("MODEL IDENTIFIED")
        return 0
    # residual dump for the best model
    best = max(score.keys(), key=lambda k: score[k])
    print(f"residuals under {best}:")
    for (IND, PROS, RES, dbl, gov, up, si, sp, sr, nind2, rn, f, base) in rows[:40]:
        print(f"  {rn}/{f} base={base:#x} acc I/P/R={IND}/{PROS}/{RES} dbl={[k for k in dbl if dbl[k]]}"
              f" gov={gov:#x} up={up} stored {si}/{sp}/{sr}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
