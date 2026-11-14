#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""t386 colour-witness: whose palette is the vendor TITLE SCREEN drawn in?

Same measurement law as scripts/refcap_match.py (bit-exact membership d0,
far d4 = dist^2 > 96, 1-in-3 grid sampling) so numbers are comparable to the
banked law (movie >=85% d0; title menu 30.5% d0 / 33.9% d4 vs the intro65a
union palette, docs/re/refcap.md).

Candidate palettes are the engine's own files plus the two videos' unions.
Prints, for every candidate, d0/d4 AND the per-colour witness table for the
screenshot's own distinct colours (how many pixels of each colour are exactly
present in the candidate).

Usage: ~/tools/revenv/bin/python scripts/t386_colour_witness.py [SHOT]
"""
import importlib.util
import os
import struct
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
from PIL import Image  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "flc_probe", os.path.join(ROOT, "scripts", "flc_probe.py"))
flc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(flc)

_spec2 = importlib.util.spec_from_file_location(
    "t386", os.path.join(ROOT, "scripts", "t386_title_art.py"))
t386 = importlib.util.module_from_spec(_spec2)
_spec2.loader.exec_module(t386)


def pal_file(rel):
    p = os.path.join(ROOT, rel)
    raw = open(p, "rb").read()
    n = len(raw) // 3
    return [tuple(raw[3 * k:3 * k + 3]) for k in range(n)]


def union(path, mx=1144):
    pals = []
    flc.ftc_decode(path, on_frame=lambda i, fr, m: pals.append(list(fr.pal)),
                   max_frames=mx)
    return {c for p in pals for c in p}


def grid(im, step=3):
    px = im.load()
    w, h = im.size
    return [px[x, y] for y in range(0, h, step) for x in range(0, w, step)]


def score(sample, pal):
    s = set(pal)
    ex = sum(1 for p in sample if p in s)
    far = 0
    for p in sample:
        if p in s:
            continue
        r, g, b = p
        best = min((r - q[0]) ** 2 + (g - q[1]) ** 2 + (b - q[2]) ** 2 for q in s)
        if best > 96:
            far += 1
    return ex / len(sample), far / len(sample)


def main():
    shot = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        ROOT, "docs", "assets", "refcap", "original-title-menu.png")
    im = Image.open(shot).convert("RGB")
    sample = grid(im)
    print("shot %s %dx%d sampled %d" % (shot, im.width, im.height, len(sample)))

    counts = {}
    for p in sample:
        counts[p] = counts.get(p, 0) + 1
    top = sorted(counts.items(), key=lambda kv: -kv[1])[:12]
    print("distinct colours %d; top12 RGB:count %s" % (
        len(counts), [(list(c), n) for c, n in top]))

    gif_sw, gif_sh, gif_idx, gif_pal, gif_frames, agree = t386.gif_decode(
        os.path.join(ROOT, "extracted", "ascend01", "data", "0opening.gif"))
    gif_used = [gif_pal[i] for i in sorted(set(gif_idx))]

    cands = {"0opening.gif GCT(256)": gif_pal,
             "0opening.gif used(%d)" % len(gif_used): gif_used}
    for rel in ("extracted/ascend01/data/game.pal",
                "extracted/ascend01/data/logo.pal",
                "extracted/ascend01/data/subfont.pal"):
        if os.path.exists(os.path.join(ROOT, rel)):
            cands[os.path.basename(rel) + "(%d)" % len(pal_file(rel))] = pal_file(rel)
    for name, rel, mx in (("intro65a union", "extracted/ascend02/data/intro65a.flc", 1144),
                          ("logic.flc union", "game/logic.flc", 226)):
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            cands[name] = sorted(union(p, mx))
    for hz in ("black00", "racea03", "hilite00"):
        p = os.path.join(ROOT, "extracted/ascend01/data", hz + ".haz")
        if os.path.exists(p):
            cands[hz + ".haz"] = pal_file("extracted/ascend01/data/%s.haz" % hz)

    print("\n%-26s %8s %8s" % ("candidate", "d0", "d4"))
    for name, cl in cands.items():
        d0, d4 = score(sample, cl)
        print("%-26s %7.1f%% %7.1f%%" % (name, d0 * 100, d4 * 100))

    print("\nper-colour witness vs 0opening.gif GCT (shot colour -> matched?)")
    gs = set(gif_pal)
    for c, n in top:
        r, g, b = c
        best = min((r - q[0]) ** 2 + (g - q[1]) ** 2 + (b - q[2]) ** 2 for q in gs)
        print("  %-18s n=%-6d exact=%-5s nearest_d2=%d" % (
            str(list(c)), n, c in gs, best))


if __name__ == "__main__":
    main()
