#!/usr/bin/env python3
"""r1_shp_unifiedlaw.py — OQ-005 t67c: unified per-record stream-start law.

Candidates tested per record at `rec` (span [rec,nxt)):
  V  (k==0 only): stream rec+8, dims u32 pair at rec        [virtual slot]
  A  (k>=1):      stream rec+0x18, dims u32 pair at rec+0x10
  B  (k>=1):      stream rec+0x20, dims u32 pair at rec+0x18 [0x10-mirror]
  X  (t197):      canonical slot/dims, EXACT-H walk with NO span bound
                  (blit law: no length arg, verbatim whole-library cache);
                  XS = only the swapped orientation completes.
Orientation: pair as (W,H) then swapped (H,W). Row-walk x-unbounded,
end-bound nxt (shp.md S14/S15 discipline) for V/A/B; X drops the end-bound.
Prints per-candidate tally, pass-every-record lib count, residual list, and
per-X paint profiles (t197). --no-x restores the pre-t197 semantics.
"""
import argparse, glob, struct, os, sys, collections

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

def rowwalk_free(d, i, H, W):
    """t197 X-class walk: S9 grammar, EXACTLY H rows, NO [rec,nxt) bound.

    Why the bound comes off (docs/re/shp.md S20.2, t196): the shape blit
    FUN_0005caac takes NO stream-length argument (5 args: shape-struct,
    payload base, selector, x, y) and its error set is {-1 missing dims
    @0x5cb2b, -2 empty clip @0x5cb36, -3 fully outside @0x5cea5} - there is
    no stream-overrun code, so the vendor decoder walks H rows and cannot
    consult the file directory span. The draw-time cache is a VERBATIM
    whole-library copy (S10/S12), so bytes past the directory span are
    resident; the file itself (len(d)) is the sole hard bound.

    Returns (i_after, painted) where painted[r] = pixels actually written
    (literal/run, clamped at W) in row r, or None if the walk cannot
    complete H rows inside the file.
    """
    painted = []
    for _ in range(H):
        p = 0; n_paint = 0
        while True:
            if i >= len(d): return None
            C = d[i]; i += 1
            if C == 0: break
            if C == 1:
                if i >= len(d): return None
                i += 1
            elif C & 1:
                n = C >> 1
                if i + n > len(d): return None
                n_paint += min(n, max(0, W - p)); p += n; i += n
            else:
                n = C >> 1
                if i + 1 > len(d): return None
                n_paint += min(n, max(0, W - p)); p += n; i += 1
        painted.append(n_paint)
    return i, painted

def rec_state(d, k, rec, nxt, allow_x=True):
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
        # t197 dims gate = the rewrite's (blit-faithful): BOTH pair
        # components must be sane or the record FAILS. The old code skipped
        # an invalid orientation with `continue` and happily walked the
        # other one, which "passed" degenerate frames the vendor blit
        # refuses (-1 missing dims @0x5cb2b / -2 empty clip @0x5cb36):
        # mouse k5 (W=0, H=46) and sg64expl k0 (H=0xfffffffb) — the only 2
        # records affected corpus-wide, demoted here, zero other changes.
        if not (0 < W <= 4096 and 0 < H <= 4096): continue
        for v in (H, W):
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
    # X (t197): the bound was our artifact. Canonical stream slot + canonical
    # dims (V/A slots; NO candidate search - R2), EXACT-H walk with no
    # directory-span bound (rowwalk_free: blit law S12/S20.2). A record is X
    # only if it FAILED the bounded law above; nothing that passed V/A/B can
    # be demoted. Orientation: H rows first, swapped only if H fails (the
    # canonical-orientation records all complete H-first; swapped-X is
    # reported as such in the paint profile).
    d_off = rec if k == 0 else rec + 0x10
    s_off = rec + 8 if k == 0 else rec + 0x18
    if allow_x and d_off + 8 <= len(d):
        W, H = struct.unpack_from("<II", d, d_off)
        if 0 < H <= 4096 and 0 < W <= 4096:
            if rowwalk_free(d, s_off, H, W) is not None:
                return "X"
            if W != H and rowwalk_free(d, s_off, W, H) is not None:
                return "XS"
    return "FAIL"

