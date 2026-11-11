#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r1_t78_shell.py RUN... — OQ-012(a) extension: measure star position
law at NON-default density (T=15/25/100 measured by r1_t78_read).

Reuse of r1_star_table laws: star records stride 96, name-anchored;
position f32[3] at name-0x14. For each run: locate the name chain, then
per slot k report radius sqrt(x^2+y^2) (galactic-centred; shells are the
law). Prints the distinct radii per run in slot order.
"""
import os, sys, re, struct, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAY = open(os.path.join(ROOT, "work", "ascend_payload.bin"), "rb").read()
ANCH = build_anchors(PAY)
SNAME_RE = rb"[A-Z][a-z]{2,15}\x00"
HINT = 0x255be1


def analyze(run):
    sd = os.path.join(run, "save")
    files = [f for f in sorted(os.listdir(sd)) if f.endswith(".sav")]
    for f in files:
        try:
            mem = zipfile.ZipFile(os.path.join(sd, f)).read("Memory")
        except Exception:
            continue
        v, _ = find_base(mem, ANCH)
        if not v or v.most_common(1)[0][1] < 5:
            continue
        H = v.most_common(1)[0][0] - 0x1BF450
        best = []
        for delta in range(0, 0x21):
            for sign in (-1, 1):
                cand = HINT + sign * delta
                names = []
                k = 0
                while k < 200:
                    p = cand + k * 96 + H
                    m = re.match(SNAME_RE, mem[p:p + 18])
                    if not m:
                        break
                    x, y = struct.unpack("<ff", mem[p - 0x14:p - 0x14 + 8])
                    names.append((m.group()[:-1].decode(), (x * x + y * y) ** 0.5))
                    k += 1
                if len(names) > len(best):
                    best = names
        if len(best) < 3:
            continue
        radii = [round(r, 1) for _, r in best]
        print(f"{run} {f}: T={len(best)} radii={radii}")
        return True
    return False


ok = 0
for run in sys.argv[1:]:
    try:
        if analyze(run):
            ok += 1
        else:
            print(f"{run}: no anchored slot")
    except Exception as e:
        print(f"{run}: ERROR {e}")
sys.exit(0 if ok else 1)
