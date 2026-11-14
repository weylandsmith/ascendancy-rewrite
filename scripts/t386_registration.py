#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""t386_registration.py — is the vendor title SCREEN the GIF, blitted?

Two images are in play:
  GIF  = extracted/ascend01/data/0opening.gif  (full-screen 640x480, 53 used
         indices, reserved dark vertical band where the menu goes)
  SHOT = docs/assets/refcap/original-title-menu.png (vendor boot screenshot,
         pinned refcap pin = external-grader artifact)

Colour-membership laws are blind (scripts/t386_colour_witness.py: every
candidate palette scores d0=9.2%). So measure STRUCTURE:

 S1 landmark: the creature's eye is a single saturated red dot in the shot.
    Find it; find the GIF's saturated-red cluster; shift = difference.
 S2 silhouette geometry: per-row dark-blob x-extent in the art region
    (luma below the row's sky baseline), GIF vs shot, + bbox.
 S3 dark-panel span in the menu band vs the windows.txt button rect
    (159..477) — is the menu drawn over the GIF's reserved band?
 S4 THE DECISIVE TEST: at candidate shift (dx,dy), build the map
    gif_index -> shot_colour over the subsampled grid and count CONFLICTS
    (an index mapping to >1 colour). At the true shift, conflicts collapse
    toward zero except where the game draws its own chrome over the art.
    Null: the same statistic for a deliberately wrong shift.

Usage: ~/tools/revenv/bin/python scripts/t386_registration.py [SHOT]
"""
import importlib.util
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
from PIL import Image  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "t386", os.path.join(ROOT, "scripts", "t386_title_art.py"))
t386 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(t386)


def luma(rgb):
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def main():
    shot_p = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        ROOT, "docs", "assets", "refcap", "original-title-menu.png")
    sw, sh, gidx, gpal, gframes, agree = t386.gif_decode(
        os.path.join(ROOT, "extracted", "ascend01", "data", "0opening.gif"))
    sim = Image.open(shot_p).convert("RGB")
    spx = sim.load()
    W, H = sim.size
    print("gif %dx%d  shot %dx%d" % (sw, sh, W, H))

    # ---- S1 landmarks -----------------------------------------------------
    def red_cluster(get):
        pts = []
        for y in range(H):
            for x in range(W):
                r, g, b = get(x, y)
                if r > 120 and g < 70 and b < 70 and (r - max(g, b)) > 70:
                    pts.append((x, y))
        if not pts:
            return None, 0, []
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        xs = sorted(p[0] for p in pts)
        ys = sorted(p[1] for p in pts)
        return (cx, cy), len(pts), [(xs[0], ys[0], xs[-1], ys[-1])]
    s_red, sn, s_box = red_cluster(lambda x, y: spx[x, y])
    g_red, gn, g_box = red_cluster(lambda x, y: gpal[gidx[y * sw + x]])
    print("S1 shot saturated-red: n=%d centroid=%s bbox=%s" % (
        sn, None if not s_red else [round(v, 1) for v in s_red], s_box))
    print("S1 gif  saturated-red: n=%d centroid=%s bbox=%s" % (
        gn, None if not g_red else [round(v, 1) for v in g_red], g_box))

    # ---- S2 silhouette ----------------------------------------------------
    def silhouette(get, y0, y1):
        rows = []
        for y in range(y0, y1, 4):
            vals = [luma(get(x, y)) for x in range(W)]
            sky = sorted(vals)[-max(1, W // 10):]  # brightest decile = sky
            base = sum(sky) / len(sky)
            dark = [x for x, v in enumerate(vals) if v < base - 60]
            rows.append((y, base, len(dark),
                         (dark[0], dark[-1]) if dark else None))
        return rows
    sil_g = silhouette(lambda x, y: gpal[gidx[y * sw + x]], 0, 190)
    sil_s = silhouette(lambda x, y: spx[x, y], 0, 190)
    print("\nS2 art-region silhouette (y: n_dark, x-extent)")
    for a, b in zip(sil_g, sil_s):
        print("   gif y=%3d n=%4d %s   |  shot n=%4d %s" % (
            a[0], a[2], a[3], b[2], b[3]))
    dg = sum(a[2] for a in sil_g)
    ds = sum(b[2] for b in sil_s)
    print("   dark pixel totals (art region): gif %d shot %d ratio %.3f" % (
        dg, ds, ds / max(dg, 1)))

    # ---- S3 menu panel ----------------------------------------------------
    print("\nS3 menu-band dark spans (luma<30), y 200..470")
    cols = []
    for x in range(W):
        c = sum(1 for y in range(200, 470, 2) if luma(spx[x, y]) < 30)
        cols.append(c)
    span = [x for x, c in enumerate(cols) if c > 60]
    ss = (min(span), max(span)) if span else None
    print("   shot dark-panel x-span %s (windows.txt button rect 159..477)" % (ss,))
    gcols = []
    for x in range(W):
        c = sum(1 for y in range(200, 470, 2)
                if luma(gpal[gidx[y * sw + x]]) < 30)
        gcols.append(c)
    gspan = [x for x, c in enumerate(gcols) if c > 60]
    gs2 = (min(gspan), max(gspan)) if gspan else None
    print("   gif  dark-panel x-span %s" % (gs2,))

    # ---- S4 conflict-count map test over shifts ---------------------------
    print("\nS4 map-conflict test (subsample step 4): gif index -> shot colour")
    pts = [(x, y) for y in range(0, H, 4) for x in range(0, W, 4)]

    def conflicts(dx, dy):
        m = {}
        n = 0
        for x, y in pts:
            sx, sy = x + dx, y + dy
            if not (0 <= sx < W and 0 <= sy < H):
                continue
            g = gidx[y * sw + x]
            s = spx[sx, sy]
            cur = m.get(g)
            if cur is None:
                m[g] = s
            elif cur != s:
                n += 1
        return n, len(m)
    probes = [(0, 40), (0, 39), (0, 41), (0, 0), (0, 20), (0, 60),
              (1, 40), (-1, 40), (2, 40), (4, 40), (-4, 40), (8, 40), (-8, 40)]
    if s_red and g_red:
        ex, ey = int(round(s_red[0] - g_red[0])), int(round(s_red[1] - g_red[1]))
        probes.insert(0, (ex, ey))
        print("   eye-derived shift candidate: (%d,%d)" % (ex, ey))
    best = None
    for dx, dy in probes:
        n, k = conflicts(dx, dy)
        print("   shift (%4d,%4d): conflicts %7d / %d indices" % (dx, dy, n, k))
        if best is None or n < best[2]:
            best = (dx, dy, n)
    print("   best probe shift %s conflicts %d" % (best[:2], best[2]))
    dx, dy = best[0], best[1]
    m = {}
    for x, y in pts:
        sx, sy = x + dx, y + dy
        if not (0 <= sx < W and 0 <= sy < H):
            continue
        m.setdefault(gidx[y * sw + x], {}).setdefault(spx[sx, sy], 0)
        m[gidx[y * sw + x]][spx[sx, sy]] += 1
    uni = sum(1 for g in m if len(m[g]) == 1)
    print("   at best shift: single-valued indices %d/%d" % (uni, len(m)))
    print("   effective title map (gif index -> gif GCT colour -> shot colour):")
    for g in sorted(m):
        dom = max(m[g].items(), key=lambda kv: -kv[1])[0]
        print("      %3d  gct=%-16s -> shot %s (%d colour(s))" % (
            g, str(list(gpal[g])), list(dom), len(m[g])))
    # .haz remap hypothesis: shot = gif_palette[haz[gif_index]] ?
    print("\nS5 .haz remap hypothesis (256-byte index->index tables):")
    hazdir = os.path.join(ROOT, "extracted", "ascend01", "data")
    for fn in sorted(os.listdir(hazdir)):
        if not fn.endswith(".haz"):
            continue
        raw = open(os.path.join(hazdir, fn), "rb").read()
        if len(raw) != 256:
            continue
        hits = 0
        tot = 0
        for g in sorted(m):
            dom = max(m[g].items(), key=lambda kv: -kv[1])[0]
            tot += 1
            if gpal[raw[g]] == dom:
                hits += 1
        if tot:
            print("   %-14s matches %d/%d indices" % (fn, hits, tot))


if __name__ == "__main__":
    main()
