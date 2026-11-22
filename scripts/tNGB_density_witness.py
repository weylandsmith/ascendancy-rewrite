#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tNGB_density_witness — B1 density-wheel REBUILD witness.

Law (docs/re/_wip_tNGB.md): the vendor density click calls FUN_000226e4 =
full galaxy regenerate (0x22728 is a rand() consumer), so the DISPLAYED
star set changes on EVERY click and its COUNT is the ladder rung. Our
port models this with a per-click MapGenerator rebuild (seed = base+gen).

Checks (on scripts/tNGB_density_shot.sh captures, rungs 50,75,100,15,25):
 1. app.log regen lines: gen 1..4 star counts == 75,100,15,25.
 2. cosmos-n law line: the RENDERED preview cosmos count sequence is
    [50,75,100,15,25] (initial + one per click) — the display galaxy is
    the wheel galaxy, not a frozen default.
 3. SET IDENTITY: h15 (hash of the first 15 star positions, printed per
    regen) must take FOUR DISTINCT values. MapGenerator at a fixed seed is
    prefix-structured, so a seed not riding gen repeats h15 (M4 mutant);
    the rand law requires a new stream per click. Pixel-space equal-N tests
    are unusable here: the four-way class law flickers which stars are
    detectable, so cross-shot overlap is a random ~30% subset either way
    (docs/re/_wip_tNGB.md discriminator analysis).
 4. Begin-panel star mass tracks N (monotone-consistent: 100-rung >
    15-rung, 75-rung > 50-rung).
Exit 0 = witness green.
"""
import re
import sys

import numpy as np
from PIL import Image

OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/tNGB_density"
# Begin panel visual (menulaw.h kBeginPanelVisual) left band: dots+stars,
# left of the emblem ring (ring outer x572).
BX0, BY0, BX1, BY1 = 502, 381, 570, 472


def band(path):
    im = np.asarray(Image.open(path).convert("RGB"))[:, :, :3]
    crop = im[BY0:BY1 + 1, BX0:BX1 + 1].astype(int)
    mx = crop.max(axis=2)
    # coloured star ink: channels spread (vendor star px census F15-3b are
    # chromatic; the navy panel fill (12,32,48) spread 36 and grey dots
    # spread ~0 stay out).
    star = (mx - crop.min(axis=2)) > 50
    return star


def main():
    fails = []
    log = open(OUT + "/app.log", errors="replace").read()
    got = re.findall(r"galaxy regen gen (\d+) stars (-?\d+) h15 ([0-9a-f]{16})",
                     log)
    want_counts = ["75", "100", "15", "25", "50", "75"]
    if [g for _, g, _ in got] != want_counts:
        fails.append(f"regen counts {[g for _, g, _ in got]} != {want_counts}")
    if [g for g, _, _ in got] != [str(i) for i in range(1, 7)]:
        fails.append(f"regen gens {[g for g, _, _ in got]} != 1..6")
    # SET IDENTITY: each regen draws a new stream (seed rides gen), so ALL
    # SIX h15 differ — crucially gen1 vs gen6, the same rung (75) visited
    # twice: a frozen seed rebuilds the IDENTICAL galaxy there.
    h15s = [h for _, _, h in got]
    if len(set(h15s)) != len(h15s):
        fails.append(f"h15 set-identity: repeated value in {h15s} — the "
                     "regen seed is not drawing a new stream per click")
    cosmos_n = re.findall(r"cosmos n (\d+)", log)
    if cosmos_n != ["50", "75", "100", "15", "25", "50", "75"]:
        fails.append(f"cosmos-n sequence {cosmos_n} != "
                     "[50,75,100,15,25,50,75]")

    rungs = [f"rung{k}" for k in range(7)]
    stars = {r: band(f"{OUT}/{r}.png") for r in rungs}
    mass = {r: int(stars[r].sum()) for r in rungs}
    print("star mass:", mass)
    if not (mass["rung2"] > mass["rung3"] and mass["rung1"] > mass["rung0"]):
        fails.append(f"mass not monotone-consistent with rung: {mass}")

    if fails:
        print("WITNESS RED:")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("WITNESS GREEN: regen lines exact, cosmos-n tracks the wheel, "
          "h15 new set every click, mass tracks N")


if __name__ == "__main__":
    main()
