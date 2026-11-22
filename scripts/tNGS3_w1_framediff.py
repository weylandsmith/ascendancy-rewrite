#!/usr/bin/env python
"""tNGS3 W1 diag: row-band diff between two raw title frames."""
import sys
from PIL import Image

a = Image.open(sys.argv[1]).convert("RGB")
b = Image.open(sys.argv[2]).convert("RGB")
pa, pb = a.load(), b.load()
W, H = a.size
changed = [y for y in range(H) if any(pa[x, y] != pb[x, y] for x in range(0, W, 2))]
bands = []
for y in changed:
    if bands and y <= bands[-1][1] + 2:
        bands[-1][1] = y
    else:
        bands.append([y, y])
print("size", W, H, "changed rows", len(changed))
print("bands", [tuple(x) for x in bands[:24]])
for lo, hi in [(275, 315), (200, 240), (240, 275)]:
    n = sum(1 for y in range(lo, hi) for x in range(W) if pa[x, y] != pb[x, y])
    print(f"px changed in {lo}..{hi}:", n)
