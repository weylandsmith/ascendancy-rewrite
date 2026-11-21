#!/usr/bin/env python3
"""tA3 TEXT LAW witness: template-fit the vendor faces against OUR 1:1
Xvfb render at the law positions, and against the vendor witnesses, and
assert (a) the BIG face wins at every TEXTITEM/newgame-label site, and
(b) our render's ink top rows land within 1 px of the law.

Law + measurements: docs/re/_wip_tA3.md. Vendor faces parsed straight
from the .fnt containers (docs/re/fnt.md law: u32 magic, N=128, HEIGHT,
255, offsets[128], per-glyph u32 width + width*H bytes, 0xFF = bg).

Usage:
  ~/tools/revenv/bin/python scripts/r1_tA3_witness.py \
      --ours-ours OURS_NEWGAME.png OURS_MAP.png \
      [--vendor-newgame scratchpad/newgame-original.png --vn-off 1] \
      [--vendor-map docs/assets/refcap/original-strategic-map.png --vm-off 40]
Exit 0 = PASS.
"""
import argparse
import struct
import sys

import numpy as np
from PIL import Image

DATA = "extracted/ascend01/data"


def load_face(path):
    d = open(path, "rb").read()
    magic, n, h, _c = struct.unpack_from("<4I", d, 0)
    assert magic == 0x2E31 and n == 128, path
    offs = struct.unpack_from("<128I", d, 16)
    W, PX = [], []
    for i in range(n):
        w = struct.unpack_from("<I", d, offs[i])[0]
        W.append(int(w))
        PX.append(d[offs[i] + 4: offs[i] + 4 + w * h])
    return W, h, PX


class Shot:
    def __init__(self, path, offx, offy):
        im = Image.open(path).convert("RGB")
        self.a = np.asarray(im, dtype=np.int32)
        self.offx, self.offy = offx, offy

    def bright(self, x, y):
        xx, yy = x + self.offx, y + self.offy
        if 0 <= xx < self.a.shape[1] and 0 <= yy < self.a.shape[0]:
            return int(self.a[yy, xx].sum()) > 420
        return False

    def exact255(self, x, y):
        xx, yy = x + self.offx, y + self.offy
        if 0 <= xx < self.a.shape[1] and 0 <= yy < self.a.shape[0]:
            return bool(self.a[yy, xx][0] == 255 and self.a[yy, xx][1] == 255
                        and self.a[yy, xx][2] == 255)
        return False

    def green(self, x, y):
        xx, yy = x + self.offx, y + self.offy
        if 0 <= xx < self.a.shape[1] and 0 <= yy < self.a.shape[0]:
            r, g, b = self.a[yy, xx]
            return bool(g >= 80 and g > r + 40 and g > b + 30)
        return False

    def lum(self, x, y):
        xx, yy = x + self.offx, y + self.offy
        if 0 <= xx < self.a.shape[1] and 0 <= yy < self.a.shape[0]:
            return float(self.a[yy, xx].mean())
        return 0.0


def glyph_cells(face, word, x, ytop):
    W, H, PX = face
    seen = set()
    xx = x
    for ch in word:
        w = W[ord(ch)]
        px = PX[ord(ch)]
        for gy in range(H):
            row = px[gy * w: gy * w + w]
            for gx in range(w):
                if row[gx] != 0xFF:
                    seen.add((xx + gx, ytop + gy))
        xx += w
    return seen




def iou(face, word, shot, x, ytop):
    H = face[1]
    seen = glyph_cells(face, word, x, ytop)
    hit = sum(1 for X, Y in seen if shot.bright(X, Y))
    miss = len(seen) - hit
    extra = 0
    xend = x + adv(face, word)
    for Y in range(ytop, ytop + H):
        for X in range(x, xend):
            if (X, Y) not in seen and shot.bright(X, Y):
                extra += 1
    return hit / max(1, hit + miss + extra)


def adv(face, word):
    return sum(face[0][ord(c)] for c in word)


def centre_x(x0, x1, word, face):
    return (x0 + x1) // 2 - adv(face, word) // 2


# (label, word, rect x0,x1, law draw-top, dy-note)
NEWGAME_SITES = [
    ("star-density", "Star Density", 7, 122, 381 + 10),
    ("species-label", "Species", 131, 246, 381 + 10),
    ("atmosphere-label", "Atmosphere", 255, 370, 381 + 10),
    ("player-color", "Player Color", 379, 493, 381 + 12),
    ("player-species-hdr", "Player Species", 502, 632, 15),
    ("begin-label", "Begin New Game", 502, 632, 455),
]
MAP_SITES = [  # rect x0=474, draw TOP = y0+2 (kRailLabelDy)
    ("rail-planets", "Planets", 130),
    ("rail-ships", "Ships", 169),
    ("rail-research", "Research", 208),
    ("rail-special", "Special Ability", 247),
    ("rail-species", "Species", 286),
]


