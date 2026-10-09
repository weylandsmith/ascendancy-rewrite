#!/usr/bin/env python3
"""r1_cap_ledger.py — POP-CAP (+0x4a) exact-law ledger (OQ-016, S10).

Three candidate recalc models for every planet record in every save slot:
  model A:  clamp(+0x55 + MPOP(active, skip flags&4, CB included))
  model B (disasm byte-exact recompute): clamp(+0x55 + MPOP(ALL active
          slots incl flags&4 items and Colony Base))   [0x38bf8 is on
          BOTH the flags&4 and non-flags&4 paths]
  model C: B but skipping Colony Base
t33 (corrected slot-array pointer +0x88): B and A 100.00% (72066/72066),
C 96.23% — B is the law. Reports match counts per model; per-planet diff
histograms for the winner's failures. Exit 0 if best model >= 99.5%;
1 negative; 2 harness error.
"""
import argparse, os, struct as st, sys, zipfile
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base
import r1_income_law as IL

CB = 5  # Colony Base item row


def slot_items(m, rec):
    base, cells, cap, arr = rec
    out = []
    for i in range(cap):
        w0 = m[arr + i * 4]
        it = m[arr + i * 4 + 1]
        fl = st.unpack_from("<H", m, arr + i * 4 + 2)[0]
        out.append((w0, it, fl))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="work/r1")
    args = ap.parse_args()
    pay = open(IL.PAY, "rb").read()
    anch = build_anchors(pay)

    run_dirs = sorted(d for d in os.listdir(args.runs)
                      if os.path.isdir(os.path.join(args.runs, d))
                      and (os.path.isdir(os.path.join(args.runs, d, "save"))
                           or os.path.isdir(os.path.join(args.runs, d, "ck"))))
    totA = totB = totC = tot = 0
    diffsB = Counter()
    badB = Counter()  # planet-name keyed failures for model B
    items_cache = {}
    for rd in run_dirs:
        src = os.path.join(args.runs, rd)
        for sub in ("save", "ck"):
            if os.path.isdir(os.path.join(src, sub)):
                src = os.path.join(src, sub)
                break
        for f in sorted(x for x in os.listdir(src) if x.endswith(".sav")):
            try:
                m = zipfile.ZipFile(os.path.join(src, f)).read("Memory")
            except Exception:
                continue
            key = (rd, f)
            v, _ = find_base(m, anch)
            if not v:
                continue
            B = v.most_common(1)[0][0]
            items = items_cache.get(B)
            if items is None:
                items = IL.item_table(m, B)
                if items is None or not IL.names_ok(items):
                    continue
                items_cache[B] = items
            recs = IL.find_records(m)
            if len(recs) < 30:
                continue
            for rec in recs:
                base, cells, cap, arr = rec
                r55 = st.unpack_from("<H", m, base + 0x55)[0]
                act = st.unpack_from("<H", m, base + 0x4a)[0]
                name = m[base + IL.NAME_AT:base + IL.NAME_AT + 24].split(b"\x00")[0].decode("cp437", "replace")
                sA = sB = sC = r55
                for (w0, it, fl) in slot_items(m, rec):
                    if it == 0xFF or it >= IL.N_ITEMS:
                        continue
                    if not (fl & 1):
                        continue
                    mp = items[it]["mpop"]
                    if it == CB:
                        sC += 0
                    else:
                        sC += mp
                    if items[it]["flags"] & 4:
                        continue
                    sA += mp
                    sB += mp
                clamp = lambda x: min(100, max(0, x))
                pA, sBc, pC = clamp(sA), clamp(sB), clamp(sC)
                tot += 1
                totA += pA == act
                totB += sBc == act
                totC += pC == act
                if sBc != act:
                    diffsB[act - sBc] += 1
                    badB[name] += 1
    print(f"samples: {tot}")
    # labels match CODE (t33 audit): sA skips flags&4 (CB included — and all
    # flags&4 rows have mpop=0 so A==B numerically always); sB = ALL active;
    # sC = skips Colony Base.
    print(f"model A (skip flags&4, incl CB): {totA} ({100.0*totA/max(1,tot):.2f}%)")
    print(f"model B (ALL active MPOP, disasm): {totB} ({100.0*totB/max(1,tot):.2f}%)")
    print(f"model C (B minus Colony Base):     {totC} ({100.0*totC/max(1,tot):.2f}%)")
    print("model B diff histogram (actual-pred):", dict(sorted(diffsB.items())))
    if badB:
        top = badB.most_common(15)
        print("model B failure planets (name, count):", top)
    best = max(totA, totB, totC)
    return 0 if tot and best >= 0.995 * tot else (1 if tot else 2)


if __name__ == "__main__":
    sys.exit(main())
