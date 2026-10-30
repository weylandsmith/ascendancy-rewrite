#!/usr/bin/env python3
"""t207 C-W census — operand-level survey of the diplo-table tail cluster.

Enumerates EVERY disassembled instruction in work/ascend_restored.bin whose
memory operand's disp32 lands in [0x12fa0, 0x13010] (the packed tail of the
race-diplo table cluster: 0x12fb3 species/ability row base, 0x12fc8 third-
party opinion matrix per t180/debugflags, 0x12fd6 relation-STATE matrix base
per t180, 0x12fdf = diplo-row0+0x1c9 = DECLARE_WAR threshold).

For each disp prints the sites with index register + scale, so the stride
questions in _wip_t207.md C-W can be answered from encodings:
  - witness gate 0x3a20b reads byte [eax*2 + 0x12fb3] with eax = 0x1ee*k
    -> effective stride 0x3dc. Are there OTHER sites on 0x12fb3, and at
    which scale do they run (0x1ee direct vs 2*0x1ee)?
  - [eax*2 + 0x12fc8]: scale-2 word matrix, row stride 0x3dc too.

Run: ~/tools/revenv/bin/python scripts/r207_disp_cluster.py [IMG]
Exit 0 always (survey tool)."""
import sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

IMG = sys.argv[1] if len(sys.argv) > 1 else "work/ascend_restored.bin"
LO, HI = 0x12FA0, 0x13010
img = open(IMG, "rb").read()
md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = True
hits = {}
# PITFALL (t205 banked): capstone's disasm() STOPS at the first undecodable
# byte (393 insns on this image). Seed-and-restart past dead bytes.
off = 0
while off < len(img):
    got = False
    for ins in md.disasm(img[off:], off):
        got = True
        off = ins.address + ins.size
        for op in ins.operands:
            if op.type == 3:  # CS_OP_MEM
                d = op.mem.disp
                if LO <= d <= HI:
                    hits.setdefault(d, []).append(
                        (ins.address, ins.mnemonic, ins.op_str,
                         op.mem.index, op.mem.scale, op.mem.base))
    if not got:
        off += 1
print(f"image={IMG} window=[{LO:#x},{HI:#x})  distinct disps={len(hits)}")
for d in sorted(hits):
    print(f"\n--- disp {d:#x}  (diplo-row0 {d-0x12e16:+d}, 12fb3 {d-0x12fb3:+d}, "
          f"12fc8 {d-0x12fc8:+d}, 12fd6 {d-0x12fd6:+d})  n={len(hits[d])}")
    for a, m, o, idx, scale, base in hits[d]:
        ir = md.reg_name(idx) if idx else "-"
        print(f"   {a:#07x} {m} {o}   [base={md.reg_name(base) if base else '-'}, index={ir}, scale={scale}]")
