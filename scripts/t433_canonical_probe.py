#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t433 PROBE 2 (v3): CANONICAL OR PER-PROCESS? — aligned, offset-safe.

Laws applied (docs/re/_wip_t433.md F0/F1):
  * refcap file row = screen row + 40  -> THIS script crops refcaps by 40
    rows FIRST, so every region below is expressed in SCREEN coordinates on
    both sides. (The v1/v2 probes got this wrong; see _wip F0.)
  * refcap is palette-pure under game.pal*4+raw//16 (100.0% exact) -> strict
    index plane.
  * VNC grabs are scaler-blended (only 69.3% palette-exact) -> compared in RAW
    RGB with a +-2 gate, and additionally in index space for structure stats.

Question: does the chrome field repeat byte-exactly across independent
processes (=> a canonical surface exists and could be extracted, which is
t433's premise) or only statistically (=> the port's Markov law is the ceiling)?

Decomposition: low-pass 2x2 identity isolates the CANONICAL layout component;
high-pass (fine grain, after removing the 2x2 mean) isolates the dither. If
low-pass is ~100% while fine is ~20%, the field is canonical-layout +
per-process grain.

Exit 0 = verdict printed.
"""
import os, sys, numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW = open(os.path.join(ROOT, "extracted/ascend01/data/game.pal"), "rb").read()[:768]
SIX = np.frombuffer(RAW, dtype=np.uint8).reshape(256, 3).astype(np.int32)
PAL = np.clip(SIX * 4 + SIX // 16, 0, 255)


def load_screen(path, refcap):
    """Return (rgb HxWx3 int32, index HxW) in SCREEN coords."""
    a = np.asarray(Image.open(path).convert("RGB")).astype(np.int32)
    if refcap:
        assert (a[:40] == 0).all(), f"{path}: expected 40 black header rows"
        a = a[40:]
    assert a.shape[0] >= 440, a.shape
    d = np.abs(a[:, :, None, :] - PAL[None, None, :, :]).sum(axis=3)
    return a, d.argmin(axis=2), (d.min(axis=2) == 0).mean()


def eq_rgb(A, B, tol=2):
    return (np.abs(A - B).max(axis=2) <= tol)


def band_report(name, regions, srcs):
    print(f"\n== {name} ==")
    keys = list(srcs)
    for (y0, y1, x0, y1x) in regions:
        pass
    for r in regions:
        y0, y1, x0, x1 = r
        base = srcs[keys[0]]
        print(f"  screen y{y0}..{y1-1} x{x0}..{x1-1}")
        for k in keys[1:]:
            A = base[0][y0:y1, x0:x1]
            B = srcs[k][0][y0:y1, x0:x1]
            fine = eq_rgb(A, B).mean()
            # low-pass 2x2 mean then compare means within +-2
            def lp(X):
                h, Y = X.shape[0] - X.shape[0] % 2, X.shape[1] - X.shape[1] % 2
                return X[:h, :Y].reshape(h // 2, 2, Y // 2, 2, 3).mean(axis=(1, 3))
            low = (np.abs(lp(A) - lp(B)).max(axis=2) <= 2).mean()
            ai, bi = base[1][y0:y1, x0:x1], srcs[k][1][y0:y1, x0:x1]
            idx = (ai == bi).mean()
            print(f"    vs {k:22s} rgb+-2 {fine*100:5.1f}%  lowpass2x2 {low*100:5.1f}%  idx {idx*100:5.1f}%")


def main():
    srcs = {}
    for k, p, rc in (
        ("ref-map", "docs/assets/refcap/original-strategic-map.png", True),
        ("ref-planet", "docs/assets/refcap/original-planet-view.png", True),
        ("ref-species", "docs/assets/refcap/original-species-research.png", True),
        ("t252-map", "work/screens/t252/baseline_game.png", False),
        ("t252-map-b", "work/screens/t252/back1_game.png", False),
        ("t252-spec", "work/screens/t252/species_menu_game.png", False),
    ):
        rgb_, idx, pure = load_screen(os.path.join(ROOT, p), rc)
        srcs[k] = (rgb_, idx)
        print(f"{k:12s} palette-exact {pure*100:5.1f}%")

    band_report("CHROME LEFT BAND", [(40, 440, 0, 7)], {k: srcs[k] for k in srcs if k != "ref-map"} | {"ref-map": srcs["ref-map"]})
    band_report("CHROME TOP BAND", [(0, 7, 0, 466)], {k: srcs[k] for k in srcs})
    band_report("CHROME RIGHT STRIP", [(60, 440, 466, 473)], {k: srcs[k] for k in srcs})
    band_report("SPECIES COLUMN (speckle)", [(40, 360, 474, 632)], {k: srcs[k] for k in srcs})
    return 0


if __name__ == "__main__":
    sys.exit(main())
