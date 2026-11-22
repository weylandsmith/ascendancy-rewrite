#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""tNGB_species_witness — B2 species-wheel -> player-count law witness.

Laws (docs/re/_wip_tNGB.md 'B2 SPECIES ARM FULL DECODE'):
  vendor 0x52e58..0x52ecc: word[+0xb9]++ wrap 8->3, then FUN_00022ce4
  (player count word[state+0xd88]=N, home worlds + colours re-rolled,
  star POSITIONS PRESERVED — no 0x226e4 regen).
Assertions (log-first per the B1 flicker lesson; pixels only on the
STATIC wheel-panel regions):
  1. 'ui raceconfig roster n N wheelgen G h15 H' lines: N visits
     6,7,3,4 (from default 5) with G==0 and H IDENTICAL on every click
     (positions preserved; a regen-mutant changes H -> RED).
  2. 'click PLAYERS_MORE msg 503 -> Six/Seven/Three/Four' words in order.
  3. Species wheel panel rect CHANGES between consecutive shots (art law
     child+0x72 = count+2, k7->k8->k9->k5) — different frames, different px.
  4. Density wheel panel rect is INVARIANT across species clicks (the arm
     does not regen; >99% of pixels identical except the spin-animated
     cosmos is OUTSIDE these rects).
Exit 0 GREEN / 1 RED.
"""
import re
import sys

import numpy as np
from PIL import Image

OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/tNGB_species"
EXPECT_N = [6, 7, 3, 4]
EXPECT_WORD = ["Six", "Seven", "Three", "Four"]
# panel interiors (disc rows, same crops as tNGB_b3_anchor): species x140..236,
# density x16..112, rows 408..466.
ROWS = slice(408, 467)
SPECIES_X = slice(140, 237)
DENSITY_X = slice(16, 113)


def main():
    fails = []
    log = open(OUT + "/app.log", errors="replace").read()
    roster = re.findall(
        r"ui raceconfig roster n (\d+) wheelgen (\d+) h15 ([0-9a-f]{16})", log)
    ns = [int(a) for a, _, _ in roster]
    gens = [int(b) for _, b, _ in roster]
    hs = [c for _, _, c in roster]
    if ns != EXPECT_N:
        fails.append(f"roster n sequence {ns} != {EXPECT_N}")
    if any(g != 0 for g in gens):
        fails.append(f"species click bumped wheelgen {gens} — regen mutant "
                     f"(vendor arm calls 0x22ce4, NOT 0x226e4)")
    if len(set(hs)) > 1:
        fails.append(f"h15 not constant across species clicks: {sorted(set(hs))}"
                     f" — star set changed, positions-preserved law violated")
    words = re.findall(r"click PLAYERS_MORE msg 503 -> (\w+)", log)
    if words != EXPECT_WORD:
        fails.append(f"SPECIES words {words} != {EXPECT_WORD}")
    # pixel legs
    shots = [np.asarray(Image.open(f"{OUT}/spec{k}.png").convert("RGB"))
             for k in range(5)]
    for k in range(4):
        d = np.abs(shots[k][ROWS, SPECIES_X].astype(int) -
                   shots[k + 1][ROWS, SPECIES_X].astype(int)).max(axis=2)
        changed = float((d > 12).mean())
        if changed < 0.05:
            fails.append(f"species panel ~unchanged spec{k}->spec{k+1} "
                         f"({changed:.1%}) — wheel art frame did not move")
    for k in range(4):
        d = np.abs(shots[k][ROWS, DENSITY_X].astype(int) -
                   shots[k + 1][ROWS, DENSITY_X].astype(int)).max(axis=2)
        same = float((d <= 12).mean())
        if same < 0.99:
            fails.append(f"density panel changed across species click "
                         f"spec{k}->spec{k+1} ({1 - same:.1%} px) — the "
                         f"species arm must NOT regen the galaxy")
    if fails:
        print("B2 WITNESS RED:")
        for f in fails:
            print("  -", f)
        return 1
    print(f"B2 WITNESS GREEN: roster {ns} h15 constant {hs[0]}, words "
          f"{words}, species art moved, density panel invariant")
    return 0


if __name__ == "__main__":
    sys.exit(main())
