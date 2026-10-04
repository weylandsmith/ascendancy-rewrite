#!/usr/bin/env python3
"""c0_anchor_test.py — the direct C=0 test for OQ-011.

Hypothesis: the payload loads at VA == its own file offset (base C = 0), so
some instruction operand should equal the file offset of a known DATA\\ path
template. Across 600k+ disassembled instructions, zero hits would be
impossible if the hypothesis were true. Measured 2026-10-04: ZERO imm operands
and ZERO no-base disp32 operands equal any anchor -> C != 0. This is the third
of four refutations catalogued in docs/re/loader.md section 4.

Also prints memory base-register usage (ebp/esp-dominant = normal frame code;
a -FPi build would show an ebx-dominant data pattern instead — 7,528 ebx uses
exist but no single-base consensus was found, see ebx_relative_test.py).

Exit 0 if any hit exists (base found), 2 if none (refutation reproduced).
Requires: capstone (~/tools/revenv), work/ascend_payload.bin,
work/functions.tsv (from scripts/ghidra/Seed2.java).
"""
import re, os, sys, collections
from capstone import Cs, CS_ARCH_X86, CS_MODE_32, CS_OP_IMM, CS_OP_MEM

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = open(os.path.join(ROOT, "work/ascend_payload.bin"), "rb").read()
funcs = [int(l.split("\t")[0], 16)
         for l in open(os.path.join(ROOT, "work/functions.tsv")).read().splitlines()[1:]
         if len(l.split("\t")) >= 2]
anchors = [m.start() for m in re.finditer(rb'DATA\\[A-Za-z%0-9._]{2,32}', d)]
aset = set(anchors)
md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = True
imm_anchor_hits, mem_abs_hits = [], []
base_regs = collections.Counter()
n_ins = 0
for fo in funcs:
    for ins in md.disasm(d[fo:fo + 8192], fo):
        n_ins += 1
        for op in ins.operands:
            if op.type == CS_OP_IMM and op.imm & 0xffffffff in aset:
                imm_anchor_hits.append((hex(fo), ins.mnemonic, ins.op_str, hex(op.imm & 0xffffffff)))
            elif op.type == CS_OP_MEM:
                m = op.mem
                base_regs[md.reg_name(m.base) if m.base else "none"] += 1
                if m.disp > 0 and (m.base == 0 or m.base is None) and m.disp in aset:
                    mem_abs_hits.append((hex(fo), ins.mnemonic, ins.op_str, hex(m.disp)))
print("insns:", n_ins, "anchors:", len(anchors))
print("operands whose value IS an anchor file offset (C=0 hypothesis):", len(imm_anchor_hits))
for x in imm_anchor_hits[:10]:
    print("   ", x)
print("mem operands with disp==anchor and no base:", len(mem_abs_hits))
for x in mem_abs_hits[:6]:
    print("   ", x)
print("memory base-register usage:", base_regs.most_common(10))
if imm_anchor_hits or mem_abs_hits:
    print("VERDICT: C=0 supported")
    sys.exit(0)
print("VERDICT: C=0 REFUTED (zero operands name any anchor offset)")
sys.exit(2)
