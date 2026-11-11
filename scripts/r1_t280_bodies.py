#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t280 keeper: re-derive the SA_ ability case-body disassembly listing from
work/ascend_restored.bin and print it (the listing banked at
work/t280_bodies.txt, quoted by docs/re/aicode.md t280 amendment E1-E3).

Laws this leans on (all banked):
  - Jump table for FUN_00043b50 lives at restored FILE 0x43b10 (the obj0
    code segment maps file == image address; the `jmp cs:[eax*4+0x2ef60]`
    operand 0x2ef60 is a data-object address, +0x14bb0 = 0x43b10; t96/t99,
    scripts/r1_t99_maint_census.py pins both the raw pool garbage and this
    table). Case index al == ability number - 5.
  - In the RESTORED image, code file offset == decoded address (this tool
    disassembles at file offsets directly, matching Ghidra base-0).

Usage: r1_t280_bodies.py [start_addr ...]   (default: all documented bodies)
Needs capstone; on this box only /home/hrethric/tools/revenv/bin/python has
it:  /home/hrethric/tools/revenv/bin/python scripts/r1_t280_bodies.py
"""
import struct
import sys

try:
    from capstone import Cs, CS_ARCH_X86, CS_MODE_32
except ImportError:
    sys.exit("capstone missing — run with /home/hrethric/tools/revenv/bin/python")

IMG = "work/ascend_restored.bin"
TABLE_FILE = 0x43B10
BODIES = [  # (label, lo, hi)  hi = next body start / T1 exit region
    ("5 SA_HealShips", 0x43BAF, 0x43BF0),
    ("6 SA_ForcePeace", 0x43BF0, 0x43C3F),
    ("7 SA_DoublePower", 0x43C3F, 0x43C79),
    ("8 SA_RepelAlienShips", 0x43C79, 0x43D33),
    ("9 SA_SapAlienPower", 0x43D33, 0x43DE4),
    ("10 SA_Cornucopia", 0x43DE4, 0x43E98),
    ("11 SA_BumpShipsInLanes", 0x43E98, 0x43EEC),
    ("12 SA_StealTech", 0x43EEC, 0x43FBA),
    ("13 SA_ShieldPlanets", 0x43FBA, 0x4400A),
    ("14 SA_MoreMaxPop", 0x4402A, 0x4405F),
    ("16 SA_BlockStarLanes", 0x4405F, 0x440B5),
    ("17 SA_Hatred", 0x440B5, 0x4414E),
    ("19 SA_FreeResearch", 0x4414E, 0x4418E),
    ("20 SA_IndustryBoost", 0x4418E, 0x441C1),
]

d = open(IMG, "rb").read()

# Self-check 1: the jump table must match the t280-measured entries exactly.
entries = list(struct.unpack_from("<16I", d, TABLE_FILE))
expected = [0x43BAF, 0x43BF0, 0x43C3F, 0x43C79, 0x43D33, 0x43DE4, 0x43E98,
            0x43EEC, 0x43FBA, 0x4402A, 0x4400A, 0x4405F, 0x440B5, 0x4400A,
            0x4414E, 0x4418E]
if entries != expected:
    print("FAIL: table changed:", [hex(v) for v in entries])
    sys.exit(1)
print("OK: jump table 16/16 == t280 measurement (case al=9 -> 0x4402a)")

# Self-check 2: body 14 opens with `mov edx, 0x2b057` (BA 57 B0 02 00).
if d[0x4402A:0x4402F] != bytes.fromhex("ba57b00200"):
    print("FAIL: body 14 head bytes drifted:", d[0x4402A:0x4402F].hex())
    sys.exit(1)
print("OK: body 14 head == mov edx,0x2b057")

md = Cs(CS_ARCH_X86, CS_MODE_32)
only = {int(a, 16) for a in sys.argv[1:]}
for label, lo, hi in BODIES:
    if only and lo not in only:
        continue
    print(f"=== {label}  {lo:#x}..{hi:#x}")
    for i in md.disasm(d[lo:hi], lo):
        print(f"  {i.address:05x}  {i.mnemonic:<9} {i.op_str}")
