#!/usr/bin/env python3
"""tA2-CONT ridge/recess witness: mean luminance of the newgame well edges
in a 1:1 render shot vs the vendor censuses (docs/re/_wip_tA2.md F3/F5).
Usage: r1_tA2c_witness.py <png> [xoff yoff]  (default offset 0,0 = 1:1 shot;
browser shots use +1,+1 law applied by the CALLER passing offsets)."""
import sys
import numpy as np
from PIL import Image

TARGETS = {  # (kind, coords, vendor_mean, tol)
    "row7":   ("row", (7, 7, 493), 24.3, 6.0),
    "col7":   ("col", (7, 8, 372), 6.5, 3.0),
    "col493": ("col", (493, 8, 372), 22.9, 6.0),
    "row373": ("row", (373, 7, 493), 64.5, 6.0),
    "row374": ("row", (374, 7, 493), 102.8, 6.0),
}

def main():
    path = sys.argv[1]
    im = np.asarray(Image.open(path).convert("RGB"), dtype=np.float64)
    lum = im.mean(axis=2)
    ok = True
    for name, (kind, a, vend, tol) in TARGETS.items():
        y_or_x, lo, hi = a
        band = lum[y_or_x, lo:hi + 1] if kind == "row" else lum[lo:hi + 1, y_or_x]
        m = float(band.mean())
        good = abs(m - vend) <= tol
        ok &= good
        print(f"{name}\tours={m:.1f}\tvendor={vend}\tdelta={m-vend:+.1f}\t{'PASS' if good else 'FAIL'}")
    # well purity
    for y in (8, 372):
        frac = float(np.mean(np.all(im[y, 8:493] == 0, axis=-1)))
        good = frac == 1.0
        ok &= good
        print(f"wellrow{y}\tblackfrac={frac:.3f}\t{'PASS' if good else 'FAIL'}")
    print("WITNESS", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
