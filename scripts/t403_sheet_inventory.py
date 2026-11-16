#!/usr/bin/env python3
"""t403 D12 sheet inventory: sizes + brightness mass of every candidate shot.

The t397 readability law bans browser-scaled 640x480 frames for TEXT bands, so
the sheet ships native-res crops. This tool exists to stop crop-by-guess (t397
pitfall): it prints each shot's size and non-background pixel mass per row band
so crops are chosen from measured bright runs, not from memory.

Run with the Hermes venv python (system python3 has no PIL):
  ~/tools/revenv/bin/python scripts/t403_sheet_inventory.py [glob ...]
"""
import glob
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT = ["work/r1/loop/t398-*.png", "work/r1/loop/t399-*.png",
           "work/r1/loop/t400-*.png", "work/r1/loop/t401-*.png",
           "work/r1/loop/t402-*.png"]


def bands(im, n=8):
    """Non-background pixel mass per horizontal band (bg = dominant colour)."""
    small = im.resize((160, max(1, im.height // 3)), Image.NEAREST)
    hist = [h for h in small.getcolors(1 << 20) if h]
    bg = max(hist, key=lambda t: t[0])[1]
    px = im.load()
    step = max(1, im.height // n)
    out = []
    for b in range(n):
        y0, y1 = b * step, min(im.height, (b + 1) * step)
        hits = 0
        for y in range(y0, y1, 2):
            for x in range(0, im.width, 2):
                if px[x, y] != bg:
                    hits += 1
        out.append((y0, y1, hits))
    return bg, out


def main():
    pats = sys.argv[1:] or DEFAULT
    paths = sorted(p for pat in pats for p in glob.glob(os.path.join(ROOT, pat)))
    if not paths:
        print("NO SHOTS MATCH", pats)
        return 1
    for p in paths:
        im = Image.open(p).convert("RGB")
        bg, bs = bands(im)
        rel = os.path.relpath(p, ROOT)
        mass = sum(h for _, _, h in bs)
        top = sorted(bs, key=lambda t: -h_mass(t))[:3] if mass else []
        print("%-46s %4dx%-4d bg=%-14s mass=%-7d bright bands=%s" % (
            rel, im.width, im.height, str(bg), mass,
            ",".join("%d-%d:%d" % t for t in top)))
    return 0


def h_mass(t):
    return t[2]


if __name__ == "__main__":
    sys.exit(main())
