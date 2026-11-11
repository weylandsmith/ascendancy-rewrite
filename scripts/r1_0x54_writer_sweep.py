#!/usr/bin/env python3
"""r1_0x54_writer_sweep.py — t45 exhaustive census of every encoding that
# SPDX-License-Identifier: GPL-3.0-or-later

touches planet-record byte +0x54 (selected-ability/queue byte; the recalc
governor branch switch operand, income-law.md S14).

Scans the RESTORED IMAGE (work/ascend_restored.bin; VA == file offset) for:
  88   MOV r/m8, r8        WRITE      |  8a  MOV r8, r/m8        READ
  89   MOV r/m32, r32      WRITE*     |  8b  MOV r32, r/m32      READ
  c6/0 MOV r/m8, imm8      WRITE      |  c7/0 MOV r/m32, imm32   WRITE*
  86/87 XCHG r/m8, r8      WRITE      |  8f /0 POP r/m8          WRITE
  80 /reg group            write unless /7 (cmp)
(* disp8 or disp32 == 0x54 covers the byte). mod==3 and SIB encodings are
counted separately; none were found for 0x54. Exit 0 always.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "work", "ascend_restored.bin")
GRP = {0: "add", 1: "or", 4: "and", 6: "xor", 7: "cmp"}


def main():
    data = open(IMG, "rb").read()
    n = len(data)
    ops = (0x80, 0x86, 0x87, 0x88, 0x89, 0x8a, 0x8b, 0x8f, 0xc6, 0xc7)
    w, r_, sib = [], [], 0
    for off in range(n - 8):
        op = data[off]
        if op not in ops:
            continue
        modrm = data[off + 1]
        mod, reg, rm = modrm >> 6, (modrm >> 3) & 7, modrm & 7
        if rm == 4:
            # SIB: disp8 is at off+3 for mod==1
            if mod == 1 and data[off + 3] == 0x54:
                sib += 1
            continue
        if mod == 3:
            continue
        disp = data[off + 2] if mod == 1 else int.from_bytes(
            data[off + 2:off + 6], "little")
        if disp != 0x54:
            continue
        if op in (0xc6, 0xc7) and reg != 0:
            continue
        if op == 0x80 and reg not in GRP:
            continue
        kind = "READ" if op in (0x8a, 0x8b) else (
            GRP[reg] if op == 0x80 else
            ("imm" if op in (0xc6, 0xc7) else "write"))
        if op == 0x80 and reg == 7:
            kind = "cmp"
        (r_ if kind in ("READ", "cmp") else w).append(
            (off, kind, data[off:off + 8].hex()))
    print(f"image {n:#x}; SIB-form hits: {sib}")
    print(f"READ/cmp [X+0x54]: {len(r_)}")
    for off, kind, h in r_:
        print(f"  {off:#07x} {kind:5s} {h}")
    print(f"WRITE [X+0x54]: {len(w)}")
    for off, kind, h in w:
        print(f"  {off:#07x} {kind:5s} {h}")
    return 0


sys.exit(main())
