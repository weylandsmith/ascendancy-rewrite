#!/usr/bin/env python3
"""t213 probe B — (i) intra-function edge map into the site-2 cluster,
(ii) entry mechanism of 0x156d4 (zero E8 callers), (iii) dl/dh value defs.

(i)  Enumerate EVERY branch (jcc/JMP, rel8/rel16/rel32 + far EA) whose target
     lands in the site-2 cluster [0x15d36,0x15e7c) of function 0x156d4, plus
     fallthrough edges across epilogues, so the reaching-def set of the packed
     order buffer [esp+0x00] at 0x15d98 can be named honestly.
(ii) Entry census: search the whole image for dwords == 0x156d4 (jump-table
     candidates) and for any indirect jump near them; plus E8/EB/JMP-FAR forms.
(iii) defs of dl and dh in 0x156d4..0x16400 feeding the 0x16361/0x16385 writes.
Usage: r213_probe_b.py [IMG]
"""
import sys, struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

IMG = sys.argv[1] if len(sys.argv) > 1 else "work/ascend_restored.bin"
img = open(IMG, "rb").read()
FLO, FHI = 0x156D4, 0x17C25
CODE_LO, CODE_HI = 0x14BB0, 0x82BB0
CL_LO, CL_HI = 0x15D36, 0x15E7C


def decode(lo, hi):
    out, gaps = {}, []
    off = lo
    while off < hi:
        md = Cs(CS_ARCH_X86, CS_MODE_32); md.detail = True
        got = False
        for ins in md.disasm(img[off:hi], off):
            out[ins.address] = ins; off = ins.address + ins.size; got = True
        if not got:
            gaps.append(off); off += 1
    return out, gaps


fn, gaps = decode(FLO, FHI)
print(f"decoded {len(fn)} insns gaps={[hex(g) for g in gaps]}")

print("\n== (i) branch edges INTO the site-2 cluster ==")
for a, ins in sorted(fn.items()):
    if not ins.mnemonic.startswith("j"):
        continue
    for op in ins.operands:
        if op.type == 2:  # CS_OP_IMM
            t = op.imm
            if CL_LO <= t < CL_HI:
                print(f"  {a:#07x} {ins.mnemonic:<8} -> {t:#07x}")
print("  (rel16/rel32 forms are included by capstone operand imm; verify widths below)")
print("\n  branch insn widths near cluster boundaries:")
for a in sorted(fn):
    if ins := fn.get(a):
        if ins.mnemonic.startswith("j") and (CL_LO - 0x40 <= a < CL_LO or CL_HI <= a < CL_HI + 0x40):
            print(f"    {a:#07x} {ins.mnemonic:<8} -> {[hex(o.imm) for o in ins.operands if o.type==2]}")

print("\n  epilogue fallthrough check: what follows each ret in 0x15a8f..0x15e90?")
for a in sorted(fn):
    if fn[a].mnemonic == "ret" and 0x15A8F <= a <= 0x15E90:
        nxt = a + fn[a].size
        ni = fn.get(nxt)
        print(f"    ret {a:#07x} -> fall {nxt:#07x} {ni.mnemonic + ' ' + ni.op_str if ni else '(gap)'}")

print("\n== (ii) entry mechanism for 0x156d4 ==")
pat = struct.pack("<I", 0x156D4)
hits = []
i = 0
while True:
    j = img.find(pat, i)
    if j < 0: break
    hits.append(j); i = j + 1
print(f"  image dwords == 0x156d4 at file offsets: {[hex(h) for h in hits]}")
md = Cs(CS_ARCH_X86, CS_MODE_32); md.detail = True
for h in hits:
    lo = max(h - 40, CODE_LO)
    print(f"  --- context around {hex(h)} (decode anchored {hex(lo)}) ---")
    for ins in md.disasm(img[lo:h + 24], lo):
        mark = "  <<" if ins.address <= h < ins.address + ins.size else ""
        print(f"    {ins.address:#07x} {ins.mnemonic} {ins.op_str}{mark}")
# also: FF /4 indirect jumps anywhere (census of jmp [mem]) to see if a table-walk exists
print("\n== (iii) dl/dh defs 0x156d4..0x16400 ==")
for a in sorted(fn):
    if a > 0x16400: break
    ins = fn[a]
    if ins.mnemonic == "mov" and ins.op_str.split(",")[0].strip() in ("dl", "dh", "edx", "edxh"):
        print(f"  {a:#07x} mov {ins.op_str}")
