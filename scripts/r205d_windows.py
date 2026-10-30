#!/usr/bin/env python3
"""t205d — verbatim disasm of the windows that decide EBX's addressing mode.

The t205b/t205c censuses showed the image uses `[reg + ABS]` forms
(e.g. 0x2742c `mov ch,[eax+0x13bdc]`) and ZERO absolute-immediate bases in the
0x13b90..0x13bf0 block. So whether "EBX = 0x13bc5 + 0x60*idx" is an absolute
address or a base-register-relative address must be read from the encoding.

Prints capstone disasm (with byte widths) of the given address windows.
Usage: r205d_windows.py [IMG] start:end [start:end ...]
"""
import sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

IMG = sys.argv[1] if len(sys.argv) > 1 else "work/ascend_restored.bin"
img = open(IMG, "rb").read()
for spec in sys.argv[2:]:
    a, b = (int(x, 16) for x in spec.split(":"))
    print(f"\n=== {a:#x}..{b:#x} ===")
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    md.detail = True
    off = a
    while off < b:
        got = False
        for ins in md.disasm(img[off:b], off):
            print(f"  {ins.address:#07x} {img[ins.address:ins.address+ins.size].hex():<18} {ins.mnemonic} {ins.op_str}")
            off = ins.address + ins.size
            got = True
        if not got:
            print(f"  {off:#07x} {img[off]:02x}                     (undecodable)")
            off += 1
sys.exit(0)
