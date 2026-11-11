#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t67b: failing-record autopsy (shp.md S15.3 hypothesis).

For every record failing BOTH stream-start candidates under its own
header-pair dims (r1_shp_streamlaw law), test alternative dims sources:
  N1 dims = NEXT record's header-pair readings (mask-pair law)
  N2 dims = PREV record's header-pair readings
  N3 dims = own rec+0x18 u16 pair +1 (off-by-one variants incl. W-1/H-1)
  N4 own u32 pair swapped (H,W)
Pass = H-row x-unbounded walk stays within [rec, next_rec).
Prints per-alt tally + per-record verdicts for 6 UI libs.
"""
import glob, struct, os, sys, collections, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_shp_streamlaw as S
importlib.reload(S)

def walks(d, rec, end, W, H):
    return S.rowwalk(d, rec, H, end) is not None and \
           S.rowwalk(d, rec, H, end) <= end

def cand_pass(d, rec, end):
    """original law: any (cand-offset, dims-form) walk fits [rec,end)."""
    for cand in (8, 0x18):
        for W, H, form in S.dims_at(d, rec):
            if cand == 8 and form != "u32pair": continue
            if cand == 0x18 and form != "u16pair": continue
            p = S.rowwalk(d, rec + cand, H, end)
            if p is not None and p <= end:
                return True
    return False

def alt_dims(d, off):
    """all dims guesses at off: u32pair, +1/+1, -1/-1, swapped."""
    out = []
    if off + 8 > len(d): return out
    w32, h32 = struct.unpack_from("<II", d, off)
    w16, h16 = struct.unpack_from("<HH", d, off)
    for W, H in ((w32, h32), (w32 + 1, h32 + 1), (w32 - 1, h32 - 1),
                 (h32, w32), (w16, h16), (w16 + 1, h16 + 1)):
        if 0 < W <= 4096 and 0 < H <= 4096:
            out.append((W, H))
    return out

def main():
    libs = sorted(glob.glob(os.path.join(S.ROOT, "extracted", "**", "*.shp"),
                            recursive=True))
    tally = collections.Counter()
    detail = []
    for path in libs:
        try:
            d, count, te, tsz, starts, ends = S.parse(path)
        except Exception:
            continue
        for k in range(count):
            rec, nxt = starts[k], ends[k]
            if cand_pass(d, rec, nxt):
                continue
            verdict = "STILL-FAIL"
            # N1: next record's dims (mask-pair hypothesis)
            if k + 1 < count:
                nrec = starts[k + 1]
                for cand in (8, 0x18):
                    for W, H, form in S.dims_at(d, nrec):
                        if cand == 8 and form != "u32pair": continue
                        if cand == 0x18 and form != "u16pair": continue
                        p = S.rowwalk(d, rec + cand, H, nxt)
                        if p is not None and p <= nxt:
                            verdict = f"N1-next-dims@cand{hex(cand)}"
                            break
                    if verdict != "STILL-FAIL": break
            if verdict == "STILL-FAIL":
                for off, tag in ((rec + 0x18, "N3-own"), (rec, "N4-own")):
                    for W, H in alt_dims(d, off):
                        for cand in (8, 0x18):
                            p = S.rowwalk(d, rec + cand, H, nxt)
                            if p is not None and p <= nxt:
                                verdict = f"{tag}-alt@{cand and 'c' or 'c'}{cand}"
                                break
                        if verdict != "STILL-FAIL": break
                    if verdict != "STILL-FAIL": break
            tally[verdict] += 1
            if os.path.basename(path) in ("0opening.shp", "13negot.shp",
                                          "14intel.shp", "1starmap.shp"):
                hdr = d[rec:rec + 0x28].hex()
                detail.append((os.path.basename(path), k, verdict, hdr))
    print("failing-record alternative-remediation tally:")
    for k, v in sorted(tally.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    print("\nUI-lib detail:")
    for r, k, v, h in detail:
        print(f"  {r} rec{k}: {v}  hdr={h}")

if __name__ == "__main__":
    main()
