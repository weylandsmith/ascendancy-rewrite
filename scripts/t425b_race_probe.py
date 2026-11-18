#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t425b S-f probe: locate the stride-0x1ee race table in a live save and
validate the base with INDEPENDENT anchors before reading any field
(diplomacy.md S10 BASE-DRIFT lesson: an unvalidated 0x12e16 census was void).

Anchors used (all cited static sites, work/ascend_restored.bin):
  word [0x13b98]  = per-race record-count bound (read at 0x27258 `mov cx,[0x13b98]`)
  word [0x13b96]  = race count hi-word (diplomacy.md S7)
  byte [0x7458e]  = LOCAL race index (aicode.md 8.2 head: esi = 0x12e16 + [0x7458e]*0x1ee)
  i16 [+0x1b2 + 2t] per row = START_ATTITUDE 310..620 (diplomacy.md S10)

Usage: python3 scripts/t425b_race_probe.py [slot.sav ...]
"""
import os
import struct
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from r1_sav_scan import build_anchors, find_base  # noqa: E402

PAY = os.path.join(ROOT, "work", "ascend_payload.bin")
STRIDE = 0x1EE


def probe(mem, pay):
    votes, _ = find_base(mem, build_anchors(pay))
    if not votes or votes.most_common(1)[0][1] < 5:
        return None
    B = votes.most_common(1)[0][0]
    print(f"B={B:#x}")
    # candidate member offsets for runtime address X, two hypotheses:
    #   H_code: X is a code-region (obj0) address -> member = B + X
    #   H_data: X is a Ghidra/data address       -> member = B + 0x82bb0 + X
    for name, f in (("B+X", lambda x: B + x), ("B+0x82bb0+X", lambda x: B + 0x82bb0 + x)):
        try:
            cnt_hi = struct.unpack_from("<H", mem, f(0x13b96))[0]
            bound = struct.unpack_from("<H", mem, f(0x13b98))[0]
            local = mem[f(0x7458e)]
        except Exception as e:
            print(f"  {name}: read fail {e}")
            continue
        print(f"  {name}: [0x13b96]={cnt_hi} [0x13b98]={bound} [0x7458e]={local}")
        rows = []
        for i in range(7):
            base = f(0x12e16) + STRIDE * i
            rec = mem[base:base + 0x1ee]
            atts = [struct.unpack_from("<h", rec, 0x1b2 + 2 * t)[0] for t in range(7)]
            in_range = sum(1 for a in atts if 300 <= a <= 700)
            rows.append((i, rec[0], rec[1], rec[2], rec[3], in_range, atts[:4]))
        good = sum(1 for r in rows if r[5] >= 4)
        print(f"    rows (i,b0,b1,b2,b3,atts_in_310..620,first4):")
        for r in rows:
            print(f"     {r}")
        print(f"    ANCHOR PASS rows={good}/7")


def main():
    pay = open(PAY, "rb").read()
    slots = sys.argv[1:]
    if not slots:
        d = os.path.join(ROOT, "work/r1/playcap/save")
        slots = [os.path.join(d, f) for f in sorted(os.listdir(d))][-2:]
    for s in slots:
        print(f"== {os.path.basename(s)}")
        probe(zipfile.ZipFile(s).read("Memory"), pay)
    return 0


if __name__ == "__main__":
    sys.exit(main())
