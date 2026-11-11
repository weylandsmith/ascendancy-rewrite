# SPDX-License-Identifier: GPL-3.0-or-later

"""Re-measure surface-item slot contiguity on the corrected +0x88 array
(tension check: FUN_0003875c picks uniformly among legal empty slots, but
T37 banked 17980/18620 contiguous prefix runs). Reports per-record:
min slot, max slot, count, and whether the occupied surface slots form a
contiguous run over NON-ROCK cells; plus a histogram of (min,max) gaps."""
import sys, os, glob, struct as st, zipfile, collections
sys.path.insert(0, "scripts")
from r1_sav_scan import build_anchors, find_base
import r1_income_law as IL

pay = open("work/ascend_payload.bin", "rb").read()
anch = build_anchors(pay)
recs = []
n_saves = 0
for run in sorted(glob.glob("work/r1/*")):
    if not os.path.isdir(run):
        continue
    for f in sorted(glob.glob(run + "/save/*.sav")):
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
        n_saves += 1
        recs.append((m, items))
print(f"saves scanned: {n_saves}")

shape = collections.Counter()
item_at_min = collections.Counter()
n_rec = 0
n_items_tot = 0
gap_hist = collections.Counter()
for m, items in recs:
    for rec in IL.find_records(m):
        rb = rec[0]
        if m[rb + 0x57] == 0xFF:
            continue
        cells = st.unpack_from("<H", m, rb + 0x18)[0]
        arr = st.unpack_from("<I", m, rb + 0x10)[0] + 0x88
        rock = {k for k in range(cells) if m[arr + 4 * k] & 8}
        nr = [k for k in range(cells) if k not in rock]
        surf_items = [k for k in range(cells)
                      if m[arr+4*k+1] != 0xFF and m[arr+4*k+1] < IL.N_ITEMS
                      and (st.unpack_from("<H", m, arr+4*k+2)[0] & 1)]
        if len(surf_items) < 2:
            shape[("n<2", len(surf_items))] += 1
            continue
        n_rec += 1
        n_items_tot += len(surf_items)
        rnk = sorted(nr.index(k) for k in surf_items if k in nr)
        contig = rnk == list(range(rnk[0], rnk[0] + len(rnk)))
        span = rnk[-1] - rnk[0] + 1
        shape[("contig" if contig else "scattered",
               "min0" if rnk[0] == 0 else "min>0")] += 1
        # expected contiguity probability under uniform-random placement:
        # C(nbuild-span+1,1) arrangements... report fill density instead
        gap_hist[min(span, 20)] += 1
        item_at_min[items[m[arr+4*min(surf_items)+1]]["name"]] += 1
print(f"records with >=2 surface items: {n_rec}  (items {n_items_tot})")
for k, c in shape.most_common(8):
    print(f"   {c:6d} x {k}")
print("span of occupied ranks (capped 20):", dict(sorted(gap_hist.items())))
print("item name at the lowest surface slot:", dict(item_at_min.most_common(6)))
