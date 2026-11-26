#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""tPF-5 differential census: industry art BOTTOM-anchored (D28 item 10).

Two witness dirs of the SAME rig (scripts/tPF5_port_witness.sh, seed 5),
rest.png each:
  --fixed   ui::stripGaugeBlitPos adds (L,T)   [shipped]
  --mutant  stripGaugeBlitPos -> {x0, y0}      [the reported bug]
The LOG line for this seed is "ui strip planind.shp rec 1 bbox(0,23)
rect(123,7) blit(123,30)" (T=23, H=77), so inside the PLIND rect
(123,7..230,106):
  FIXED   art rows 30..106, backdrop rows 7..29
  MUTANT  art rows  7..83,  backdrop rows 84..106
Backdrop here is the unlit panel interior (measured pure (0,0,0)); the rec-1
industry art is warm (mean ~ (118,71,50)), so "is this row art?" is a clean
per-row test that needs no palette guess.

Checks (all must pass to call the witness real):
  C1 fixed band rows 7..12 are BACKDROP (luminance < 12)
  C2 fixed bottom rows 100..106 are ART (luminance > 40)
  C3 mutant band rows 7..12 are ART (the bug paints art where the frame is)
  C4 mutant bottom rows 100..106 are BACKDROP (the user's black band)
  C5 anti-vacuity: the two images differ in the PLIND rect on > 20% of px
     AND differ by < 5% OUTSIDE the strip (nothing else moved)
"""
import argparse
import sys
from PIL import Image

PLIND = (123, 7, 231, 107)          # x0,y0,x1,y1 exclusive
OUTSIDE = (0, 115, 640, 480)        # below the whole strip strip


def rows(im, y0, y1, box=PLIND):
    px = im.load()
    rs = gs = bs = n = 0
    for y in range(y0, y1):
        for x in range(box[0], box[2]):
            r, g, b = px[x, y][:3]
            rs += r; gs += g; bs += b; n += 1
    return (rs / n, gs / n, bs / n)


def lum(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def frac_nonblack(im, y0, y1, box=PLIND):
    """Fraction of pixels differing from the panel backdrop (0,0,0). The
    rec-1 industry art's TOP rows are dark (~28,20,21), so a luminance
    threshold is NOT a valid 'is art' test; non-black-ness is."""
    px = im.load()
    n = hit = 0
    for y in range(y0, y1):
        for x in range(box[0], box[2]):
            n += 1
            if px[x, y][:3] != (0, 0, 0):
                hit += 1
    return hit / n


def frac_diff(a, b, box):
    pa, pb = a.crop(box), b.crop(box)
    da, pbc = list(pa.getdata()), list(pb.getdata())
    return sum(1 for x, y in zip(da, pbc) if x != y) / len(da)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixed", default="/tmp/tpf5_shots")
    ap.add_argument("--mutant", default="/tmp/tpf5_shots_mut")
    a = ap.parse_args()
    fx = Image.open(f"{a.fixed}/rest.png").convert("RGB")
    mu = Image.open(f"{a.mutant}/rest.png").convert("RGB")
    assert fx.size == mu.size == (640, 480), (fx.size, mu.size)

    fb, fa = rows(fx, 7, 13), rows(fx, 100, 107)
    mb, ma = rows(mu, 7, 13), rows(mu, 100, 107)
    print(f"FIXED  band 7..12  {tuple(round(v,1) for v in fb)}  lum={lum(fb):.1f}")
    print(f"FIXED  foot 100..106 {tuple(round(v,1) for v in fa)}  lum={lum(fa):.1f}")
    print(f"MUTANT band 7..12  {tuple(round(v,1) for v in mb)}  lum={lum(mb):.1f}")
    print(f"MUTANT foot 100..106 {tuple(round(v,1) for v in ma)}  lum={lum(ma):.1f}")

    fnb_fx, fnb_mu = frac_nonblack(fx, 7, 13), frac_nonblack(mu, 7, 13)
    foot_fx, foot_mu = frac_nonblack(fx, 100, 107), frac_nonblack(mu, 100, 107)
    print(f"non-black frac  band: fixed {fnb_fx:.3f} mutant {fnb_mu:.3f}"
          f"   foot: fixed {foot_fx:.3f} mutant {foot_mu:.3f}")
    c1 = lum(fb) < 12 and fnb_fx < 0.02
    c2 = lum(fa) > 40 and foot_fx > 0.9
    c3 = fnb_mu > 0.9          # bug paints art into the frame band
    c4 = lum(ma) < 12 and foot_mu < 0.02
    d_in = frac_diff(fx, mu, PLIND)
    d_out = frac_diff(fx, mu, OUTSIDE)
    c5 = d_in > 0.20 and d_out < 0.05
    print(f"C1 fixed band is backdrop (lum<12):        {'PASS' if c1 else 'FAIL'}")
    print(f"C2 fixed foot is art (lum>40):             {'PASS' if c2 else 'FAIL'}")
    print(f"C3 MUTANT band is art (bug paints high):   {'PASS' if c3 else 'FAIL'}")
    print(f"C4 MUTANT foot is backdrop (black band):   {'PASS' if c4 else 'FAIL'}")
    print(f"C5 differential in-rect {d_in:.3f} (>0.20), "
          f"outside {d_out:.3f} (<0.05): {'PASS' if c5 else 'FAIL'}")
    ok = all([c1, c2, c3, c4, c5])
    print("VERDICT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
