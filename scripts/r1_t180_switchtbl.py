#!/usr/bin/env python3
"""t180: resolve the FUN_000454a4 switch table (OQ-023 state-3 writers).

Dispatch evidence (objdump, work/ascend_restored.bin, VA == file offset):
    454dd: 80 fb 0e                cmp    bl,0xe
    454e0: 0f 87 4a 07 00 00       ja     0x45c30          ; 15-case bound
    454e6: 31 c0                   xor    eax,eax
    454e8: 88 d8                   mov    al,bl
    454ea: 8d 2c 85 00 00 00 00    lea    ebp,[eax*4]      ; EBP := bl*4
    ...
    45560: 2e ff a5 b8 08 03 00    jmp    DWORD PTR cs:[ebp+0x308b8]

EBP here is NOT a frame pointer -- 0x454ea overwrites it with the scaled
index, so the target is the CS-relative absolute slot 0x308b8 + bl*4. Per
the banked cs-relative law (docs/REFUTED-ROUTES.md R13: "cs-relative
immediates need the code-object intra base (+0x14bb0)"; worked example there:
cs:0x8c90 == file 0x1d840), the table is at image 0x308b8 + 0x14bb0 =
0x45468 -- i.e. 60 bytes = 15 u32 entries sitting directly in front of the
case bodies at 0x454a4. That adjacency is the self-check: an entry value
that lands inside [0x454a4, 0x45c30) confirms the base.

Usage: r1_t180_switchtbl.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "work", "ascend_restored.bin")
CS_BASE = 0x14BB0          # code-object-0 intra base (R13)
CS_SLOT = 0x308B8          # jmp displacement
CASE_LO, CASE_HI = 0x454A4, 0x45C30
NCASE = 15


def main():
    data = open(IMG, "rb").read()
    tbl = CS_BASE + CS_SLOT
    print(f"cs:{CS_SLOT:#x} -> image {tbl:#x}  (bodies {CASE_LO:#x}..{CASE_HI:#x})")
    inrange = 0
    for i in range(NCASE):
        v = int.from_bytes(data[tbl + i * 4: tbl + i * 4 + 4], "little")
        ok = CASE_LO <= v < CASE_HI
        inrange += ok
        print(f"  bl={i:2d} {i:#04x} -> {v:#x}  {'IN-BODY' if ok else 'out'}")
    print(f"in-range {inrange}/{NCASE}")


if __name__ == "__main__":
    main()
