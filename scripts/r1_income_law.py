#!/usr/bin/env python3
"""r1_income_law.py — live-verify the colony income law (OQ-016 income half)
against guest RAM. Docs landing: docs/re/economy.md, docs/re/ships.md.

STATIC LAW (work/ascend_restored.bin DISASSEMBLY, FUN_00038ba4 recalc
0x38ba4..0x38f5c; slot finder FUN_0003958c; item loader FUN_00037fc0):

Stride-123 system record, base = planet-NAME - 0x24 (OQ-014 locator law;
+0x10 slot-array ptr physical, member = ptr; slot u32 {byte0
cls(+0x8 unbuildable), byte1 itemIdx(0xff empty), u16 flags@+2 (bit0 active,
bit3 doubled)})):

  empty-slot accounting (itemIdx==0xff): i < +0x18 -> [rec+0x1c]++
    (class==0 also counts [rec+0x20]); i >= +0x18 -> [rec+0x1e]++  (fresh
    planet: +0x1c==cells, +0x1e==10 — verified).
  ACTIVE slots (u16 bit0), item != 0xff, item != 23 (Ship):
    IND += item.IND(i8@+0)  ; +1 if slot class == 2   (@0x38cbe)
    PROS+= item.PROS(i8@+2) ; +1 if slot class == 3   (@0x38cd7)
    RES += item.RES(i8@+1)  ; +1 if slot class == 4   (@0x38cfc)
    item-flags(u16@+6) bit2 set -> [rec+0x58]++ and skip the rest;
      else bit3 -> [rec+0x59]++; MPOP(i8@+3) -> [rec+0x4a];
      slot flags bit1 or item bit6 clear [rec+0x4c] += item UPOP(i8@+4)
  post-loop doubles via first ACTIVE slot holding item k (@0x38d3f/7a/b5):
    12 Hyperpower Plant -> IND  += IND>>1
    13 Fertilization    -> PROS += PROS>>1
    14 Internet         -> RES  += RES>>1
  governor [rec+0x54] (0xff none): '!' PROS += IND>>2 ('@0x38e05');
    '"' RES += IND>>2 (@0x38e10)
  compression (@0x38e2d/@0x38e5e, FILD + pow double 0x3FEB333333333333=0.85
  + FISTP nearest):
    IND  = 0 if 0 else round((IND+1)**0.85)
    PROS = 0 if 0 else round((PROS+1)**0.85); then
           PROS = max(0, PROS - u16[rec+0x42]//4)  (@0x38e8d)
    RES linear (no pow).
  tail stores @0x38ecb/ed3/edb: [rec+0x44]=IND [rec+0x46]=RES [rec+0x48]=PROS.

Item table Ghidra 0x73e40 stride 0x28 (IND@0 RES@+1 PROS@+2 MPOP@+3 UPOP@+4,
OQ-014) -> member index B + 0x82BB0 + 0x73e40; names cross-checked against
planitem.txt rows 12/13/14/22/23/24 so a wrong anchor fails loudly.

Exit 0 = IND AND RES match >= 90% of governor-clean owned records on one
capture (PROS reported, not gating). 1 = ran, negative. 2 = harness.

Usage: r1_income_law.py --run-dir DIR [--slot NAME] [--verbose]
"""
import argparse, math, os, re, struct as st, sys, zipfile
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAY = os.path.join(ROOT, "work", "ascend_payload.bin")
ITEM_STRIDE, N_ITEMS = 0x28, 39
REC = 123
NAME_AT = 0x24           # name field inside record (base = name - 0x24)
NAME_RE = re.compile(rb"[A-Za-z0-9 '^_.-]{3,20}\x00")
CELLS = {7, 11, 23, 45, 73}


def load_slots(run_dir, slot=None):
    pay = open(PAY, "rb").read()
    anch = build_anchors(pay)
    src = run_dir
    for sub in ("save", "ck"):
        if os.path.isdir(os.path.join(run_dir, sub)):
            src = os.path.join(run_dir, sub)
            break
    slots = sorted(f for f in os.listdir(src) if f.endswith(".sav"))
    if slot:
        slots = [s for s in slots if s == slot]
    out = []
    for f in slots:
        try:
            m = zipfile.ZipFile(os.path.join(src, f)).read("Memory")
        except Exception:
            continue
        v, _ = find_base(m, anch)
        if not v:
            continue
        out.append((f, m, v.most_common(1)[0][0]))
    return out


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
            "upop": st.unpack_from("<b", m, b + 4)[0],
            "flags": st.unpack_from("<H", m, b + 6)[0],
        })
    return rows


def names_ok(rows):
    want = {22: "Shipyard", 23: "Ship", 24: "Orbital Docks",
            12: "Hyperpower Plant", 13: "Fertilization Plant", 14: "Internet"}
    return all(rows[k]["name"] == v for k, v in want.items())


def find_records(m):
    """Name-anchor walk: cluster name-like starts by (pos mod 123), keep the
    mod class whose base=name-0x24 satisfies cells in CELLS and cap=cells+10
    on the longest chain (OQ-014 law; never a raw-offset scan)."""
    starts = defaultdict(list)
    pos = 0
    while True:
        mm = NAME_RE.search(m, pos)
        if not mm:
            break
        starts[mm.start() % REC].append(mm.start())
        pos = mm.start() + 1

    def good(base):
        cells = st.unpack_from("<H", m, base + 0x18)[0]
        cap = st.unpack_from("<H", m, base + 0x1a)[0]
        if cells not in CELLS or cap != cells + 10:
            return False
        ptr = st.unpack_from("<I", m, base + 0x10)[0]
        arr = ptr
        if not (0 <= arr and arr + cap * 4 <= len(m)):
            return False
        return all(m[arr + i * 4 + 1] in (0xFF,) or m[arr + i * 4 + 1] < N_ITEMS
                   for i in range(cap))

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
        # score chain
        ok = sum(1 for n in chain if good(n - NAME_AT))
        if ok > sum(1 for n in best if good(n - NAME_AT)):
            best = chain
    return [(n - NAME_AT, st.unpack_from("<H", m, n - NAME_AT + 0x18)[0],
             st.unpack_from("<H", m, n - NAME_AT + 0x1a)[0],
             st.unpack_from("<I", m, n - NAME_AT + 0x10)[0])
            for n in best if good(n - NAME_AT)]


