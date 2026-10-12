#!/usr/bin/env python3
"""r1_shp_streamlaw.py — OQ-005 t67: per-record stream-start discriminator.

Context (docs/re/shp.md S12/S14): blit FUN_0005caac reads DIMS from the
shape header (arg1 [hdr]=W-1,[hdr+8]=H-1 via EBX) and the STREAM CURSOR
from ESI := arg2 + u32[arg2+8+8*sel] + 0x18 (@0x5cb4d..0x5cb85). arg2 =
library base P+0x88 (verbatim copy; S12.2/S14.3). Row streams are
x-unbounded (writes clamp @0x5cd31/0x5cd62); draw consumes h+1 rows.

File container (S1): magic 1.10, count u32 @4, tsz u32 @8 (== 8*(count+1)),
u64 directory at 0x10 (slots 0..count-1 -> rec starts 1..count-1 plus
metadata tail), rec0 at 0x10+tsz.

Candidate per-record stream starts tested here (walk h+1 rows, report
landing vs record span [rec, next)):
  A rec+8    : dims u32-pair header, stream +8
  B rec+0x18 : dims u16-pair + 0x10 fill, stream +0x18
  C dir[k]+0x18 (blit virtual via tsz for k=0, dir slot k-1 else):
    == A for rec0 (tsz+0x18 = rec0+8) and == B for rec1+ (dir[k-1]=rec
    start) — C is the CODE law; A/B are its two halves tested per record
    index separately so failures localize.

A record PASSES when the (h+1)-row walk lands inside [rec, next] —
landing == next is exact; landing < next means tail (frame headerless
continuation measured S14.5 — tail bytes may be further frames; a
sub-frame walk landing early is allowed and reported).
"""
import os, struct, sys, glob, collections

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
    """consume H rows, x-unbounded; return pos or None if reads past end"""
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

def dims_at(d, off):
    """return list of plausible (W,H,form) readings at off"""
    out = []
    w32, h32 = struct.unpack_from("<II", d, off)
    if 0 < w32 <= 4096 and 0 < h32 <= 4096 and h32 != w32 + 1:
        out.append((w32, h32, "u32pair"))
    w16, h16 = struct.unpack_from("<HH", d, off)
    if 0 < w16 <= 4096 and 0 < h16 <= 4096:
        out.append((w16, h16, "u16pair"))
    return out

def main():
    libs = sorted(glob.glob(os.path.join(ROOT, "extracted", "**", "*.shp"),
                            recursive=True))
    lib_state = collections.Counter()
    detail_fail = []
    for p in libs:
        rel = os.path.basename(p)
        try:
            d, count, te, tsz, starts, ends = parse(p)
        except Exception as e:
            lib_state["container-err"] += 1; continue
        state = "law-C-pass"
        for k in range(count):
            rec, nxt = starts[k], ends[k]
            # CODE law C: virtual entry + 0x18
            virt = tsz if k == 0 else starts[k]   # starts[k]==dir[k-1]+0? no: starts[k] IS rec start
            # For k>=1: blit table u32 at PAY+8+8(k) holds dir[k] = starts[k+1]-te?? verify below;
            # empirical S14.3: u32[PAY+8+8k] sequence = (tsz, dir0, dir1, ...) where dir_k are
            # FILE-RELATIVE offsets recorded at file+0x10+8k. Blit entry = PAY + that value,
            # stream = entry + 0x18. For widget sel k: value = dir[k] = starts[k+1]-te.
            # => widget sel k addresses physical record k+1 header at rec_{k+1} start,
            #    stream at rec_{k+1} + 0x18. Record k=0 is addressed ONLY via tsz virtual slot.
            pass
        # Per-record INDEPENDENT test of A and B candidates:
        pat = []
        for k in range(count):
            rec, nxt = starts[k], ends[k]
            got = None
            for cand in (8, 0x18):
                for W, H, form in dims_at(d, rec):
                    if cand == 8 and form != "u32pair": continue
                    if cand == 0x18 and form != "u16pair": continue
                    pos = rowwalk(d, rec + cand, H, nxt)
                    if pos is None: continue
                    if pos <= nxt:
                        got = (cand, form, pos, nxt)
                        break
                if got: break
            pat.append("PASS" if got else f"FAIL@{k}")
        bad = [x for x in pat if x != "PASS"]
        if not bad:
            lib_state["all-records-pass"] += 1
        else:
            lib_state[f"fail x{len(bad)}"] += 1
            detail_fail.append((rel, bad[:6]))
    print("libraries:", len(libs))
    for k, v in sorted(lib_state.items()): print(f"  {k}: {v}")
    print("failures:")
    for r, b in detail_fail: print("  -", r, b)

if __name__ == "__main__":
    main()
