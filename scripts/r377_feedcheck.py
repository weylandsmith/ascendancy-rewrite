#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""t377 diagnostic: does the live feed carry ANY ship-record movement in the
post-15:33 span? Compares first vs last deduped frame per slot."""
import importlib.util
import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "r370", os.path.join(here, "r370_slot_events.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

frames = m.stream(1794429182264000000, -1, seek=900_000_000)
print("frames", len(frames), frames[0][0], "->", frames[-1][0],
      "turns", frames[0][1], "->", frames[-1][1])
f0 = {int(k): w for k, w in frames[0][2].items() if len(w) == 177}
fl = {int(k): w for k, w in frames[-1][2].items() if len(w) == 177}
ndiff = 0
for s in sorted(set(f0).intersection(fl)):
    if f0[s] != fl[s]:
        ndiff += 1
        words = [hex(i * 2) for i, (a, b) in enumerate(zip(f0[s], fl[s])) if a != b]
        print("slot", s, "changed bytes:", words[:16])
print("slots differing first->last:", ndiff, "of", len(set(f0).intersection(fl)))
