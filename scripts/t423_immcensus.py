#!/usr/bin/env python3
"""t423: imm-operand census over the code segment (skipdata-aware).
Usage: t423_immcensus.py <lo-hex> <hi-hex> <imm1,imm2,...>
Restored-image addresses (base 0). Prints sites with imm == target."""
import sys
from capstone import *
from capstone.x86_const import X86_OP_IMM

lo, hi = int(sys.argv[1], 16), int(sys.argv[2], 16)
targets = {int(t, 16) for t in sys.argv[3].split(',')}
data = open('/home/hrethric/projects/ascendancy/work/ascend_restored.bin', 'rb').read()
md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = True
hits = []
addr = lo
while addr < hi:
    got = False
    for ins in md.disasm(data[addr:addr + 0x4000], addr):
        got = True
        for op in ins.operands:
            if op.type == X86_OP_IMM and op.imm in targets:
                hits.append((ins.address, ins.mnemonic, ins.op_str))
                break
        addr = ins.address + ins.size
    if not got:
        addr += 1
print(f"{len(hits)} hits in [{hex(lo)},{hex(hi)}) for {[hex(t) for t in sorted(targets)]}")
for a, m, o in hits:
    print(f"{a:06x}  {m} {o}")
