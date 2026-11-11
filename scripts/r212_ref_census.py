#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t212 — every reference to the displayed-score slot region in obj0.

OQ-021 residue: the presenter 0x28074/0x280be reads dword [0x482fb]; the
aicode.md P7 lead writes WORD [0x48300] (0x2519b/0x25217/0x25225) — a slot 5
bytes higher, OUTSIDE that dword (0x482fb..0x482fe). So the producer of the
DISPLAYED count is still unmapped.

Two passes over obj0 code [0x14bb0,0x82bb0) of work/ascend_restored.bin,
capstone with resume-past-data-gaps (t201 law: a sequential pass dies at the
first undecodable byte and silently under-reports):

  PASS A  memory operands whose disp32 falls in [LO,HI) — absolute (no base)
          and [reg+disp] / [reg+index*scale+disp] forms alike.
  PASS B  INSTRUCTIONS WHOSE IMMEDIATE falls in [LO,HI) — the address-taking
          form (`mov eax, 0x48304` at 0x25008 feeding a memset, t206) which a
          memory-operand-only census misses entirely.

POSITIVE CONTROLS (asserted; a zero is trusted only if these are found):
  PASS A finds 0x28074 (read) and 0x2519b (inc word [0x48300]).
  PASS B finds 0x25008 (mov eax, 0x48304).
Exit 0 with findings; exit 2 if a control fails (census is then NOT usable).
"""
import sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

IMG = sys.argv[1] if len(sys.argv) > 1 else "work/ascend_restored.bin"
LO = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0x482F0
HI = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x48310
img = open(IMG, "rb").read()
CLO, CODE_HI = 0x14BB0, 0x82BB0
WRITE_MN = {"mov", "movzx", "movsx", "lea", "inc", "dec", "neg", "not", "xchg",
            "or", "and", "xor", "add", "sub", "sbb", "shl", "shr", "sar",
            "stosb", "stosd", "movabs", "pop", "popal"}

def newmd():
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    md.detail = True
    return md

mem_rows, imm_rows = [], []
off = CLO
while off < CODE_HI:
    end = off
    md = newmd()
    try:
        it = md.disasm(img[off:CODE_HI], off)
        while True:
            ins = next(it)
            for i, o in enumerate(ins.operands):
                if o.type == 3:                      # CS_OP_MEM
                    d = o.mem.disp
                    if LO <= d < HI:
                        base = md.reg_name(o.mem.base) if o.mem.base else ""
                        idx = (f"*{o.mem.scale}{md.reg_name(o.mem.index)}"
                               if o.mem.index else "")
                        shape = ("ABS" if not base and not idx
                                 else f"{base}{idx}+disp")
                        wr = "W" if (ins.mnemonic in WRITE_MN and i == 0) else "R"
                        mem_rows.append((ins.address, wr, shape, d,
                                         f"{ins.mnemonic} {ins.op_str}"))
                elif o.type == 2:                    # CS_OP_IMM
                    v = o.imm   # capstone x86 detail attribute is `.imm`
                    if LO <= v < HI:
                        imm_rows.append((ins.address, v,
                                         f"{ins.mnemonic} {ins.op_str}"))
            end = ins.address + ins.size
    except StopIteration:
        pass
    off = end if end > off else off + 1

print(f"region {LO:#x}..{HI:#x}   code [{CLO:#x},{CODE_HI:#x})")
print(f"\nPASS A — memory operands: {len(mem_rows)} hits")
for a, wr, shape, d, txt in sorted(mem_rows):
    print(f"  {a:#07x} {wr} {shape:22s} disp={d:#x}  {txt}")
print(f"\nPASS B — address-taking immediates: {len(imm_rows)} hits")
for a, v, txt in sorted(imm_rows):
    print(f"  {a:#07x} imm={v:#x}  {txt}")

ctrl_a = {0x28074, 0x280be, 0x2519b}
ctrl_b = {0x25008}
got_a = {a for a, *_ in mem_rows}
got_b = {a for a, *_ in imm_rows}
ok = True
for c in sorted(ctrl_a):
    if c not in got_a:
        ok = False
        print(f"CONTROL FAIL: PASS A missing {c:#x}")
for c in sorted(ctrl_b):
    if c not in got_b:
        ok = False
        print(f"CONTROL FAIL: PASS B missing {c:#x}")
print("\ncontrols:", "OK" if ok else "FAILED — do not trust the zeros")
sys.exit(0 if ok else 2)
