#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t214: inflation-vs-time profile of the shared capture timeline.

Why: four watcher instances write the same dir (docs/re/_wip_t214.md S2). A
tail window showed 3.77x row inflation with max 4 reps. Two things depend on
HOW that factor varied over the capture's life:

  1. Are prior RAW-COUNT claims (t187 "state-4 x1115", t189 "68 sustained raw
     rows") inflated 2x or 4x?  The orphan uptimes imply writers ACCRETED
     (2 on 2026-10-26/28, 3 then 4 on 2026-10-29), so the answer is time-local.
  2. Ordering safety. r1_stream.build_index sorts by (file_mtime_ns, file), so
    duplicate emissions of the same key are adjacent and first-wins is
    deterministic. If the factor CHANGES mid-window, a naive sequential (unsorted)
    reader can see turn-boundary sequences interleaved out of order.

Method: one streaming pass, regex-extract (file, file_mtime_ns, wall, turn) per
line -- NO json.loads (240k lines x ~24KB; the r1_stream docstring measures a
full parse at ~60 s, a scan at ~20 s). Bucket by wall clock into 10-minute bins,
report per-bin rows, distinct keys, collapse factor. Prints a small table only.
"""
import os
import re
import collections
import sys

JSONL = "/home/hrethric/projects/ascendancy/work/r1/playcap/live-timeline.jsonl"

RE_FILE = re.compile(r'"file":\s*"([^"]+)"')
RE_MT = re.compile(r'"file_mtime_ns":\s*(\d+)')
RE_WALL = re.compile(r'"wall":\s*"?([0-9:]{5,12})"?')
RE_TURN = re.compile(r'"turn":\s*(\d+)')

CHUNK = 4000  # lines per append-order chunk (~1.7% of the 240k-row file)


def main():
    bin_rows = collections.Counter()
    bin_keys = collections.defaultdict(set)
    bin_dates = collections.defaultdict(set)
    reps_hist = collections.Counter()
    per_key_reps = {}
    total = 0
    bad = 0
    n_keys_total = set()
    with open(JSONL, "r", errors="replace") as f:
        for line in f:
            total += 1
            m_t = RE_TURN.search(line)
            if not m_t:
                bad += 1
                continue
            mf = RE_FILE.search(line)
            mm = RE_MT.search(line)
            mw = RE_WALL.search(line)
            if not (mf and mm and mw):
                bad += 1
                continue
            key = (mf.group(1), mm.group(1))
            per_key_reps[key] = per_key_reps.get(key, 0) + 1
            n_keys_total.add(key)
            # TIME AXIS: `wall` is clock time-of-day with NO date ("13:22:11"),
            # so it cannot order a capture that spans days. (A first draft sliced
            # w[-5:] and silently binned MM:SS — the bins looked plausible and
            # were wrong: binning code needs a unit assertion, not a eyeball.)
            # Append order IS monotone in time-of-append, so chunk by line index.
            b = (total - 1) // CHUNK
            bin_rows[b] += 1
            bin_keys[b].add(key)
            if " " in mw.group(1):
                bin_dates[b].add(mw.group(1).split(" ")[0])
    print(f"lines={total} bad={bad} distinct_keys_total={len(n_keys_total)} "
          f"overall_collapse={total / max(1, len(n_keys_total)):.2f}x")
    reps = collections.Counter(per_key_reps.values())
    print("per-key rep histogram (reps: n_keys):",
          {k: reps[k] for k in sorted(reps)})
    print(f"\ncollapse factor per {CHUNK}-row append-order chunk:")
    prev = None
    for b in sorted(bin_rows):
        rows = bin_rows[b]
        keys = len(bin_keys[b])
        cf = rows / max(1, keys)
        flag = ""
        if prev is not None and abs(cf - prev) > 0.6:
            flag = "  <== factor step"
        print(f"  chunk {b:3d} (lines {b*CHUNK+1:6d}..{b*CHUNK+rows:6d}) "
              f"rows={rows:5d} keys={keys:5d} collapse={cf:5.2f}x{flag}")
        prev = cf
    print("\nwall fields carrying a DATE:",
          sorted(set().union(*bin_dates.values()) if bin_dates else [])[:10]
          or "none — wall is time-of-day only, no date")


if __name__ == "__main__":
    sys.exit(main())
