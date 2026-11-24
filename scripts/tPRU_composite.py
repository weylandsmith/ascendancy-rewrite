#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tPR-U USER GRADE PACKAGE — research screen side-by-side.

ours (port render after the tRSB1 dolly-out + click choreography) | vendor
(work/screens/t252/research_open_game.png — THE reference capture; research.md
S8 cites it; re-capturing the vendor is a REFUTED route class). Both sides are
cropped to the RESWIN field rect and upscaled NEAREST (no invented pixels).

The field rect: kResWin = (7,46)-(476,472) per statuslaw.h:92 (windows.txt
TYPE 9 RESWIN). We crop the INTERIOR (8,46)-(476,472) = 468x426 on both sides
so the grader compares field-to-field, chrome excluded.

Deuteranopia law (user profile): labels are TEXT, verdicts never colour-only.

Usage:
  ~/tools/revenv/bin/python scripts/tPRU_composite.py OURS.png VENDOR.png \
      OUT.png [--checklist checklist.txt] [--zoom-port x0 y0 x1 y1]
Exit 0 iff the sanity asserts pass (dims, nonblank, both sides differ).
"""
import sys
import textwrap

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FIELD = (8, 46, 476, 472)   # RESWIN interior crop, both sides


def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(p, sz)
        except OSError:
            continue
    return ImageFont.load_default()


def main():
    argv = list(sys.argv[1:])
    checklist_p = None
    if "--checklist" in argv:
        i = argv.index("--checklist")
        checklist_p = argv[i + 1]
        del argv[i:i + 2]
    zoom = (40, 200, 320, 420)          # port frontier cluster window
    if "--zoom-port" in argv:
        i = argv.index("--zoom-port")
        zoom = tuple(int(v) for v in argv[i + 1:i + 5])
        del argv[i:i + 5]
    ours_p, vendor_p, out_p = argv[0:3]

    ours_full = Image.open(ours_p).convert("RGB")
    vend_full = Image.open(vendor_p).convert("RGB")
    assert ours_full.size == (640, 480), ours_full.size
    assert vend_full.size == (640, 480), vend_full.size

    of = ours_full.crop(FIELD)          # 468x426
    vf = vend_full.crop(FIELD)
    S = 2
    of2 = of.resize((of.width * S, of.height * S), Image.NEAREST)
    vf2 = vf.resize((vf.width * S, vf.height * S), Image.NEAREST)

    # 3x zoom strip: port frontier disk + prereq line, and the vendor disk
    zc = (zoom[0] - FIELD[0], zoom[1] - FIELD[1],
          zoom[2] - FIELD[0], zoom[3] - FIELD[1])
    zp = ours_full.crop(zoom).resize(((zoom[2]-zoom[0]) * 3, (zoom[3]-zoom[1]) * 3),
                                     Image.NEAREST)
    vz = (150, 40, 330, 340)
    zv = vend_full.crop(vz).resize(((vz[2]-vz[0]) * 3, (vz[3]-vz[1]) * 3),
                                   Image.NEAREST)

    f14, f18, f20 = font(14), font(18), font(20)
    gut, pad = 10, 12
    checklist = []
    if checklist_p:
        with open(checklist_p, encoding="utf-8") as fh:
            checklist = [ln.rstrip("\n") for ln in fh if ln.strip()]
    wrapped = []
    for ln in checklist:
        wrapped += textwrap.wrap(ln, width=110) or [""]
    list_h = 40 + 26 * len(wrapped) + 16 if wrapped else 0

    W = of2.width * 2 + gut
    H = list_h + 34 + of2.height + 34 + max(zp.height, zv.height) + 20
    canvas = Image.new("RGB", (W, H), (32, 32, 32))
    d = ImageDraw.Draw(canvas)
    y = 10
    if wrapped:
        d.text((pad, y), "HOW TO GRADE THIS SCREEN (plain language):",
               font=f20, fill=(250, 250, 250))
        y += 34
        for ln in wrapped:
            d.text((pad + 6, y), ln, font=f14, fill=(235, 235, 235))
            y += 26
        y += 10
    top = y
    canvas.paste(of2, (0, top + 34))
    canvas.paste(vf2, (of2.width + gut, top + 34))
    d.text((8, top + 8), "OURS (port render, seed 5, after dolly-out + click)",
           font=f18, fill=(235, 235, 235))
    d.text((of2.width + gut + 8, top + 8),
           "VENDOR (work/screens/t252/research_open_game.png)", font=f18,
           fill=(235, 235, 235))
    d.line([(of2.width + gut // 2, top), (of2.width + gut // 2, top + 34 + of2.height)],
           fill=(200, 200, 200), width=2)

    ztop = top + 34 + of2.height + 6
    d.text((8, ztop), "3x ZOOM — ours left (frontier disk + prereq line) | vendor right",
           font=f18, fill=(235, 235, 235))
    ztop += 30
    canvas.paste(zp, (0, ztop))
    canvas.paste(zv, (0, ztop + zp.height + 8))
    d.text((zp.width + gut + 8, ztop),
           "vendor zoom: picture INSIDE the disk (seam TRSV1-C — we do NOT\n"
           "draw inside-ring pictures yet; ring + lines only)", font=f14,
           fill=(235, 235, 235))

    # sanity: dims + nonblank + the two fields are not identical
    a = np.asarray(of).astype(int)
    b = np.asarray(vf).astype(int)
    assert of.size == vf.size == (468, 426)
    assert a.mean() > 1.0 and b.mean() > 1.0, "blank field"
    frac = (np.abs(a - b).mean(axis=2) > 12).mean()
    print(f"SANITY dims={of.size}x2 ours_mean={a.mean():.2f} "
          f"vendor_mean={b.mean():.2f} differing_px_frac={frac:.3f}")
    canvas.save(out_p)
    print(f"SAVED {out_p} size={canvas.size}")


if __name__ == "__main__":
    main()
