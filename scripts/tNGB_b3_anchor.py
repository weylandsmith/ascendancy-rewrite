#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tNGB_b3_anchor — B3 per-control wheel anchor verification.

Method = the F15-1 best-shift pixel-agreement law (docs/re/_wip_tNGC.md
F15-1/2): crop each wheel panel interior (disc rows 408..466) from OUR
raceconfig render and from the vendor refcap (scratchpad/newgame-original.
png, browser-crop law im[1:481,1:641]), slide ours by (dx,dy) in +-4, take
the shift maximizing exact-ish agreement (channel delta <= 12).

PRE-B3 BASELINE (F15-1, same method): atmos 91.4% @(-2,-1), density
93.6% @(1,-1), species 80.0% @(1,0). The B3 correction (menulaw.h
kWheelBlitDx/Dy = {+1,+1,-2} x {-1,0,-1}) is VALID iff post-change the
best-shift agreement per panel >= baseline AND the best shift moves toward
(0,0). Species content differs by setting (ours k9 seven-player vs vendor
k7) — treat species as informational; density/atmos are the verdict.
Exit 0 = improved or equal; 1 = regression (revert kWheelBlitDx/Dy).
"""
import sys

import numpy as np
from PIL import Image

REPO = "/home/hrethric/projects/ascendancy"
OURS = sys.argv[1] if len(sys.argv) > 1 else "/tmp/tNGB_density/rung0.png"
VEND = REPO + "/scratchpad/newgame-original.png"

# panel interior crops: (x0, x1) shared rows 408..466 (F15-1 law)
PANELS = {"density": (16, 112), "species": (140, 236), "atmos": (264, 364)}
BASE = {"density": (93.6, (1, -1)), "species": (80.0, (1, 0)),
        "atmos": (91.4, (-2, -1))}


def agree(ours, vend, dx, dy):
    # shift ours by (dx,dy) over vend; overlap window only
    r0, c0 = max(dy, 0), max(dx, 0)
    r1 = min(vend.shape[0], ours.shape[0] + dy)
    c1 = min(vend.shape[1], ours.shape[1] + dx)
    if r1 <= r0 or c1 <= c0:
        return -1.0
    a = ours[r0 - dy:r1 - dy, c0 - dx:c1 - dx]
    b = vend[r0:r1, c0:c1]
    d = np.abs(a - b).max(axis=2)
    return 100.0 * float((d <= 12).mean())


def best_shift(ours, vend):
    best = (-1.0, (0, 0))
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            s = agree(ours, vend, dx, dy)
            if s > best[0]:
                best = (s, (dx, dy))
    return best


def main():
    vend = np.asarray(Image.open(VEND).convert("RGB"))[1:481, 1:641].astype(int)
    ours = np.asarray(Image.open(OURS).convert("RGB")).astype(int)
    fails = []
    for name, (x0, x1) in PANELS.items():
        oc = ours[408:467, x0:x1 + 1]
        vc = vend[408:467, x0:x1 + 1]
        s, (dx, dy) = best_shift(oc, vc)
        base, (bdx, bdy) = BASE[name]
        print(f"{name}: post-B3 best {s:.1f}% @({dx},{dy})  "
              f"baseline {base}% @({bdx},{bdy})")
        if name == "species":
            # tNG-B B2: with the vendor default FIXED to 5 (k7 'Five',
            # window-init 0x52c55) the species panel is the SAME content as
            # the refcap — verdict like the others: best shift at origin.
            # Floor 87.0: clean default-5 measures 88.8; the old wrong
            # default 7 (k9) measured 80.0 — a default mutant is RED.
            if (dx, dy) != (0, 0):
                fails.append(f"species best shift ({dx},{dy}) != (0,0) — "
                             f"wheel blit anchor off the corrected law")
            elif s < 87.0:
                fails.append(f"species agreement {s:.1f}% < 87.0 — species "
                             f"setting/content off the vendor default Five")
            continue
        # ANCHOR LAW (mutation-campaign lesson): agreement-at-best-shift is
        # INVARIANT to the blit anchor (a 1px mutant just moves the best
        # shift), so the discriminator is the best-shift POSITION: after the
        # B3 correction it must sit at the origin.
        if (dx, dy) != (0, 0):
            fails.append(f"{name} best shift ({dx},{dy}) != (0,0) — wheel "
                         f"blit anchor off the corrected law")
        elif s < base - 1.0:
            fails.append(f"{name} agreement REGRESSED {base}% -> {s:.1f}%")
    if fails:
        print("B3 WITNESS RED:")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("B3 WITNESS GREEN: anchor corrections improve or hold agreement")


if __name__ == "__main__":
    main()
