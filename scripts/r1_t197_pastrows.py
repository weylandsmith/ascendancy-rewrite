#!/usr/bin/env python3
"""r1_t197_pastrows.py — what do past-span rows actually WRITE? (t197)

The X-class walk (scripts/r1_shp_unifiedlaw.py) completes H rows for 29
records only by reading stream bytes at/after the directory span end. Two
candidate truths (docs/STATE.md t197 spec):
  (a) past-span rows are TRANSPARENT/skip ops -> destination untouched or
      index-0 -> the frame looks complete (t196 vision saw a coherent planind
      ladder with blank bottom rows);
  (b) the walk has DESYNCED over the next record's header bytes -> garbage
      pixels land in the destination plane.
This probe decodes each X record unbounded into a W x H plane and reports,
for the past-span rows only: distinct palette-index count, fraction index 0,
and a hex sample — plus the byte offsets where the desynced header junk
begins. Nothing here grades codec correctness (R13); it characterises what
a faithful unbounded decoder must reproduce.
"""
import importlib.util, os, os.path, struct, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location(
    "law", os.path.join(ROOT, "scripts", "r1_shp_unifiedlaw.py"))
law = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(law)

TARGETS = collections.defaultdict(list)   # lib -> [k]
libs = sorted(set(law.glob.glob(os.path.join(ROOT, "extracted", "**", "*.shp"),
                                recursive=True)))
X = []
for p in libs:
    try:
        d, count, te, tsz, starts, ends = law.parse(p)
    except Exception:
        continue
    for k in range(count):
        if law.rec_state(d, k, starts[k], ends[k]) in ("X", "XS"):
            X.append((p, k, d, starts[k], ends[k]))

def decode_free(d, i, H, W, plane):
    """rowwalk_free + write pixels; returns per-row (start, wrote)."""
    rows = []
    for r in range(H):
        st = i; p = 0
        while True:
            C = d[i]; i += 1
            if C == 0: break
            if C == 1:
                p += d[i]; i += 1
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
        rows.append((st, r))
    return i, rows

print(f"X records: {len(X)}")
print("lib            k   WxH        past_rows  distinct_idx  frac0  sample")
for p, k, d, rec, nxt in X:
    d_off = rec if k == 0 else rec + 0x10
    s_off = rec + 8 if k == 0 else rec + 0x18
    W, H = struct.unpack_from("<II", d, d_off)
    plane = bytearray(W * H)
    i_after, rows = decode_free(d, s_off, H, W, plane)
    past = [r for (st, r) in rows if st >= nxt]
    if not past:
        print(f"{os.path.basename(p)[:-4]:14s} {k:<3d} {W}x{H:<8} 0")
        continue
    px = [plane[r * W + c] for r in past for c in range(W)]
    c = collections.Counter(px)
    sample = " ".join(f"{v:02x}" for v, n in c.most_common(5))
    print(f"{os.path.basename(p)[:-4]:14s} {k:<3d} {W}x{H:<8} {len(past):<10d} "
          f"{len(c):<12d} {c[0]/len(px):.3f}  {sample}")
