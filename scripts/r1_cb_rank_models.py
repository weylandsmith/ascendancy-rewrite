#!/usr/bin/env python3
"""r1_cb_rank_models.py — t42 model fit for the home/CB cell-rank paradox.

OBSERVED (r1_cell_choice_census, first-save homes): CB barren-cell rate
~25% ~= terrain barren rate, but t40 measured nonbarren-rank 0/1 in 0/157
and the rank histogram is HEAVILY top-heavy (rank>=4 in 48/59).

MODELS (CB = uniform pick among a cell set S at placement):
  U-ALL   S = all surface cells                       -> barren ~31%, rank0 ~4%
  U-NROCK S = non-rock cells                          -> barren ~31%, rank0 ~1.7%
  U-NBAR  S = nonbarren cells (rule-B static law)     -> barren 0%, rank0 ~1.7%
  SHIFT   S = non-rock; rank0/1 suppressed BECAUSE the first non-rock cell
          is consumed at world-gen by the per-empire +1 IND grant (t19/t20
          home-pair law) -> predicted: FIRST NON-ROCK CELL IS BARREN on
          homes where CB rank(nonbar)==rank(nonrock); testable directly.
Report per model: barren-CB rate, rank0 rate, and a joint statistic
(Pearson chi2 over [barrenCB?, rank-bin] 2x4 table vs model expectation).
"""
import sys, os, glob, struct as st, zipfile, collections, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base
import r1_income_law as IL

TURN_PHYS, IMAGE_MAP_BASE = 0x254E10, 0x1BF450  # banked H-map law (r1_pros_growth)


def homes():
    pay = open("work/ascend_payload.bin", "rb").read()
    anch = build_anchors(pay)
    worlds = {}
    for run in sorted(glob.glob("work/r1/*")):
        if not os.path.isdir(run):
            continue
        for f in sorted(glob.glob(run + "/save/*.sav"), key=os.path.getmtime):
            try:
                m = zipfile.ZipFile(f).read("Memory")
            except Exception:
                continue
            votes, _ = find_base(m, anch)
            if not votes:
                continue
            base = votes.most_common(1)[0][0]
            items = IL.item_table(m, base)
            if items is None or not IL.names_ok(items):
                continue
            try:
                turn = st.unpack_from("<H", m, TURN_PHYS + (base - IMAGE_MAP_BASE))[0]
            except Exception:
                continue
            ids = []
            cbs = []
            for rec in IL.find_records(m):
                rb = rec[0]
                if m[rb + 0x57] == 0xFF:
                    continue
                ptr = st.unpack_from("<I", m, rb + 0x10)[0] + 0x88
                surf = st.unpack_from("<H", m, rb + 0x18)[0]
                capw = st.unpack_from("<H", m, rb + 0x1a)[0]
                name = m[rb + 0x24:m.index(b"\x00", rb + 0x24)].decode("cp437", "replace")
                ids.append((name, capw))
                for k in range(min(capw, 200)):
                    if (m[ptr + 4 * k + 1] == 5
                            and (st.unpack_from("<H", m, ptr + 4 * k + 2)[0] & 1)
                            and k < surf):
                        sur = [m[ptr + 4 * q] for q in range(surf)]
                        cbs.append((name, sur, k))
            if not ids or turn > 1:
                continue
            wid = tuple(ids)
            if wid not in worlds:
                worlds[wid] = cbs
    return worlds


def main():
    rows = []
    for wid, cbs in homes().items():
        for name, sur, k in cbs:
            nonrock = [q for q, c in enumerate(sur) if not (c & 8)]
            nonbar = [q for q, c in enumerate(sur) if c != 0 and not (c & 8)]
            rock_n = len(sur) - len(nonrock)
            barren_n = len(nonrock) - len(nonbar)
            rn = nonrock.index(k) if k in nonrock else -1
            rb = nonbar.index(k) if k in nonbar else -1
            first_nr_barren = bool(nonrock) and (sur[nonrock[0]] == 0)
            rows.append(dict(k=k, nsur=len(sur), nonrock=len(nonrock),
                             nonbar=len(nonbar), rock=rock_n, barren=barren_n,
                             rn=rn, rb=rb, cb_barren=(sur[k] == 0),
                             fnb=first_nr_barren, name=name))
    n = len(rows)
    print(f"first-save turn<=1 home CBs: {n}")
    barren_cb = sum(r["cb_barren"] for r in rows)
    rank0 = sum(1 for r in rows if r["rb"] == 0)
    rank1 = sum(1 for r in rows if r["rb"] == 1)
    fnb = sum(r["fnb"] for r in rows)
    print(f"barren-CB rate:      {barren_cb}/{n} = {barren_cb/n:.3f}")
    print(f"nonbar-rank0 homes:  {rank0}/{n}   rank1: {rank1}/{n}")
    print(f"first-nonrock IS barren: {fnb}/{n} = {fnb/n:.3f}")
    # mean barren fraction of nonrock (expected barren-CB rate under U-NROCK)
    mb = sum(r["barren"]/max(1, r["nonrock"]) for r in rows) / n
    mr = sum(1/max(1, r["nonrock"]) for r in rows) / n
    mrn = sum(1/max(1, r["nonbar"]) for r in rows) / n
    print(f"E[barren frac nonrock]={mb:.3f} (U-NROCK predicts CB-barren~{mb:.3f})")
    print(f"E[1/nonrock]={mr:.4f} (U-NROCK rank0~{mr:.3f}); E[1/nonbar]={mrn:.4f} (U-NBAR rank0)")
    # SHIFT prediction: homes with cb on nonbar AND rank equal in both scales
    eq = [r for r in rows if r["rb"] >= 0 and r["rn"] >= 0]
    print(f"\nper-row: cell nsur nonrock nonbar rank_nr rank_nb cb_barren fnb  name")
    for r in sorted(rows, key=lambda r: (r["rb"], r["rn"])):
        print(f"  {r['k']:4d} {r['nsur']:4d} {r['nonrock']:6d} {r['nonbar']:6d} "
              f"{r['rn']:7d} {r['rb']:7d} {str(r['cb_barren']):9s} {str(r['fnb']):5s} {r['name']}")
    # distribution of rank_nr (non-rock scale) bins
    h = collections.Counter(min(r["rn"] // 5, 8) if r["rn"] >= 0 else -1 for r in rows)
    print(f"\nrank(nonrock) hist bins of 5: {dict(sorted(h.items()))}")


main()
