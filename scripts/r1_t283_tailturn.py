#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t283 pre-flight: cheap last-turn probe of a live-timeline.jsonl.

Prints: rows scanned from the tail window, first/last (turn, ts) pairs, and
the max turn seen. Deliberately never reads the whole file (stream law).
"""
import json
import os
import subprocess
import sys

RUN = sys.argv[1] if len(sys.argv) > 1 else \
    "/home/hrethric/projects/ascendancy/work/r1/playcap"
PATH = RUN if RUN.endswith(".jsonl") else os.path.join(RUN, "live-timeline.jsonl")
WINDOW = int(sys.argv[2]) if len(sys.argv) > 2 else 2_000_000

size = os.path.getsize(PATH)
data = subprocess.run(["tail", "-c", str(WINDOW), PATH],
                      stdout=subprocess.PIPE).stdout.split(b"\n")
rows = []
for l in data:
    l = l.strip()
    if not l:
        continue
    try:
        j = json.loads(l)
    except Exception:
        continue
    rows.append((j.get("turn"), j.get("ts") or j.get("timestamp")))
print(f"file {PATH} size {size}")
print(f"tail-window rows parsed {len(rows)}")
if rows:
    print("first", rows[0])
    print("last", rows[-1])
    print("max turn", max(t for t, _ in rows if isinstance(t, int)))
