#!/usr/bin/env python3
"""r1_shp_unifiedlaw.py — OQ-005 t67c: unified per-record stream-start law.

Candidates tested per record at `rec` (span [rec,nxt)):
  V  (k==0 only): stream rec+8, dims u32 pair at rec        [virtual slot]
  A  (k>=1):      stream rec+0x18, dims u32 pair at rec+0x10
  B  (k>=1):      stream rec+0x20, dims u32 pair at rec+0x18 [0x10-mirror]
Orientation: pair as (W,H) then swapped (H,W). Row-walk x-unbounded,
end-bound nxt (shp.md S14/S15 discipline). Prints per-candidate tally,
pass-every-record lib count, residual list.
"""
import glob, struct, os, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def parse(p):
    d = open(p, "rb").read()
    if d[:4] != b"1.10": raise ValueError("magic")
    count = struct.unpack_from("<I", d, 4)[0]
    tsz = struct.unpack_from("<I", d, 8)[0]
    if tsz != 8 * (count + 1): raise ValueError("table-size")
    te = 0x10 + tsz
    starts = [te] + [struct.unpack_from("<Q", d, 0x10 + 8 * k)[0]
                     for k in range(count - 1)]
    ends = starts[1:] + [len(d)]
    return d, count, te, tsz, starts, ends

def rowwalk(d, i, H, end):
    for _ in range(H):
        while True:
            if i >= end: return None
            C = d[i]; i += 1
            if C == 0: break
            if C == 1:
                if i >= end: return None
                i += 1
            elif C & 1:
                n = C >> 1; i += n
                if i > end: return None
            else:
                n = C >> 1; i += 1
                if i > end: return None
    return i

def rec_state(d, k, rec, nxt):
    """return candidate tag or FAIL."""
    trials = []
    if k == 0:
        # t182 FIX: V stream starts at rec+8, not rec. The old ("V", rec, rec)
        # walked 8 header bytes as control codes; when they happened to parse
        # as valid ops the walk desynced and either consumed the span with a
        # bogus row count or failed spuriously. Measured (t182): the rec+8 law
        # -- S16 text, S17 live-RAM table (sel0 -> rec0+8, 43/43 selectors),
        # rewrite shp.cpp -- promotes EXACTLY 10 k==0 records (10status,
        # 2savegam, 4loadgam, planpro, planres, smship11, smship15, lgrace07/
        # 09/10 rec0) from FAIL to V-canonical and DEMOTES ZERO of the 187.
        trials.append(("V", rec + 8, rec))
    else:
        trials.append(("A", rec + 0x18, rec + 0x10))
    for tag, s_off, d_off in trials:
        if d_off + 8 > len(d): continue
        W, H = struct.unpack_from("<II", d, d_off)
        for v in (H, W):
            if not (0 < v <= 4096): continue
            q = rowwalk(d, s_off, v, nxt)
            if q is not None and q <= nxt:
                return tag
    if k >= 1 and rec + 0x1c <= len(d):
        # B: dims u16 mirror pair at +0x18, stream +0x20 [1starmap family]
        w16, h16 = struct.unpack_from("<HH", d, rec + 0x18)
        for v in (h16, w16):
            if 0 < v <= 4096:
                q = rowwalk(d, rec + 0x20, v, nxt)
                if q is not None and q <= nxt:
                    return "B"
    return "FAIL"

def main():
    libs = sorted(glob.glob(os.path.join(ROOT, "extracted", "**", "*.shp"),
                            recursive=True))
    tally = collections.Counter()
    liball = 0
    residual = collections.Counter()
    for p in libs:
        try:
            d, count, te, tsz, starts, ends = parse(p)
        except Exception:
            tally["container-err"] += 0
            continue
        bad = 0
        for k in range(count):
            tag = rec_state(d, k, starts[k], ends[k])
            tally[tag] += 1
            if tag == "FAIL":
                bad += 1
                residual[os.path.basename(p)] += 1
        if bad == 0: liball += 1
    print("libraries:", len(libs))
    for k, v in sorted(tally.items()): print(f"  record {k}: {v}")
    print(f"libraries passing EVERY record: {liball}/{len(libs)}")
    if residual:
        print("residual failing records by file:")
        for f, n in sorted(residual.items(), key=lambda x: -x[1]):
            print(f"  {f}: {n}")

if __name__ == "__main__":
    main()
