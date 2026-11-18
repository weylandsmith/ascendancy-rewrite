#!/usr/bin/env python3
"""t422 CONT cycle 2: decisive test of the F8 'blit a smaller noise buffer
with vertical stretch' hypothesis (docs/re/_wip_t422.md F8).

If the vendor left chrome band were rows[y] = buf[y*s] for integer s>1
(and/or a horizontal scale), then band rows y and y+k are IDENTICAL for
every y whenever k*s is a multiple of the buffer height H, i.e. the
row-identity fraction id(k) = mean_y [row(y)==row(y+k)] must show
EXACTLY-1.0 plateaus at the k = H/s * j multiples, with a period no
larger than s*H (or 1.0 already at k = H if s==1 i.e. a fixed bitmap).

Measured on the pinned 640x480 vendor capture rows 40..479 x1..6.
A NOISE FLOOR baseline = id computed on the RIGHT-zone chrome rows
(x474..632 widget-contaminated? no -- use left band rows vs a row-shuffled
copy of itself via a prime-offset permutation to keep the census).
Verdict printed as PLATEAU (stretched buffer / fixed bitmap) or
NOISE FLOOR (per-pixel generator; statistical law is the ceiling).
"""
import numpy as np

im = np.array(__import__('PIL.Image', fromlist=['Image']).open(
    'docs/assets/refcap/original-strategic-map.png').convert('RGB'))
band = im[40:480, 1:7].astype(np.int32)          # rows x 6 x 3
H, W = band.shape[0], band.shape[1]

def ident(k, arr):
    a = arr[:len(arr) - k]
    b = arr[k:]
    return float(np.mean(np.all(a == b, axis=(1, 2))))

ks = list(range(1, 441))
vals = {k: ident(k, band) for k in ks}
# perfect-identity plateaus
perfect = [k for k in ks if vals[k] >= 0.999]
near = [(k, round(vals[k], 3)) for k in ks if vals[k] >= 0.50]
print("band", band.shape)
print("k with id>=0.999:", perfect)
print("k with id>=0.50:", near if near else "NONE")
mx = max(vals, key=lambda k: vals[k])
print(f"best k={mx} id={vals[mx]:.3f}")
print("VERDICT:", "PLATEAU -> stretched/fixed buffer (period candidates: divisors of k)"
      if perfect else "NOISE FLOOR -> no row-periodicity; per-pixel generator; "
      "statistical law is the CEILING for still-capture evidence")
