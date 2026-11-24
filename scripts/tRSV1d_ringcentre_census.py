#!/usr/bin/env python3
# tRS-V1d DRAWN-CENTRE CENSUS v2 (seam TRSV1c-E closure leg).
# Usage: tRSV1d_ringcentre_census.py shot.png lx1 ly1 [lx2 ly2 ...]
# The anchor law (docs/re/_wip_tRSV1d.md P0-P2): the projected word is the
# blit ANCHOR and the record bbox (-30,-30,29,29) centres the 60x60 content
# on it, so the CONTENT bbox (pixels differing from the flat field
# background — the port paints the field a uniform colour, tPR-U item 5)
# must span crop [0..59] on both axes about the logged centre.
# v1 used a brightness threshold: its bbox is the bright-RIM subset, which
# the art biases to the top — a -1.5 y artifact, not geometry. v2 measures
# the content itself. PASS = content bbox == [0..59] +/- 1 on both axes.
# Anti-vacuity: the +30,+30-shifted crop's content bbox must NOT equal the
# same full-span (the ring must be localised to the anchor, not smeared).
import sys
from PIL import Image

def content_bbox(img, box, bg, tol=24):
    px = img.crop(box).convert("RGB")
    w, h = px.size
    xs, ys = [], []
    for y in range(h):
        for x in range(w):
            r, g, b = px.getpixel((x, y))
            if abs(r-bg[0]) + abs(g-bg[1]) + abs(b-bg[2]) > tol:
                xs.append(x); ys.append(y)
    if not xs:
        return None, 0
    return (min(xs), min(ys), max(xs), max(ys)), len(xs)

def main():
    shot = sys.argv[1]
    pts = [(int(sys.argv[i]), int(sys.argv[i+1]))
           for i in range(2, len(sys.argv), 2)]
    if not pts:
        print("usage: shot.png lx ly [...]"); return 2
    img = Image.open(shot).convert("RGB")
    W, H = img.size
    # Background = the modal of a ring OUTSIDE every disk: sample the field
    # corners of the RESWIN interior (8,46)..(476,472) minus the crops; the
    # port's field is flat so a single corner sample is representative.
    bg = img.getpixel((30, 60))
    print(f"field background sample (30,60) = {bg}")
    ok = True
    for (lx, ly) in pts:
        box = (lx - 30, ly - 30, lx + 30, ly + 30)
        if box[0] < 8 or box[1] < 46 or box[2] > 476 or box[3] > 472:
            print(f"SKIP ({lx},{ly}) crop outside RESWIN interior"); continue
        bb, n = content_bbox(img, box, bg)
        if bb is None:
            print(f"FAIL ({lx},{ly}) no content in the anchor crop")
            ok = False; continue
        # Expected content span crop [0..59]: the content must touch all
        # four crop edges (bbox == content bbox by the record's own def).
        touches = bb[0] <= 1 and bb[1] <= 1 and bb[2] >= 58 and bb[3] >= 58
        # Centre of the CONTENT bbox mapped back to absolute px:
        cx = lx - 30 + (bb[0] + bb[2]) / 2.0
        cy = ly - 30 + (bb[1] + bb[3]) / 2.0
        print(f"({'PASS' if touches else 'FAIL'}) ({lx},{ly}) content n={n} "
              f"bbox={bb} centre=({cx:.1f},{cy:.1f}) "
              f"offset=({cx-lx:+.1f},{cy-ly:+.1f})")
        ok = ok and touches
        # Anti-vacuity: shift the crop +30,+30; content must NOT fill it.
        box2 = (lx, ly, lx + 60, ly + 60)
        bb2, n2 = content_bbox(img, box2, bg)
        full2 = bb2 and bb2[0] <= 1 and bb2[1] <= 1 and bb2[2] >= 58 and bb2[3] >= 58
        print(f"  control +30,+30 crop: n={n2} "
              f"{'LEAK (ring smeared?)' if full2 else 'OK'}")
        ok = ok and not full2
    print("VERDICT", "PASS" if ok else "FAIL")
    return 0 if ok else 1

sys.exit(main())
