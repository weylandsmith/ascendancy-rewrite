#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t205b — static operand census for the disputed static addresses
0x13b98 (race count word), 0x13bc4 (disputed byte), 0x13bc5 (disputed table).

Scans obj0 code [0x14bb0,0x82bb0) of work/ascend_restored.bin with capstone
(r201 resume-past-data-gaps pattern) and reports EVERY instruction whose
memory operand references one of those addresses, either as an absolute
disp32 (no base reg -> Ghidra DAT_/LAB_ symbol) or as base+disp / base+index
where the disp alone equals the target.

Prints: address, W/R, mnemonic+ops, plus which operand matched and whether an
indexed (scaled) access is involved. Exit 0 always (findings printed).
"""
import sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

IMG = sys.argv[1] if len(sys.argv) > 1 else "work/ascend_restored.bin"
img = open(IMG, "rb").read()
LO, HI = 0x14BB0, 0x82BB0
TARGETS = {0x13B98: "race_cnt_u16", 0x13B9C: "after_cnt",
           0x13BC4: "disputed_byte", 0x13BC5: "table_base",
           0x13Bc8: "word_after", 0x13BD0: "f_a", 0x13BD4: "f_b",
           0x13BD8: "f_c", 0x13BDC: "reveal_bit_target"}
WRITE_MN = {"mov", "movzx", "movsx", "inc", "dec", "neg", "xchg", "or", "and",
            "xor", "add", "sub", "sbb", "shl", "shr", "sar", "stosb", "stosd",
            "rep stosb", "rep stosd", "movabs", "lea"}

rows = []
off = LO
while off < HI:
    end = off
    it = md_iter = None
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    md.detail = True
    try:
        it = md.disasm(img[off:HI], off)
        while True:
            ins = next(it)
            for o in ins.operands:
                if o.type != 3:
                    continue
                m = o.mem
                hit = None
                if m.disp in TARGETS and not m.base:
                    hit = f"ABS disp={m.disp:#x} {TARGETS[m.disp]}"
                elif m.disp in TARGETS and m.base and not m.index:
                    hit = f"{md.reg_name(m.base)}+disp{m.disp:#x} {TARGETS[m.disp]}"
                elif m.index and m.scale and m.disp in TARGETS:
                    hit = (f"{md.reg_name(m.base) if m.base else ''}+"
                           f"{md.reg_name(m.index)}*{m.scale}+{m.disp:#x} {TARGETS[m.disp]}")
                if hit:
                    rows.append((ins.address,
                                 "W" if (ins.mnemonic in WRITE_MN and o is ins.operands[0]) else "R",
                                 hit, f"{ins.mnemonic} {ins.op_str}"))
                    break
            end = ins.address + ins.size
    except StopIteration:
        pass
    off = end if end > off else off + 1

print(f"=== t205b static census of {', '.join(hex(t) for t in sorted(TARGETS))} "
      f"in [{LO:#x},{HI:#x}) — {len(rows)} sites ===")
cur = None
for a, wr, hit, txt in rows:
    if hit != cur:
        print(f"\n--- operand {hit} ---")
        cur = hit
    print(f"  {a:#07x} {wr}  {txt}")
sys.exit(0)