def best_fit(face, word, shot, x, ytop, span=2):
    return max(iou(face, word, shot, x + dx, ytop + dy)
               for dx in range(-span, span + 1)
               for dy in range(-span, span + 1))


def check_shot(tag, shot, big, sm, sites, is_map=False, dynamic=None,
               fit=False):
    # dynamic = labels whose WORD depends on the campaign state (density/
    # species/atmosphere setting): a vendor shot from a different state
    # cannot be content-checked (tA1-CONT contract) — ours-side only.
    dynamic = dynamic or set()
    ok = True
    for s in sites:
        if tag.startswith("vendor") and s[0] in dynamic:
            print(f"{tag}/{s[0]}\tSKIP (dynamic word, other campaign state)")
            continue
        if is_map:
            label, word, y0 = s
            x, ytop = 474 + 2, y0 + 2
        else:
            label, word, x0, x1, ytop = s
            x = centre_x(x0, x1, word, big)
        if fit:
            # vendor browser/refcap captures drift +-1 px (banked drift
            # law); the EVIDENCE is that the best fit is the big face.
            fb = best_fit(big, word, shot, x, ytop)
            fs = best_fit(sm, word, shot, x, ytop)
        else:
            fb = iou(big, word, shot, x, ytop)
            fs = iou(sm, word, shot, x, ytop)
        # face law: big must beat sm
        good = fb >= fs + 0.10 and fb >= 0.55
        # ours-side COLOUR CLASS (tA3 F4): white-label ink must be the
        # exact core (255,255,255) on >=50% of the template cells (kLore
        # green sites excluded). Catches ink-colour mutations the
        # luminance threshold is blind to.
        if good and not fit:  # all witness sites are white-class
            cells = glyph_cells(big, word, x, ytop)
            core = sum(1 for X, Y in cells if shot.exact255(X, Y))
            frac = core / max(1, len(cells))
            g2 = frac >= 0.5
            good &= g2
            print(f"{tag}/{label}/core255\tfrac={frac:.3f}\t"
                  f"{'PASS' if g2 else 'FAIL'}")
        ok &= good
        print(f"{tag}/{label}\tbig={fb:.3f}\tsm={fs:.3f}\t"
              f"{'PASS' if good else 'FAIL'}")
    return ok


def first_ink_row(shot, x0, x1, y0, y1, kind):
    for y in range(y0, y1 + 1):
        if kind == "white" and any(shot.bright(x, y) for x in range(x0, x1 + 1)):
            return y
        if kind == "green" and any(shot.green(x, y) for x in range(x0, x1 + 1)):
            return y
    return None


BASELINES = [  # (label, x0,x1, ysearch0, ysearch1, kind, law_top, tol)
    ("base-species-name", 340, 482, 12, 30, "green", 17, 0),
    ("base-header", 505, 629, 12, 30, "white", 15, 0),
    ("base-summary", 100, 245, 320, 332, "white", 326, 0),
    ("base-lore", 336, 486, 259, 270, "green", 265, 0),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ours_newgame")
    ap.add_argument("ours_map")
    ap.add_argument("--vendor-newgame", default=None)
    ap.add_argument("--vendor-map", default=None)
    ap.add_argument("--vn-off", type=int, default=1,
                    help="browser-shot x AND y offset (newgame)")
    a = ap.parse_args()

    big = load_face(f"{DATA}/bigfont.fnt")
    sm = load_face(f"{DATA}/smfont.fnt")

    ok = True
    DYN = {"star-density", "species-label", "atmosphere-label"}
    ng = Shot(a.ours_newgame, 0, 0)
    ok &= check_shot("ours-newgame", ng, big, sm, NEWGAME_SITES, dynamic=DYN)
    for label, x0, x1, ys0, ys1, kind, law, tol in BASELINES:
        got = first_ink_row(ng, x0, x1, ys0, ys1, kind)
        good = got is not None and abs(got - law) <= tol
        ok &= good
        print(f"ours-newgame/{label}\tfirst={got}\tlaw={law}\t"
              f"{'PASS' if good else 'FAIL'}")
    ok &= check_shot("ours-map", Shot(a.ours_map, 0, 0), big, sm, MAP_SITES,
                     is_map=True)
    if a.vendor_newgame:
        ok &= check_shot("vendor-newgame",
                         Shot(a.vendor_newgame, a.vn_off, a.vn_off), big, sm,
                         NEWGAME_SITES, dynamic=DYN, fit=True)
    if a.vendor_map:
        # palette-exact refcap: root row = window row + 40, columns exact
        ok &= check_shot("vendor-map", Shot(a.vendor_map, 0, 40), big, sm,
                         MAP_SITES, is_map=True, fit=True)
    print("WITNESS", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
