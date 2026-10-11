#!/usr/bin/env python3
"""r1_trajectory_regression.py — t49 BLOCKED-route ONE RUN.

Ship array law [verified verbatim, FUN_00022304]: base DAT_0003a095
runtime = B + 0x82bb0 + 0x3a095, stride 0x162, max 0x6b slots, live
count = dword at runtime(B + 0x82bb0 + 0x43489) >> 0x10; slot owner
byte = dword[ship+0x54] >> 0x10; state byte +0x58 (4 = in flight);
3-D float coords floats at +0x9e/+0xa2/+0xa6; queued orders count
dword +0x15a; gizmo design field dword +0x10.

Regression question (BLOCKED.md t48): per turn, does an in-flight
ship's float displacement correlate with (drive Level sum + design
base)? For each run, consecutive-save pairs (slot numbers n, n+1 in
same run dir): for every state-4 ship, delta3 = coord[n+1] - coord[n],
|d| vs the ship's design base +0x10. We do NOT have per-ship gizmo
Level lists decoded; design base +0x10 is the aggregate stat t47/S10
law puts drive sums INTO -- so +0x10 alone IS the Level-sum proxy.
Exit 0: |d| shows a clean nonzero linear pattern vs +0x10 (upgrade).
Exit 1: no in-flight ships, OR deltas zero/uncorrelated (null branch:
campaign law = queued turn word; immediate-arrival correct).
Exit 2: harness broken.
"""
import math
import os
import struct
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_income_law as IL
from r1_sav_scan import build_anchors

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "work", "r1")
STRIDE = 0x162


def ship_view(m, B):
    """return {idx: (state, (x,y,z), base10, orders)} for live slots.

    Mapping note [t49 measured]: the empirically-consistent read of the
    ship array is HEAP span: arr = B + 0x82bb0 + 0x3a095, count = WORD
    at B + 0x82bb0 + 0x43483 (the dword 0x43489>>16 image-span guess
    read 200 uniformly = wrong). In every banked save: count 5, all
    slots owner 0xFFFF state 0 pos (0,0,0)."""
    arr = B + 0x82bb0 + 0x3a095
    cnt = struct.unpack_from("<H", m, B + 0x82bb0 + 0x43483)[0]
    out = {}
    if not (0 < cnt <= 0x6B) or arr + cnt * STRIDE > len(m):
        return out
    for i in range(cnt):
        s = arr + i * STRIDE
        st = m[s + 0x58]
        x, y, z = struct.unpack_from("<fff", m, s + 0x9e)
        b10 = struct.unpack_from("<i", m, s + 0x10)[0]
        nq = struct.unpack_from("<i", m, s + 0x15a)[0]
        if not all(math.isfinite(v) for v in (x, y, z)):
            continue
        out[i] = (st, (x, y, z), b10, nq)
    return out


def main():
    try:
        build_anchors(IL.PAY)
    except Exception as e:
        print("ANCHORS FAIL:", e)
        return 2
    pairs = 0
    inflight = 0
    zero_delta = 0
    nonzero = []   # (|d|, base10, dxyz, st_next)
    for d in sorted(os.listdir(BASE)):
        rp = os.path.join(BASE, d)
        if not os.path.isdir(rp):
            continue
        if not (os.path.isdir(os.path.join(rp, "save")) or os.path.isdir(os.path.join(rp, "ck"))):
            continue
        src = rp
        for sub in ("save", "ck"):
            if os.path.isdir(os.path.join(rp, sub)):
                src = os.path.join(rp, sub)
                break
        names = [f for f in os.listdir(src) if f.endswith(".sav")]
        nums = sorted(int(f[:-4]) for f in names if f[:-4].isdigit())
        views = {}
        try:
            allslots = IL.load_slots(rp)
        except Exception:
            continue
        for f, m, B in allslots:
            try:
                n = int(f[:-4])
            except ValueError:
                continue
            views[n] = ship_view(m, B)
        ks = sorted(views)
        for a, b in zip(ks, ks[1:]):
            if b != a + 1:
                continue
            va, vb = views[a], views[b]
            pairs += 1
            for i, (st, xyz, b10, nq) in va.items():
                if st != 4 or i not in vb:
                    continue
                inflight += 1
                st2, xyz2, _, _ = vb[i]
                dd = tuple(p2 - x for p2, x in zip(xyz2, xyz))
                mag = math.sqrt(sum(v * v for v in dd))
                if mag < 1e-6:
                    zero_delta += 1
                else:
                    nonzero.append((mag, b10, dd, st2))
    print(f"consecutive pairs: {pairs}, state-4 observations: {inflight}")
    print(f"zero deltas: {zero_delta}, nonzero: {len(nonzero)}")
    if nonzero:
        mags = sorted(m for m, *_ in nonzero)
        print("nonzero |d| min/med/max:",
              round(mags[0], 1), round(mags[len(mags)//2], 1), round(mags[-1], 1))
        print("sample (|d|, design base +0x10, delta):")
        for m, b10, dd, st2 in nonzero[:10]:
            print(f"  {m:9.1f}  base {b10:6d}  d=({dd[0]:8.1f},{dd[1]:8.1f},{dd[2]:8.1f}) ->st {st2}")
    if inflight == 0:
        print("VERDICT: null — no in-flight ships anywhere in corpus")
        return 1
    # crude correlation check nonzero |d| vs base
    if len(nonzero) >= 3:
        xs = [b for _, b, _, _ in nonzero]
        ys = [m for m, _, _, _ in nonzero]
        mx, my = sum(xs)/len(xs), sum(ys)/len(ys)
        cov = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
        vx = sum((x-mx)**2 for x in xs) ** .5
        vy = sum((y-my)**2 for y in ys) ** .5
        r = cov/(vx*vy) if vx and vy else 0.0
        print(f"corr(|d|, design base) r={r:.3f} n={len(nonzero)}")
    return 0 if len(nonzero) >= 5 else 1


if __name__ == "__main__":
    sys.exit(main())
