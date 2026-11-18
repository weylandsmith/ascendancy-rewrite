#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t425b S-f — RACE-RECORD COLOUR BYTE CENSUS (S-f: filter slot -> owner).

Static premise (disassembled this session from work/ascend_restored.bin,
scripts/t399_disasm.py):

  0x29967  mov  dl, [esp+0x54]          ; running bit 1<<i (race index i)
  0x29976  mov  cl, [eax+0xd8]          ; COSMOSWnd race-visible mask
  0x2997c  test edx, ecx ; je skip      ; FILTER: skip race i when bit clear
  0x29980  mov  al, [ebp+0x12e18]       ; RACE RECORD byte +2  (row base
                                        ;  = 0x12e16 + 0x1ee*i, ebp walks
                                        ;  0..0xd82 step 0x1ee @0x2994d)
  0x29986  shl  al, 2
  0x2998b  add  al, 0x13                ; idx = 0x13 + 4*byte(+2)
  0x29993  sub  edx, 3                  ; idx -= 3  (then + base)
  => the vendor's star-paint COLOUR INDEX comes from race-record byte +2,
     NOT from the slot index. If byte +2 were the race index the ramp would
     be 0x10,0x14,0x18...; distinctness of the seven bytes is what decides
     whether the filter is a PERMUTATION of the display colours.

Reads the stride-0x1ee race table at runtime 0x12e16 out of dosbox-x autosave
slots via the POINTER LAW (docs/re/r1-savestate.md OQ-011 CLOSED):
runtime X -> member index B + 0x82bb0 + X, where B is found by
scripts/r1_sav_scan.py's anchor vote (imported, not re-implemented).

Usage: python3 scripts/t425b_race_colour.py [run-dir ...]
(default run dir: work/r1/playcap)
Exit 0 = census produced for >=1 slot; 1 = nothing decoded; 2 = harness.
"""
import os
import struct
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from r1_sav_scan import build_anchors, find_base  # noqa: E402

NEEDLE = os.path.join(ROOT, "work", "ascend_payload.bin")
STRIDE = 0x1EE
RACE_BASE = 0x12E16          # &DAT_00012e16 (diplomacy.md S10, aicode.md 8.2)
MEMBER_OF_CODE = 0x82BB0     # payload file offset -> member (OQ-011)


def rows_from_slot(mem, pay):
    anch = build_anchors(pay)
    votes, _ = find_base(mem, anch)
    if not votes or votes.most_common(1)[0][1] < 5:
        return None, None
    B = votes.most_common(1)[0][0]
    base_member = B + MEMBER_OF_CODE + RACE_BASE
    out = []
    for i in range(7):
        off = base_member + STRIDE * i
        rec = mem[off:off + 0x40]
        if len(rec) < 0x40:
            return B, None
        out.append((i, rec[0], rec[1], rec[2], rec[3], rec[4]))
    return B, out


def main():
    if not os.path.exists(NEEDLE):
        print(f"harness: needle missing {NEEDLE}")
        return 2
    pay = open(NEEDLE, "rb").read()
    dirs = sys.argv[1:] or [os.path.join(ROOT, "work/r1/playcap")]
    seen = 0
    per_slot = {}
    for d in dirs:
        savedir = os.path.join(d, "save")
        if not os.path.isdir(savedir):
            continue
        for f in sorted(x for x in os.listdir(savedir) if x.endswith(".sav")):
            try:
                mem = zipfile.ZipFile(os.path.join(savedir, f)).read("Memory")
            except Exception:
                continue
            B, rows = rows_from_slot(mem, pay)
            if not rows:
                continue
            seen += 1
            b2 = [r[2] for r in rows]
            per_slot[f] = b2
            print(f"{f}: B={B:#x} byte+2={b2} distinct={len(set(b2))} "
                  f"faceBase={[0x10 + 4 * v for v in b2]}")
    if not seen:
        print("negative: no slot decoded (no live payload copy in these saves)")
        return 1
    # cross-slot stability
    uniq = {tuple(v) for v in per_slot.values()}
    print(f"SLOTS {seen} — distinct byte+2 vectors across slots: {len(uniq)}")
    for v in uniq:
        print("  ", list(v))
    print("LAW CHECK: byte+2 == race index i for all rows ->",
          all(all(b == i for i, b in enumerate(v)) for v in per_slot.values()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