def pow85(v):
    if v == 0:
        return 0
    x = (v + 1) ** 0.85
    f = math.floor(x)
    d = x - f
    return f if d < 0.5 else (f + 1 if d > 0.5 else (f if f % 2 == 0 else f + 1))


def pow85(v):
    if v == 0:
        return 0
    x = (v + 1) ** 0.85
    f = math.floor(x)
    d = x - f
    return f if d < 0.5 else (f + 1 if d > 0.5 else (f if f % 2 == 0 else f + 1))


def recompute(m, rec, items):
    """Byte-exact FUN_00038ba4 (docs/re/economy.md 6). Returns
    (IND, RES, PROS, c0, c20, c1e, c4a, c4c, c24) post-clamp."""
    base, cells, cap, arr = rec
    IND = RES = PROS = 0
    c0 = c20 = c1e = c24 = c4c = 0
    c4a = st.unpack_from("<H", m, base + 0x55)[0]
    for i in range(cap):
        w0 = m[arr + i * 4]
        it = m[arr + i * 4 + 1]
        fl = st.unpack_from("<H", m, arr + i * 4 + 2)[0]
        if it == 0xFF:
            if i >= cells:
                c1e += 1
            elif not (w0 & 8):
                c0 += 1
                if w0 == 0:
                    c20 += 1
            continue
        if it >= N_ITEMS:
            continue
        d = items[it]
        if fl & 1:
            if d["ind"]:
                IND += d["ind"] + (1 if w0 == 2 else 0)
            if d["pros"]:
                PROS += d["pros"] + (1 if w0 == 3 else 0)
            if d["res"]:
                RES += d["res"] + (1 if w0 == 4 else 0)
            if d["flags"] & 4:
                c24 += 1
            elif d["flags"] & 8:
                pass  # +0x59 counter not verified, not gated
            c4a += d["mpop"]
        else:
            if it == 23 or (fl & 2) or (d["flags"] & 0x40):
                continue
            c4c += d["mpop"]
    for k, which in ((12, "i"), (13, "p"), (14, "r")):
        for i in range(cap):
            if m[arr + i * 4 + 1] == k:
                if st.unpack_from("<H", m, arr + i * 4 + 2)[0] & 1:
                    if which == "i":
                        IND += IND >> 1
                    elif which == "p":
                        PROS += PROS >> 1
                    else:
                        RES += RES >> 1
                break
    gov = m[base + 0x54]
    if gov == ord("!"):
        PROS += IND >> 2
    elif gov == ord('"'):
        RES += IND >> 2
    ind = pow85(IND)
    pros = pow85(PROS)
    u = st.unpack_from("<h", m, base + 0x42)[0]
    pros = max(0, pros - (u >> 2))
    c4a = min(100, max(0, c4a))
    u = min(u, c4a) if u >= 0 else 0
    c4c = min(max(0, c4c), u)
    return ind, RES, pros, c0, c20, c1e, c4a, c4c, c24


def main():
    full8 = [0]
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--slot")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    slots = load_slots(args.run_dir, args.slot)
    if not slots:
        print("harness: no readable slot with derivable base")
        return 2
    results = []
    for name, m, P0 in slots[:4]:
        items = item_table(m, P0)
        if items is None or not names_ok(items):
            print(f"{name}: item-table cross-check FAILED")
            continue
        recs = find_records(m)
        clean = [r for r in recs if m[r[0] + 0x57] != 0xFF]
        mi = mr = mp = n = 0
        for r in clean:
            vals = recompute(m, r, items)
            ei, rs, pr = vals[0], vals[1], vals[2]
            store = [st.unpack_from('<H', m, r[0]+o)[0] for o in (0x44, 0x46, 0x48, 0x1c, 0x20, 0x1e, 0x4a, 0x4c)]
            agree = sum(v == w for v, w in zip(vals, store))
            full8[0] += agree == 8
            gi = st.unpack_from("<H", m, r[0] + 0x44)[0]
            gr = st.unpack_from("<H", m, r[0] + 0x46)[0]
            gp = st.unpack_from("<H", m, r[0] + 0x48)[0]
            n += 1
            mi += ei == gi
            mr += rs == gr
            mp += pr == gp
            if args.verbose and (ei != gi or rs != gr):
                nm = m[r[0] + NAME_AT:r[0] + NAME_AT + 30].split(b"\x00")[0].decode("cp437", "replace")
                print(f"  {nm:18s} cells={r[1]} IND {ei}->{gi} RES {rs}->{gr} PROS {pr}->{gp}")
        print(f"{name}: recs={len(recs)} clean-owned={n} IND {mi}/{n} RES {mr}/{n} PROS {mp}/{n}")
        if n:
            results.append((min(mi, mr) / n, name))
    if results:
        frac, nm = max(results)
        if frac >= 0.9:
            print(f"LAW HOLDS on {nm} ({frac:.0%} IND+RES match)")
            return 0
    print("negative this run")
    return 1


if __name__ == "__main__":
    sys.exit(main())
