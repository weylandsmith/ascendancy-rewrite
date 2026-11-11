#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t269b — locate ANOMALY rows in the timeline: T != 50 or rank == 0
(the t269 pass found T in {50:71023, 25:12, 0:2, 100:1} and rank=0 x2).
Streams (OOM law), prints header fields only (ship_raw/relation never read).
usage: r269_anom.py"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSONL = os.path.join(ROOT, "work/r1/playcap", "live-timeline.jsonl")


def fnum(line, key):
    pat = '"%s": ' % key
    i = line.find(pat)
    if i < 0:
        return None
    i += len(pat)
    j = i
    while j < len(line) and line[j].isdigit():
        j += 1
    return int(line[i:j]) if j > i else None


def fstr(line, key):
    pat = '"%s": "' % key
    i = line.find(pat)
    if i < 0:
        return None
    i += len(pat)
    j = line.find('"', i)
    return line[i:j]


n = 0
n_anom = 0
with open(JSONL, "r", errors="replace") as f:
    for line in f:
        n += 1
        T = fnum(line, "T")
        rk = fnum(line, "rank")
        if T == 50 and rk != 0:
            continue
        n_anom += 1
        print("line=%d file=%s mtime_ns=%s wall=%s turn=%s T=%s V=%s sel=%s "
              "rank=%s any=%s full=%s pm=%s in_game=%s" % (
                  n, fstr(line, "file"), fnum(line, "file_mtime_ns"),
                  fstr(line, "wall"), fnum(line, "turn"), T,
                  fnum(line, "score_stars"), fnum(line, "selector_byte"),
                  rk, fnum(line, "systems_any"), fnum(line, "systems_full"),
                  fnum(line, "planets_mine"), '"in_game": true' in line))
print("lines=%d anomalies=%d" % (n, n_anom))
