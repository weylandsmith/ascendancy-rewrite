#!/usr/bin/env python3
"""r1_t75_read.py — offline analysis of an r1_t75_run.sh capture.

Per slot: base B (payload anchor vote >=5), then via score.md S2 / pointer-law
corollary idx (member = B + 0x82bb0 + X):
  DAT_000482fb  owned-star count fed to the score screen
  DAT_00043510  end-condition SELECTOR byte (0x2c01d semantics: nonzero fires
                the presenter cluster; 4 == end-ctrl arm per 0x2c01d `cmp al,5`
                guard region — record the RAW byte, interpretation follows the
                0x2c03a jump table: table[idx] arms chosen by value)
  DAT_0004350c  rank dword (0xFFFFFFFF = none)
  hi-u16 DAT_00016143 = T total stars (context)
Exit 0 always unless harness error (no slots). Prints one row per slot and a
VERDICT line: FIRING if any slot has selector != 0.
"""
import sys, os, zipfile, struct, glob
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAY = open(os.path.join(ROOT, "work/ascend_payload.bin"), "rb").read()
ANCH = build_anchors(PAY)

def base_of(mem):
    v = Counter()
    for p, w in ANCH:
        hits, s = [], 0
        while True:
            o = mem.find(w, s)
            if o < 0:
                break
            hits.append(o); s = o + 1
            if len(hits) > 5:
                break
        if len(hits) == 1:
            v[hits[0] - p] += 1
    if not v or v.most_common(1)[0][1] < 5:
        return None
    return v.most_common(1)[0][0]

def main():
    run = sys.argv[1]
    fired = False
    seen = 0
    maxn = 0
    for sp in sorted(glob.glob(os.path.join(run, "save", "*.sav"))):
        try:
            mem = zipfile.ZipFile(sp).read("Memory")
        except Exception:
            continue
        B = base_of(mem)
        if B is None:
            print(os.path.basename(sp), "no-anchor")
            continue
        assert B is not None  # closure-narrowing for the lambda below
        idx = lambda X, n: mem[B + 0x82bb0 + X: B + 0x82bb0 + X + n]
        n, = struct.unpack("<I", idx(0x482fb, 4))
        sel = idx(0x43510, 1)[0]
        rank, = struct.unpack("<I", idx(0x4350c, 4))
        T, = struct.unpack("<H", idx(0x16143 + 2, 2))
        seen += 1
        if sel != 0:
            fired = True
        if n > maxn:
            maxn = n
        print(f"{os.path.basename(sp)}: owned={n}/{T} "
              f"pct={100*n//T if T else 0} selector={sel:#04x} rank={rank:#010x}")
    counted = maxn > 0
    in_band = maxn >= 26  # injection band 29/50; allow off-by-a-couple settling
    if fired and in_band:
        verdict = ("FIRING (selector nonzero) at band ~29/50 => threshold "
                   "in (50%,58%] => >1/2 class (vendor comment 'over half')")
    elif fired:
        verdict = (f"ANOMALY: selector nonzero but max owned {maxn}/50 below "
                   "band — fire unattributable to the injected set; rerun")
    elif counted:
        verdict = ("NO FIRE with counting observed (max owned "
                   f"{maxn}/50 in-band) => threshold ABOVE 58% => 2/3-class"
                   if in_band else
                   f"INCONCLUSIVE: counting only {maxn}/50 (fabrication did "
                   "not stick for the injected stars); no threshold claim")
    else:
        verdict = ("INVALID RUN: selector zero AND count never left 0 — the "
                   "campaign was never entered (resume click missed) or "
                   "ownership is not counted at .gam load; no threshold claim")
    print("VERDICT:", verdict, "| injected band 29 stars of 50")
    return 0 if (fired and in_band) or (counted and not fired and in_band) else 1

if __name__ == "__main__":
    sys.exit(main())
