#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""t386 remap test — IS the vendor title screenshot the GIF under a palette map?

The colour-membership law is blind here (every candidate palette scores the
same 9.2% d0 — only black is shared), so test the STRUCTURE instead:

  H: shot[x,y] = f(gif[x,y]) for a single-valued f.

If H holds (one shot colour per GIF index over the sampled grid), the title
screen IS 0opening.gif, drawn with a different palette than the GIF's own
GCT — i.e. the vendor ships the image and re-colours it at boot.
Also report: the map, whether it is a bijection, monotone in luminance, and
whether it looks like a gamma/scale of the GIF's own GCT entries.

Usage: ~/tools/revenv/bin/python scripts/t386_remap_test.py [SHOT]
"""
import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
from PIL import Image  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "t386", os.path.join(ROOT, "scripts", "t386_title_art.py"))
t386 = importlib.util.module_from_spec(_spec)
_spec2 = _spec.loader
_spec2.exec_module(t386)


def lum(c):
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def main():
    shot = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        ROOT, "docs", "assets", "refcap", "original-title-menu.png")
    gifp = os.path.join(ROOT, "extracted", "ascend01", "data", "0opening.gif")
    sw, sh, idx, pal, frames, agree = t386.gif_decode(gifp)
    im = Image.open(shot).convert("RGB")
    if (im.width, im.height) != (sw, sh):
        print("SIZE MISMATCH shot %dx%d gif %dx%d" % (im.width, im.height, sw, sh))
    px = im.load()

    gif_used = sorted(set(idx))
    shot_cols = {}
    for y in range(sh):
        for x in range(sw):
            shot_cols[px[x, y]] = shot_cols.get(px[x, y], 0) + 1
    print("gif distinct indices %d ; shot distinct colours %d" % (
        len(gif_used), len(shot_cols)))

    # induced map on the FULL grid (not a sample): gif index -> set of shot colours
    m = {}
    conflicts = 0
    for y in range(sh):
        base = y * sw
        for x in range(sw):
            g = idx[base + x]
            s = px[x, y]
            cur = m.setdefault(g, {})
            cur[s] = cur.get(s, 0) + 1
    print("\nmap gif_index -> shot colours (dominant share)")
    uni = 0
    rows = []
    for g in sorted(m):
        cc = m[g]
        dom = max(cc.items(), key=lambda kv: -kv[1])
        frac = dom[1] / sum(cc.values())
        if len(cc) == 1:
            uni += 1
        rows.append((g, len(cc), dom[0], round(frac, 4)))
    for r in sorted(rows, key=lambda r: -r[3]):
        print("  idx %3d -> %d colour(s), dominant %s share %.4f" % (
            r[0], r[1], list(r[2]), r[3]))
    print("\nsingle-valued indices: %d/%d" % (uni, len(m)))

    # luminance ordering agreement
    doms = [(lum(pal[g]), lum(r[2][0]), g) for g, r in
            ((g, {k: v for k, v in m[g].items()}) for g in m)]
    pairs = sorted([(lum(pal[g]), lum(max(m[g], key=lambda k: m[g][k])), g) for g in m])
    a = [p[0] for p in pairs]
    b = [p[1] for p in pairs]
    inv = sum(1 for i in range(len(a)) for j in range(i + 1, len(a))
              if (a[i] - a[j]) * (b[i] - b[j]) < 0)
    print("luminance inversions between GIF GCT order and shot map: %d of %d pairs"
          % (inv, len(a) * (len(a) - 1) // 2))
    print("sample map entries (gif RGB -> shot RGB):")
    for g in sorted(m, key=lambda g: -lum(max(m[g], key=lambda k: m[g][k])))[:12]:
        print("   %s -> %s" % (list(pal[g]),
                               list(max(m[g], key=lambda k: m[g][k]))))


if __name__ == "__main__":
    main()
