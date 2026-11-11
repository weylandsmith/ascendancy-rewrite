#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r1_t197_pastrows2.py — are the past-span rows the NEXT record's top rows?

Follow-up to r1_t197_pastrows.py: planind/3cfgnew past-span rows paint many
distinct non-zero palette indices (not transparent). Hypothesis: the walk,
running off its own span, walks the FOLLOWING record's stream with the same
dims, so the past-span rows reproduce the next record's top-of-frame rows.
Test: decode record k unbounded, decode k+1 bounded-normal, compare row-for-
row similarity of k's past rows against k+1's leading rows (and against k's
own leading rows as a control). sim = fraction of equal pixels.
"""
import importlib.util, os, struct, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location(
    "law", os.path.join(ROOT, "scripts", "r1_shp_unifiedlaw.py"))
law = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(law)

def decode_free(d, i, H, W):
    plane = bytearray(W * H)
    rows = []
    for r in range(H):
        st = i; p = 0
        while True:
            C = d[i]; i += 1
            if C == 0: break
            if C == 1: p += d[i]; i += 1
            elif C & 1:
                n = C >> 1
                for j in range(n):
                    if p < W: plane[r * W + p] = d[i + j]
                    p += 1
                i += n
            else:
                n = C >> 1; v = d[i]; i += 1
                for j in range(n):
                    if p < W: plane[r * W + p] = v
                    p += 1
        rows.append(st)
    return plane, rows

def sim(a, ao, b, bo, W):
    pa = a[ao * W: ao * W + W]; pb = b[bo * W: bo * W + W]
    return sum(1 for x, y in zip(pa, pb) if x == y) / W

libs = sorted(set(law.glob.glob(os.path.join(ROOT, "extracted", "**", "*.shp"),
                                recursive=True)))
print("lib          k  past_rows  sim(past->k+1 top)  sim(past->k own top)")
for p in libs:
    try:
        d, count, te, tsz, starts, ends = law.parse(p)
    except Exception:
        continue
    for k in range(count):
        if law.rec_state(d, k, starts[k], ends[k]) not in ("X", "XS"):
            continue
        rec, nxt = starts[k], ends[k]
        d_off = rec if k == 0 else rec + 0x10
        s_off = rec + 8 if k == 0 else rec + 0x18
        W, H = struct.unpack_from("<II", d, d_off)
        plane, rows = decode_free(d, s_off, H, W)
        # rows[] holds each row's stream START offset (appended above);
        # enumerate gives (row_index, start) — do not flip the unpack.
        past_idx = [idx for (idx, st) in enumerate(rows) if st >= nxt]
        if not past_idx or k + 1 >= count:
            continue
        nx_rec, nx_nxt = starts[k + 1], ends[k + 1]
        nd_off = nx_rec + 0x10; ns_off = nx_rec + 0x18
        nW, nH = struct.unpack_from("<II", d, nd_off)
        if nW != W:
            print(f"{os.path.basename(p)[:-4]:12s} {k:<2d} {len(past_idx):<10d} "
                  f"next rec dims {nW}x{nH} != {W}x{H} (no row compare)")
            continue
        nplane, _ = decode_free(d, ns_off, nH, nW)
        r0 = past_idx[0]
        s_next = sim(plane, r0, nplane, 0, W)
        s_own = sim(plane, r0, plane, 0, W)
        print(f"{os.path.basename(p)[:-4]:12s} {k:<2d} {len(past_idx):<10d} "
              f"{s_next:.3f}                {s_own:.3f}")
