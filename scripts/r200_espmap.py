#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t200 — mechanical esp-offset tracker over a code span.

Prints, for every instruction, the frame-relative offset of each [esp+k]
operand, where frame base P = esp right after the prologue's stack adjust
(i.e. the offset space the compiler used for locals). Handles push/pop/
call/add esp/sub esp/sub esp via mem forms; ignores callee-cleanup.

Usage: r200_espmap.py LO HI [IMG]
"""
import sys
import re
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

img = open(sys.argv[3] if len(sys.argv) > 3 else "work/ascend_restored.bin", "rb").read()
LO, HI = int(sys.argv[1], 16), int(sys.argv[2], 16)
md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = True

imm_re = re.compile(r",\s*(0x[0-9a-f]+|\d+)$")

esp = 0
for ins in md.disasm(img[LO:HI], LO):
    mn, ops = ins.mnemonic, ins.op_str
    ann = []
    for o in ins.operands:
        # NB: o.mem.base == 41 does NOT mean ESP in the installed capstone
        # (t200 pitfall) — resolve the base register by name.
        if o.type == 3 and o.mem.base and ins.reg_name(o.mem.base) == "esp":
            ann.append(f"[[P{o.mem.disp + esp:+#x}]]")
    line = f"{ins.address:#07x}  {mn} {ops}"
    if ann:
        line += "   " + " ".join(ann)
    print(line)
    if mn == "push":
        esp -= 4
    elif mn == "pop":
        esp += 4
    # cdecl: CALL preserves ESP in the caller after the callee returns --
    # do NOT decrement here (t200: decrementing drifts every later annot).
    elif mn in ("add", "sub", "and", "xor"):
        m = imm_re.search(ops)
        if m and ops.split(",")[0].strip() == "esp":
            v = int(m.group(1), 0)
            esp += v if mn == "add" else -v
    elif mn == "leave":
        esp = 0
