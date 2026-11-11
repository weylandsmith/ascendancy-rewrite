#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t288: offline census of the game's pending-input globals across banks.

Static lead (t103 P13): WORD ds:0x484c4 = msg code, ds:0x484c6 = char/ebx,
ds:0x484ec/0x484f0 = second pair; written by the INPUT layer, read verbatim
by relay 0x54976. The ring-slot Memory member holds the full linear image
(pointer law), so these are readable from any banked slot WITHOUT a debugger.

Prints u16/u32 readings at data offsets 0x484c0..0x48508 for one slot per
named bank, plus the 16-byte hex rows, labelled by health class.

usage: r288_input_census.py BANK_DIR[:CLASS] [more...]
Exit 0 always unless a bank fails to decode.
"""
import os, struct, sys, zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_sav_scan as SS

PAYLOAD = os.path.join(ROOT, "work/ascend_payload.bin")
H = 0x88
OBJ1_OFF = 0x82bb0
OFFS = [0x484c4, 0x484c6, 0x484c8, 0x484ca, 0x484cc, 0x484ce,
        0x484ec, 0x484ee, 0x484f0, 0x484f2]


def main():
    pay = open(PAYLOAD, "rb").read()
    anch = SS.build_anchors(pay)
    rc = 0
    for arg in sys.argv[1:]:
        bank, _, cls = arg.partition(":")
        bank = os.path.join(ROOT, bank) if not bank.startswith("/") else bank
        slots = sorted([os.path.join(bank, f) for f in os.listdir(bank)
                        if f.endswith(".sav")], key=os.path.getmtime)
        if not slots:
            print(f"{arg}: NO .sav files"); rc = 1; continue
        got = False
        for sp in reversed(slots):
            try:
                mem = zipfile.ZipFile(sp).read("Memory")
            except Exception as e:
                print(f"{os.path.basename(sp)}: unreadable ({e})"); continue
            votes, _ = SS.find_base(mem, anch)
            if not votes or votes.most_common(1)[0][1] < 5:
                continue
            B = votes.most_common(1)[0][0]
            # member-index law (r1_wp_session.py:22-24,85): mem[B + OBJ1_OFF + off]
            # holds data offset off; LINEAR is that minus H.
            base = B + OBJ1_OFF
            row = []
            for off in OFFS:
                row.append(f"{off:x}={struct.unpack_from('<H', mem, base+off)[0]:#06x}")
            lo, hi = 0x484c0, 0x48510
            hexrow = mem[base+lo:base+hi]
            print(f"{arg} slot={os.path.basename(sp)} B={B:#x} "
                  f"linear(484c4)={B-H+OBJ1_OFF+0x484c4:#x}")
            print("   " + " ".join(row))
            print(f"   raw {lo:x}..{hi:x}: {hexrow.hex()}")
            got = True
            break
        if not got:
            print(f"{arg}: no slot with a confident base vote"); rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
