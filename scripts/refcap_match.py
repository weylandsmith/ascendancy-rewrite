#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""refcap_match.py — compare screenshots of the ORIGINAL game (captured by
scripts/ref_capture.sh) against the reference FLIC decode the C++ port is
pinned to (flic.cpp == golden tsv == flc_probe.py; gate 4e == on-screen).

Rule (measured 2026-10-05, docs/re/refcap.md; thresholds chosen from the
d-histogram below, not guessed):

T1 EXACT-PALETTE LAW — fraction d0 of sampled screenshot colours that are
   BIT-EXACT members of the intro65a union palette (all 1144 frames), plus
   d4 (distance^2 > 96, "far"). PASS iff d0 >= 0.85 and d4 < 0.02.
   Measured: movie frames 90.6-99.5% d0 / <=0.8% d4; tutorial menu 11.1% d0
   (its navy is a NEAR miss, ~1 channel off — tolerance rules are blind to
   exactly this, hence the exact law); title menu 30.5% d0 / 33.9% d4.
T2 CONTROL — MEASURED, NOT ASSUMED. The obvious control (score against
   logic.flc's union palette) is VACUOUS: the two vendor videos share the
   engine palette (99.5% vs 99.5% on the same shot — recorded in
   docs/re/refcap.md so nobody re-runs it). The live control is the in-run
   NEGATIVE SHOT: the title menu captured seconds before the click must FAIL
   the law (30.5% exact / 33.9% far measured). scripts/refcap_gate.sh runs
   both sides every time.
(1:1 blit row-search was tried and REFUTED — no byte-exact window exists at
   any offset (docs/re/refcap.md): the game composites the movie into a
   letterboxed band (~32..608 x ~240..452 root coords) with caption text
   that the GAME draws (zero bottom-band pixels in all 1144 decoded frames —
   the caption strings are not in any extracted file), at a scale that is
   not 1:1 with the 640x480 FLIC frames.)

Usage: ~/tools/revenv/bin/python scripts/refcap_match.py SHOT.png [--max 1144]
Exit 0: T1 and T2 pass. Exit 2: either fails (SHOT is not intro playback).
"""
import argparse
import os
import sys
import importlib.util

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_spec = importlib.util.spec_from_file_location(
    "flc_probe", os.path.join(ROOT, "scripts", "flc_probe.py"))
if _spec is None or _spec.loader is None:
    sys.exit("cannot load scripts/flc_probe.py")
flc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(flc)

from PIL import Image  # noqa: E402  (revenv host only)

INTRO = os.path.join(ROOT, "extracted", "ascend02", "data", "intro65a.flc")


def union_palette(path, max_frames):
    pals = []

    def on_frame(i, fr, meta):
        pals.append(list(fr.pal))

    flc.ftc_decode(path, on_frame=on_frame, max_frames=max_frames)
    return {c for p in pals for c in p}


def palette_hist(im, up, step=3):
    """d0 = bit-exact membership fraction, d4 = far (dist^2 > 96) fraction."""
    px = im.load()
    w, h = im.size
    exact = far = total = 0
    for y in range(0, h, step):
        for x in range(0, w, step):
            p = px[x, y]
            total += 1
            if p in up:
                exact += 1
                continue
            d = min((p[0]-q[0])**2 + (p[1]-q[1])**2 + (p[2]-q[2])**2
                    for q in up)
            if d > 96:
                far += 1
    return exact / max(total, 1), far / max(total, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shot")
    ap.add_argument("--max", type=int, default=1144)
    ap.add_argument("--expect", choices=("movie", "not-movie"), default="movie",
                    help="movie: law must PASS (exit 0). not-movie: law must "
                         "FAIL (exit 0) — the control direction.")
    a = ap.parse_args()

    im = Image.open(a.shot).convert("RGB")
    up_intro = union_palette(INTRO, a.max)
    d0, d4 = palette_hist(im, up_intro)
    law = d0 >= 0.85 and d4 < 0.02
    ok = law if a.expect == "movie" else (not law)
    print(f"{a.shot}: exact {d0:.1%}, far {d4:.1%} -> law "
          f"{'HOLDS' if law else 'FAILS'}; expected "
          f"{'HOLDS' if a.expect == 'movie' else 'FAILS'} -> "
          f"{'OK' if ok else 'VIOLATION'}")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
