#!/usr/bin/env python3
"""t426 cycle 2 probe: is the chrome-band luminance GRADIENT a per-row
reweighting of the census colour set, or a deterministic per-pixel ramp?

Authority: docs/assets/refcap/original-{strategic-map,planet-view,
species-research}.png (640x480, palette-PURE, png = screen + 40 -> for the
map shot screen row r == png row r+40; the top band is screen 0..6).
scratchpad/galaxymap-original.png is 642x481 identity but NOT palette-pure:
used only for the bottom band, reported in RGB not index space.

Prints:
  A. TOP band per-row index census (screen rows 0..7), three x-zones.
  B. LEFT band per-column census restricted to rows 60..460 (control: must
     reproduce the t422 F7 numbers) AND per-row census restricted to the
     interior rows (tests whether the left band has a row gradient too).
  C. RIGHT strip cols 466..472 per-row census (screen rows 0..20 + interior).
  D. CROSS-SCREEN identity of the top band (map vs planet vs species) at
     zero shift -> is the gradient part of the screen-fixed field?
  E. Per-row mean luminance profile for each band (the gradient curve).
Read-only census; exit 0.
"""
import collections
import sys

import numpy as np
from PIL import Image

MAP = np.asarray(Image.open(
    "docs/assets/refcap/original-strategic-map.png").convert("RGB"))
PLA = np.asarray(Image.open(
    "docs/assets/refcap/original-planet-view.png").convert("RGB"))
SPE = np.asarray(Image.open(
    "docs/assets/refcap/original-species-research.png").convert("RGB"))
SCR = np.asarray(Image.open(
    "scratchpad/galaxymap-original.png").convert("RGB"))
PAL = open("extracted/ascend01/data/game.pal", "rb").read()
conv = [(PAL[3*i] * 255 // 63, PAL[3*i+1] * 255 // 63, PAL[3*i+2] * 255 // 63)
        for i in range(256)]
cmap = {c: i for i, c in enumerate(conv)}


def idx(px):
    return cmap.get(tuple(int(v) for v in px), None)


def lum(px):
    c = tuple(int(v) for v in px)
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def census(region):
    """index -> count over a region of pixels; None bucket = OFF-palette."""
    out = collections.Counter()
    for px in np.asarray(region).reshape(-1, 3):
        i = idx(px)
        out[i if i is not None else -1] += 1
    return out


def show(tag, reg):
    c = census(reg)
    tot = sum(c.values())
    items = sorted(c.items(), key=lambda kv: -kv[1])[:8]
    body = " ".join(
        f"{'OFF' if k < 0 else k}:{n * 100.0 / tot:.1f}" for k, n in items)
    print(f"{tag:26s} n={tot:6d} {body}")


print("== A. TOP band per-row (screen y = png y - 40), map shot ==")
for y in range(0, 9):
    png = y + 40
    show(f"row{y} x60..420", MAP[png, 60:421])
for y in range(0, 9):
    png = y + 40
    show(f"row{y} x7..59", MAP[png, 7:60])
for y in range(0, 9):
    png = y + 40
    show(f"row{y} x421..465", MAP[png, 421:466])
for y in range(0, 9):
    png = y + 40
    show(f"row{y} x0..6", MAP[png, 0:7])

print("\n== A2. mean luminance profile, top band rows 0..9 (x60..420) ==")
for y in range(0, 10):
    png = y + 40
    lums = [lum(p) for p in MAP[png, 60:421]]
    print(f"row{y}: mean {np.mean(lums):6.1f} p10 {np.percentile(lums,10):6.1f}"
          f" p50 {np.percentile(lums,50):6.1f} p90 {np.percentile(lums,90):6.1f}")

print("\n== B. LEFT band control: per-column census rows 60..460 ==")
for x in range(0, 8):
    show(f"col{x} rows60..460", MAP[60:461, x:x+1])
print("-- left band per-ROW census (interior x0..6), rows 60..460 step 40 --")
for y in range(60, 461, 40):
    show(f"rows{y}..{y+39} x0..6", MAP[y:y+40, 0:7])

print("\n== C. RIGHT strip cols 466..472 per-row ==")
for y in list(range(0, 12)) + [60, 100, 200, 300, 400, 460]:
    png = y + 40 if y + 40 < MAP.shape[0] else None
    if png is None:
        continue
    show(f"row{y} x466..472", MAP[png, 466:473])

print("\n== C2. right strip mean luminance rows 0..12 (x466..472) ==")
for y in range(0, 13):
    lums = [lum(p) for p in MAP[y + 40, 466:473]]
    print(f"row{y}: mean {np.mean(lums):6.1f}")

print("\n== D. CROSS-SCREEN top-band identity at zero shift ==")
for name, img in (("planet", PLA), ("species", SPE)):
    for y in range(0, 8):
        png = y + 40
        a = MAP[png, 0:466]
        b = img[png, 0:466]
        same = int(np.all(a == b, axis=-1).sum())
        print(f"{name:8s} row{y} x0..465: {same}/{a.shape[0]} "
              f"{same*100.0/a.shape[0]:.1f}%")

print("\n== E. BOTTOM band from scratchpad (NON-PURE, identity rows) ==")
for y in range(468, min(481, SCR.shape[0])):
    lums = [lum(p) for p in SCR[y, 60:421]]
    print(f"srow{y}: mean {np.mean(lums):6.1f} p10 {np.percentile(lums,10):6.1f}"
          f" p50 {np.percentile(lums,50):6.1f} p90 {np.percentile(lums,90):6.1f}")
print("-- scratchpad bottom census rows 473..479 (index space, best-effort) --")
show("rows473..479 x60..420", SCR[473:480, 60:421])
print("-- scratchpad TOP band rows 0..7 (identity, compare vs pure map) --")
for y in range(0, 8):
    show(f"srow{y} x60..420", SCR[y, 60:421])

print("\n== F. vertical run-length of the top band (row 3, x60..420) ==")
for y in (0, 3, 5, 6):
    seq = [idx(p) for p in MAP[y + 40, 60:421]]
    runs = collections.Counter()
    cur, n = seq[0], 1
    for v in seq[1:]:
        if v == cur:
            n += 1
        else:
            runs[min(n, 6)] += 1
            cur, n = v, 1
    runs[min(n, 6)] += 1
    tot = sum(runs.values())
    print(f"row{y} h-run " + " ".join(
        f"k{k}:{runs[k]*1.0/tot:.3f}" for k in range(1, 7)))
sys.exit(0)
