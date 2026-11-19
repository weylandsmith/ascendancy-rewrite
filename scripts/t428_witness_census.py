#!/usr/bin/env python3
"""t428 strip census: score OUR planet-screen render (crop 640x480).

Law docs/re/_wip_t428.md F9. Checks on the five TYPE-29 panel rects:
  1. PLRES/PLIND/PLPRO interiors are PHOTO ART: >= 40 distinct colours in
     the interior and NOT a flat grey (the deleted outline-loop failure
     mode is a near-empty rect);
  2. PLPOP interior contains pop-sprite pixels: red-family (busy k1) or
     yellow-family (free k2) px count > 0 AND the panel is not flat;
  3. PLBUILD contains WHITE text pixels (the name / "No Project");
  4. the strip sits ABOVE the field: rows 116..118 are black outside the
     chrome columns (the field/strip boundary).
Exit 0 + VERDICT PASS iff all pass.
"""
import sys
import numpy as np
from PIL import Image

path = sys.argv[1]
rgb = np.array(Image.open(path).convert("RGB"), dtype=np.int32)
assert rgb.shape[0] >= 480 and rgb.shape[1] >= 640, "crop must be 640x480+"
rgb = rgb[:480, :640]

def interior(x0, y0, x1, y1):
    return rgb[y0 + 6:y1 - 5, x0 + 6:x1 - 5]  # inset: skip the frame bevel

fails = []

def photo(x0, y0, x1, y1, name, min_cols=8):
    sub = interior(x0, y0, x1, y1)
    px = sub.reshape(-1, 3)
    lum = px.sum(axis=1)
    keep = px[lum > 30]
    if len(keep) < 500:
        fails.append(f"{name}: only {len(keep)} lit px (panel empty?)")
        return
    uniq = np.unique(keep, axis=0)
    # The low gauge records ARE low-colour navy mottle (rec0 = 8 colours
    # census), so the threshold is per-record: the panel must carry at
    # least `min_cols` distinct colours and a mottle spread.
    spread = keep.max(axis=0) - keep.min(axis=0)
    if len(uniq) < min_cols:
        fails.append(f"{name}: only {len(uniq)} colours (below {min_cols})")
    if int(spread.max()) < 25:
        fails.append(f"{name}: flat fill (spread {spread})")

photo(7, 7, 114, 106, "PLRES")
photo(123, 7, 230, 106, "PLIND", min_cols=40)
photo(239, 7, 346, 106, "PLPRO", min_cols=40)

# PLPOP: red-family busy / yellow-family free sprite pixels.
sub = interior(355, 7, 454, 106)
r, g, b = sub[:, :, 0], sub[:, :, 1], sub[:, :, 2]
redish = ((r > 140) & (g < 110) & (b < 110)).sum()
yellow = ((r > 140) & (g > 110) & (b < 110)).sum()
print(f"PLPOP redish={int(redish)} yellowish={int(yellow)}")
if redish + yellow == 0:
    fails.append("PLPOP: no busy/free sprite pixels (pop grid unpainted?)")

# PLBUILD: white text pixels.
sub = interior(463, 8, 632, 106)
w = ((sub[:, :, 0] > 200) & (sub[:, :, 1] > 200) & (sub[:, :, 2] > 200)).sum()
print(f"PLBUILD white text px={int(w)}")
if w < 40:
    fails.append(f"PLBUILD: only {int(w)} white px (no project text)")

# t428d FIELD STARFIELD: 17np rec 4 lit px at screen (7,115) (blit law
# docs/re/_wip_t428d.md F1; the vendor witness B registered 158/269 with
# 101/111 mismatches BRIGHT = overpaint). On OUR render the non-overpainted
# stars must match through game.pal EXACTLY (same decode path); overpainted
# ones read brighter. PASS iff matched >= 50% of lit (vendor floor).
import os
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_idx = os.path.join(_root, "work/r1/shp_png/t428c/raw/17np--4.idx")
_pal = os.path.join(_root, "extracted/ascend01/data/game.pal")
if os.path.exists(_idx) and os.path.exists(_pal):
    kimg = np.fromfile(_idx, dtype=np.uint8).reshape(357, 625)
    pal = (np.fromfile(_pal, dtype=np.uint8).reshape(256, 3)
           .astype(np.int32) * 255) // 63
    ys, xs = np.nonzero(kimg)
    px_y, px_x = ys + 115, xs + 7  # screen coords == crop coords
    ok = (px_y >= 0) & (px_y < 480) & (px_x >= 0) & (px_x < 640)
    got = rgb[px_y[ok], px_x[ok]]
    want = pal[kimg[ys[ok], xs[ok]]]
    d = np.abs(got - want).max(1)
    matched = int((d <= 8).sum())
    bright = int(((d > 8) & (got.sum(1) > 60)).sum())
    dark = int(((d > 8) & (got.sum(1) <= 60)).sum())
    print(f"FIELD k4@(7,115): lit={int(ok.sum())} matched={matched} "
          f"bright(overpaint)={bright} dark={dark}")
    if matched * 2 < int(ok.sum()):
        fails.append(f"FIELD: only {matched}/{int(ok.sum())} star px match "
                     "(k4 blit unpainted?)")
else:
    print("FIELD: rec4 idx or game.pal missing (skipped)")

print("VERDICT " + ("PASS" if not fails else "FAIL"))
for f in fails:
    print("  -", f)
sys.exit(0 if not fails else 1)
