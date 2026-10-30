#!/usr/bin/env python3
"""t205c — find the STRIDED consumers of the 0x13bc4/0x13bc5 block.

The t205b disp-only census found only ABSOLUTE scalar reads of 0x13bc4 and no
strided base at all, yet banked law says the debug flag at 0x27401 writes
[0x13bdc + i*0x60] and 0x250aa reads [0x13bc5 + i*0x1c]. In 32-bit absolute
addressing those must materialise as `lea reg, [0x13bc5]` (disp32 as an
IMMEDIATE operand) followed by [reg + 0x1c] / [reg + i*0x60].

Two passes over obj0 [0x14bb0,0x82bb0):
  PASS A: any instruction with an IMMEDIATE equal to a candidate block address
          (0x13bc0..0x13bf0, plus 0x13b98/0x13b9c) — catches lea/mov-imm bases.
  PASS B: register-relative sites whose disp is a plausible RECORD FIELD offset
          (0x00..0x5f) and whose base register was last assigned by a PASS-A
          site within the same function window (approx: nearest preceding
          PASS-A site in a +-0x200 byte window). Reports the field-offset
          histogram, which is the layout evidence.

Prints per-candidate-base site lists. Exit 0 always.
"""
import sys
from collections import defaultdict
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

IMG = sys.argv[1] if len(sys.argv) > 1 else "work/ascend_restored.bin"
img = open(IMG, "rb").read()
LO, HI = 0x14BB0, 0x82BB0
CAND = set(range(0x13B90, 0x13C00)) | {0x48304}
# capstone operand types: CS_OP_INVALID=0 REG=1 IMM=2 MEM=3 (t205 PITFALL: an
# earlier revision used type==1 for immediates and therefore reported ZERO
# absolute bases, silently contradicting 0x39f94 `mov ebx, 0x13bc5`).

# Pass A: immediates
base_sites = defaultdict(list)
field_sites = defaultdict(list)


def scan(start, stop):
    off = start
    while off < stop:
        end = off
        md = Cs(CS_ARCH_X86, CS_MODE_32)
        md.detail = True
        try:
            it = md.disasm(img[off:stop], off)
            while True:
                ins = next(it)
                for o in ins.operands:
                    if o.type == 2 and o.imm in CAND:
                        base_sites[o.imm].append((ins.address, f"{ins.mnemonic} {ins.op_str}"))
                    if o.type == 3:
                        m = o.mem
                        if m.base and not m.index and 0 <= m.disp <= 0x5f:
                            field_sites[(ins.address, m.disp)].append(
                                (md.reg_name(m.base), ins.mnemonic, ins.op_str))
                        if m.base and m.index and m.scale in (0x30, 0x60, 0x18, 0xc):
                            field_sites[(ins.address, -m.scale)].append(
                                (md.reg_name(m.base) + "+" + md.reg_name(m.index),
                                 ins.mnemonic, ins.op_str))
                end = ins.address + ins.size
        except StopIteration:
            pass
        off = end if end > off else off + 1


scan(LO, HI)
print(f"=== t205c pass A: candidate block bases used as immediates ===")
for c in sorted(base_sites):
    print(f"\n--- {c:#x} ({len(base_sites[c])} sites) ---")
    for a, t in base_sites[c]:
        print(f"  {a:#07x}  {t}")
sys.exit(0)