def x_profile(d, k, rec, nxt):
    """Paint profile for an X/XS record: rows_done of declared H, how many
    trailing rows paint 0 px (transparent skip ops), and where the span ends.
    Distinguishes (t196 S4 / STATE t197 spec): 'trailing all-skip rows' tail
    vs 'header-desync tail' (rows past the span whose painted px come from
    the NEXT record's header bytes parsed as ops)."""
    d_off = rec if k == 0 else rec + 0x10
    s_off = rec + 8 if k == 0 else rec + 0x18
    W, H = struct.unpack_from("<II", d, d_off)
    r = rowwalk_free(d, s_off, H, W)
    swapped = False
    if r is None:
        r = rowwalk_free(d, s_off, W, H); W, H = H, W; swapped = True
    if r is None: return None
    i_after, painted = r
    # Per-row stream starts via a parallel free walk (the free walk above
    # already proved this terminates inside the file).
    starts = []
    i = s_off
    for _ in range(H):
        starts.append(i)
        while True:
            if i >= len(d): break
            C = d[i]; i += 1
            if C == 0: break
            if C == 1: i += 1
            elif C & 1: i += (C >> 1)
            else: i += 1
    n_past = sum(1 for s in starts if s >= nxt)
    n_skip_past = sum(1 for s, p in zip(starts, painted) if s >= nxt and p == 0)
    return dict(W=W, H=H, swapped=swapped, rows_done=len(painted),
                i_after=i_after, bytes_past=max(0, i_after - nxt),
                rows_past=n_past, skip_rows_past=n_skip_past)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-x", action="store_true",
                    help="pre-t197 semantics: bounded V/A/B only")
    ap.add_argument("--profiles", action="store_true",
                    help="print per-X paint profile lines")
    a = ap.parse_args()
    libs = sorted(glob.glob(os.path.join(ROOT, "extracted", "**", "*.shp"),
                            recursive=True))
    tally = collections.Counter()
    liball = 0
    residual = collections.Counter()
    xprofiles = []
    for p in libs:
        try:
            d, count, te, tsz, starts, ends = parse(p)
        except Exception:
            tally["container-err"] += 0
            continue
        bad = 0
        for k in range(count):
            tag = rec_state(d, k, starts[k], ends[k], allow_x=not a.no_x)
            tally[tag] += 1
            if tag == "FAIL":
                bad += 1
                residual[os.path.basename(p)] += 1
            elif tag in ("X", "XS"):
                prof = x_profile(d, k, starts[k], ends[k])
                prof.update(lib=os.path.basename(p), k=k, tag=tag)
                xprofiles.append(prof)
        if bad == 0: liball += 1
    print("libraries:", len(libs))
    for k, v in sorted(tally.items()): print(f"  record {k}: {v}")
    print(f"libraries passing EVERY record: {liball}/{len(libs)}")
    if a.profiles and xprofiles:
        print("X paint profiles (rows_past = rows whose stream bytes begin "
              "at/after the dir span end; skip_past = those painting 0px):")
        for pr in xprofiles:
            print(f"  {pr['lib'][:-4]:14s} k{pr['k']:<3d} {pr['tag']:<2s} "
                  f"{pr['W']}x{pr['H']} rows={pr['rows_done']} "
                  f"past={pr['rows_past']}r/{pr['bytes_past']}B "
                  f"skip_past={pr['skip_rows_past']}"
                  + (" SWAPPED" if pr["swapped"] else ""))
    if residual:
        print("residual failing records by file:")
        for f, n in sorted(residual.items(), key=lambda x: -x[1]):
            print(f"  {f}: {n}")

if __name__ == "__main__":
    main()
