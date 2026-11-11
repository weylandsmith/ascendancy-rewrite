#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r348_planet0a_census.py — planet-record +0x0a OFFLINE census (t348 probe 1).

Premises banked (income-law.md:2050, r1-savestate.md ~:934): file-side two
value bands ~17.5k/~50.2k, 23 distinct, "pointer-like seed field repaired at
load", live churns on UNOWNED records, not read by income recalc.
+0x0c is a u16 star-index bijection, so +0x0a is a standalone u16 — the
pointer-value law (t298, u32 stored = guest PHYSICAL, target member = value +
0x88) is tested here against CANDIDATE BASES, not assumed.
NOTE observed: 50328 - 17560 == 0x8000 exactly -> bit-15 + 15-bit-offset shape
is one hypothesis this census tests (law: for every V, V^0x8000 also seen?).

Reads the 48-save corpus (same run set as r345) via the pointer law helpers.
Exit 0 = census ran AND per-record file-side stability verdict printed;
2 = harness error (no captures / no base vote).
"""
import argparse, glob, os, struct, sys, zipfile, collections, functools

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base
from r1_income_law import find_records

def sav_paths(run):
    return sorted(glob.glob(os.path.join(run, "save", "*.sav"))) + \
           sorted(glob.glob(os.path.join(run, "ring-final", "*.sav")))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", action="append", default=None)
    ap.add_argument("--per-run", type=int, default=3)
    args = ap.parse_args()
    runs = args.run_dir or sorted(glob.glob("work/r1/r1deep-*")) + \
           ["work/r1/t340-shieldc-20261108-014705"]
    needle = open("work/ascend_payload.bin", "rb").read()
    anch = build_anchors(needle)

    Vc = collections.Counter()                 # distinct +0x0a values
    VO = collections.Counter()                 # (V, owner)
    per_rec = collections.defaultdict(set)     # rec index -> {V across saves}
    laws = collections.Counter()               # hypothesis hit counters
    tot = 0
    nsaves = 0
    last = None                                # (m, B, recs) of final save probed

    for run in runs:
        for p in sav_paths(run)[: args.per_run]:
            try:
                mem = zipfile.ZipFile(p).read("Memory")
            except Exception:
                continue  # torn copy law
            v, _ = find_base(mem, anch)
            if not v:
                continue
            B, _w = v.most_common(1)[0]
            recs = find_records(mem)
            if not recs or len(recs) < 100:
                continue
            nsaves += 1
            last = (mem, B, p)
            for i, r in enumerate(sorted(recs, key=lambda x: x[0])):
                base = r[0] if isinstance(r, (tuple, list)) else r
                V = struct.unpack_from("<H", mem, base + 0x0a)[0]
                owner = mem[base + 0x57]
                Vc[V] += 1
                VO[(V, owner)] += 1
                per_rec[i].add(V)
                tot += 1
                p10 = struct.unpack_from("<I", mem, base + 0x10)[0]
                arr = p10 + 0x88
                # hypothesis battery (counted, not asserted):
                if V == (p10 & 0xFFFF): laws["V==low16(+0x10 phys)"] += 1
                if V == (arr & 0xFFFF): laws["V==low16(arr member)"] += 1
                if V == ((arr - base) & 0xFFFF): laws["V==(arr-base)&0xffff"] += 1
                if V == ((p10 - (B + 0x82BB0)) & 0xFFFF): laws["V==dataseg_off(p10)"] += 1
                if V == ((base - B - 0x82BB0) & 0xFFFF): laws["V==dataseg_off(rec)"] += 1
                if V >> 15: laws["V bit15 SET"] += 1
                star = struct.unpack_from("<H", mem, base + 0x0c)[0]
                if V == star * 0x28: laws["V==star*40"] += 1

    print(f"saves={nsaves} rec_samples={tot}")
    print("distinct +0x0a values:", len(Vc))
    for V in sorted(Vc):
        print(f"  V={V:6d} (0x{V:04x}) n={Vc[V]:5d} owners={sorted({o for (v, o) in VO if v == V})}")
    print("\nhypothesis battery (hits / samples):")
    for k, n in laws.most_common():
        print(f"  {k}: {n}/{tot}")
    stab = collections.Counter(len(s) for s in per_rec.values())
    print("\nper-record distinct-V count across corpus (stability):", dict(sorted(stab.items())))
    churn = [i for i, s in per_rec.items() if len(s) > 1]
    print(f"records that CHURN across saves: {len(churn)}/{len(per_rec)}")

    # target-shape probe on the final save: for each distinct V, what lives at
    # the candidate targets? (member V+0x88 == guest-physical V under t298;
    #  B+0x82bb0+V == data-seg-offset interpretation)
    mem, B, p = last
    print(f"\ntarget-shape probe from {p} (B={B}):")
    for V in sorted(Vc):
        t1 = V + 0x88
        t2 = B + 0x82BB0 + V
        def sig(t):
            if not (0 <= t < len(mem) - 16):
                return "OOB"
            b = mem[t:t + 16]
            asc = sum(1 for c in b if 32 <= c < 127)
            z = sum(1 for c in b if c == 0)
            return f"ascii{asc:2d} zero{z:2d} {b.hex()}"
        print(f"  V={V:6d} phys: {sig(t1)}")
        print(f"           dseg: {sig(t2)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
