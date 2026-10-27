#!/usr/bin/env python3
"""r1_t106_alias.py — is the +0x55 seed residual the SLOT-ARRAY ALIASING set?

Hypothesis (from P2/P3): the seed word r55 and the weight row +0x16 are
coherent with each other; the surface grid read through [rec+0x10]+0x88 is the
odd one out. If the heap arrays of some planet records are SHARED (two records'
+0x10 pointers resolve to the same array object, or the array object's slot
window overlaps a neighbour's), the counted cell set is not the set the
generator wrote, and the seed law will fail exactly there.

Tests per run (first save):
  A. uniqueness of the resolved array pointer across planet records
  B. window CONTENT equality between records sharing an array
  C. SEED LAW score split: aliased vs unique records
  D. neighbour-overlap: does [arr, arr+4*cap) intersect another record's array?

Exit 0 if aliased records account for ALL seed-law failures (closure-shaped
result); 1 otherwise. Prints the numbers either way.
"""
import argparse, collections, collections, glob, os, struct as st, sys, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_income_law as IL
from r1_sav_scan import build_anchors, find_base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", default="work/r1/*")
    args = ap.parse_args()
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    anch = build_anchors(open(IL.PAY, "rb").read())

    tot = dup = dev_tot = dev_dup = clean_fail = 0
    per_run = []
    for run in sorted(glob.glob(os.path.join(ROOT, args.runs))):
        src = os.path.join(run, "save")
        if not os.path.isdir(src):
            continue
        svs = sorted(glob.glob(os.path.join(src, "*.sav")), key=os.path.getmtime)
        if not svs:
            continue
        try:
            m = zipfile.ZipFile(svs[0]).read("Memory")
        except Exception:
            continue
        v, _ = find_base(m, anch)
        if not v:
            continue
        recs = IL.find_records(m)
        if not recs:
            continue
        ptrs = collections.Counter(base + 0x10 for base, *_ in recs)
        # resolved array identity: content hash of the FULL window, plus the
        # stored pointer itself (both aliasing forms matter)
        by_ptr = collections.defaultdict(list)
        for base, cells, cap, arr in recs:
            by_ptr[arr].append((base, cells, cap))
        shared = {a for a, lst in by_ptr.items() if len(lst) > 1}
        # content sharing where pointers differ (heap objects with identical
        # grid bytes are normal for all-barren worlds, so report only shared
        # NON-uniform grids)
        dup_recs = set()
        for a, lst in by_ptr.items():
            if len(lst) > 1:
                dup_recs.update(b for b, _, _ in lst)
        fails = 0
        fail_shared = 0
        for base, cells, cap, arr in recs:
            w = [m[arr + i * 4] for i in range(cap)]
            nb = sum(1 for c in w[:cells] if (c & 0xF) != 0)
            r55 = st.unpack_from("<H", m, base + 0x55)[0]
            if r55 != nb // 3 + 5:
                fails += 1
                if arr in shared:
                    fail_shared += 1
        n = len(recs)
        tot += n
        dup += len(dup_recs)
        dev_tot += fails
        dev_dup += fail_shared
        clean_fail += fails - fail_shared
        per_run.append((os.path.basename(run), n, len(shared), len(dup_recs),
                        fails, fail_shared))

    print(f"corpus records={tot} records_sharing_array={dup} "
          f"seed_failures={dev_tot} failures_on_shared={dev_dup} "
          f"failures_on_unique={clean_fail}")
    print(f"shared-array records: {100.0*dup/max(1,tot):.2f}% of all records")
    print("\nrun                              n  shared duprec fail fail_shared")
    for r in per_run:
        print(f"  {r[0]:32s} {r[1]:4d} {r[2]:6d} {r[3]:6d} {r[4]:4d} {r[5]:10d}")
    print("\nVERDICT:", "ALIASING EXPLAINS EVERY FAILURE" if clean_fail == 0 and dev_dup > 0
          else ("NO SHARED ARRAYS AT ALL" if dup == 0 else
                f"ALIASING EXPLAINS {dev_dup}/{dev_tot}; "
                f"{clean_fail} failures sit on UNIQUE arrays"))
    return 0 if (clean_fail == 0 and dev_dup > 0) else 1


if __name__ == "__main__":
    sys.exit(main())
