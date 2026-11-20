#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t433 PROBE 3: HOW ARE THE INSTANCES RELATED?

Facts banked (docs/re/_wip_t433.md F4/F4b): the chrome band has MANY distinct
instances; the strategic-map instance is identical across 3 independent
sessions (ref-map == t252 == t268 == t253-baseline, 100.0%), while other
screens carry different instances, and within one session the field CHANGES
instance after certain actions (t253 design screen B -> D).

If instances were PHASE SHIFTS of one long pseudo-random buffer, some (dx,dy)
would restore high identity — and the buffer would be an extractable surface
(the t433 goal). If they are independent draws of the same law, no shift peaks
and the statistical law is the honest ceiling.

Tests on the left band (screen x0..6, y40..439) for instance pairs:
  (1) vertical shift sweep, identity vs dy  -> peak? (shift law)
  (2) index-offset test: is B == A + k (mod 256 / within ramp) for some k?
  (3) law equality: lag-1 h/v + vertical run-lengths (same law, diff pixels)

Exit 0 = verdict printed.
"""
import os, sys, numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW = open(os.path.join(ROOT, "extracted/ascend01/data/game.pal"), "rb").read()[:768]
SIX = np.frombuffer(RAW, dtype=np.uint8).reshape(256, 3).astype(np.int32)
PAL = np.clip(SIX * 4 + SIX // 16, 0, 255)


def idx_of(path, refcap):
    a = np.asarray(Image.open(path).convert("RGB")).astype(np.int32)
    if refcap:
        assert (a[:40] == 0).all(), f"{path}: expected 40 black header rows"
        a = a[40:]
    d = np.abs(a[:, :, None, :] - PAL[None, None, :, :]).sum(axis=3)
    return d.argmin(axis=2).astype(np.uint8)


def band(a):
    return a[40:440, 0:7]


def vstats(b):
    h = (b[:, :-1] == b[:, 1:]).mean()
    v = (b[:-1, :] == b[1:, :]).mean()
    runs = []
    for c in range(b.shape[1]):
        ch = b[:, c]
        d = np.flatnonzero(ch[1:] != ch[:-1])
        runs.append(np.diff(np.concatenate(([-1], d, [len(ch)]))))
    r = np.concatenate(runs)
    return h, v, (r == 1).mean(), (r == 2).mean()


def main():
    inst = {
        "A(map,vendor)": idx_of(f"{ROOT}/docs/assets/refcap/original-strategic-map.png", True),
        "B(planet,vendor)": idx_of(f"{ROOT}/docs/assets/refcap/original-planet-view.png", True),
        "C(species,vendor)": idx_of(f"{ROOT}/docs/assets/refcap/original-species-research.png", True),
        "D(t253-design)": idx_of(f"{ROOT}/work/screens/t253/tab2_hull_game.png", False),
        "E(t253-fleetclick)": idx_of(f"{ROOT}/work/screens/t253/fleet_row1_leftclick_game.png", False),
    }
    print("LAW EQUALITY (left band screen x0..6 y40..439):")
    for k, v in inst.items():
        h, vv, k1, k2 = vstats(band(v))
        b = band(v)
        print(f"  {k:18s} lag1 h/v {h:.3f}/{vv:.3f}  vrun k1/k2 {k1:.3f}/{k2:.3f}  "
              f"distinct idx {len(np.unique(b))}")

    keys = list(inst)
    print("\nSHIFT SWEEP (vertical, identity of band(A) vs band(B)[dy:]):")
    for i in range(len(keys)):
        for j in range(len(keys)):
            if i == j:
                continue
            a = band(inst[keys[i]])
            bfull = band(inst[keys[j]])
            best, bestdy = (-1, None)
            for dy in range(-300, 301):
                lo, hi = max(0, dy), min(400, 400 + dy)
                if hi - lo < 100:
                    continue
                seg = bfull[lo:hi] if dy >= 0 else bfull[lo:hi]
                aa = a[lo:hi] if dy >= 0 else a[lo - dy:hi - dy]
                if aa.shape != seg.shape:
                    continue
                idn = float((aa == seg).mean())
                if idn > best:
                    best, bestdy = idn, dy
            base = float((a == bfull).mean())
            print(f"  {keys[i]:18s} vs {keys[j]:18s} zero-shift {base*100:5.1f}%  "
                  f"best {best*100:5.1f}% at dy={bestdy}")

    print("\nINDEX-OFFSET TEST (is B == A + k?):")
    for i in range(len(keys)):
        for j in range(len(keys)):
            if i >= j:
                continue
            a = band(inst[keys[i]]).astype(int)
            b = band(inst[keys[j]]).astype(int)
            diff = (b - a) % 256
            cnt = np.bincount(diff.ravel(), minlength=256)
            top = np.argsort(-cnt)[:3]
            print(f"  {keys[i][:12]:12s} vs {keys[j][:12]:12s} top deltas "
                  f"{[(int(t), round(100*cnt[t]/diff.size,1)) for t in top]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
