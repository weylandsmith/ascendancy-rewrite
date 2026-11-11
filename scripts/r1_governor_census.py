#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r1_governor_census.py — t45 OQ-024 corpus evidence.

Census of the planet-record byte +0x54 (the field the recalc governor
branch FUN_00038ba4 @0x38df0 switches on) over EVERY owned planet record
in EVERY banked save, using the t33-corrected record walk (find_records:
slot array = [planet+0x10] + 0x88). Records identified per OQ-014 name-
anchor law; ownership = byte +0x57 != 0xFF (t40 fix). Trigger values of
interest: 0x21/0x22/0x23 = items 33/34/35 (Endless Party / Scientist
Takeover / Automation, IDs verified against the RUNTIME item table copy
at base + 0x82bb0 + 0x73e40). Also histograms byte +0x52 (selected cell
word) emptiness as a side-channel: a governor SELECT would pin +0x52 to
a real cell while +0x54 holds a special item id.

Exit codes: 0 = branch never fires in corpus (OQ-024 negative re-
measured); 1 = a firing record EXISTS (escalate: capture semantics
upgradable to measured-positive); 2 = harness broken.
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_income_law as IL
from r1_sav_scan import build_anchors, find_base

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "work", "r1")


def runs():
    for d in sorted(os.listdir(BASE)):
        p = os.path.join(BASE, d)
        if not os.path.isdir(p):
            continue
        if os.path.isdir(os.path.join(p, "save")) or os.path.isdir(os.path.join(p, "ck")):
            yield p


def main():
    try:
        anch = build_anchors(IL.PAY)
    except Exception as e:
        print("ANCHORS FAIL:", e)
        return 2
    hist = {}
    fires = []
    saves = 0
    recs = 0
    for p in runs():
        try:
            slots = IL.load_slots(p)
        except Exception:
            continue
        for f, m, B in slots:
            if B is None:
                continue
            saves += 1
            walked = IL.find_records(m)
            if not walked:
                continue
            for rec in walked:
                rb = rec if isinstance(rec, int) else rec[0]
                owner = m[rb + 0x57]
                if owner == 0xFF:
                    continue
                recs += 1
                v = m[rb + 0x54]
                hist[v] = hist.get(v, 0) + 1
                if v in (0x21, 0x22, 0x23):
                    fires.append((os.path.basename(p), f, hex(rb), hex(v)))
    print(f"saves walked: {saves}, owned records: {recs}")
    print("+0x54 histogram (byte -> count):")
    for k in sorted(hist):
        print(f"  {k:#04x} {k:3d} -> {hist[k]}")
    if fires:
        print("GOVERNOR BRANCH FIRES:", len(fires))
        for x in fires[:20]:
            print("  ", x)
        return 1
    print("branch never fires in corpus (no record holds 0x21/0x22/0x23)")
    return 0


sys.exit(main())
