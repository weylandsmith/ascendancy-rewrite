#!/usr/bin/env python3
"""t211 probe C: (1) writer census of byte [reg+0x62] (the 0x49f28 dispatch
discriminator) across obj0 code — capstone operand pass, resume-on-gap (t201
pitfall: sequential capstone STOPS at data gaps; blind pass found 36/325).
Writes = mov/store forms whose mem operand disp==0x62, EXCLUDING cmp/test
(t209 pitfall). (2) writers of [esp+0x730]/[esp+0x734] within 0x4cd90
(splash-loop bounds) and the loop bodies that read them."""
import sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_32, CS_OP_MEM

IMG = "work/ascend_restored.bin"
img = open(IMG, "rb").read()
CODE_LO, CODE_HI = 0x14bb0, 0x82bb0

def decode_all(lo, hi):
    out = {}
    off = lo
    while off < hi:
        md = Cs(CS_ARCH_X86, CS_MODE_32); md.detail = True
        got = False
        for ins in md.disasm(img[off:hi], off):
            out[ins.address] = ins
            off = ins.address + ins.size
            got = True
        if not got:
            off += 1
    return out

insns = decode_all(CODE_LO, CODE_HI)
print("decoded insns:", len(insns))

STORE_MNEMS = {"mov", "movzx", "movsx", "lea", "xchg", "and", "andn", "or",
               "xor", "xorps", "movaps", "movups", "movlpd", "fld", "fst",
               "fstp", "sts", "st", "rep"}
print("\n== [reg+0x62] byte-field: STORE-form sites (disp==0x62) ==")
n = 0
for a, i in sorted(insns.items()):
    if i.mnemonic in ("cmp", "test"):
        continue
    for op in i.operands:
        if op.type == CS_OP_MEM and op.mem.disp == 0x62:
            # store-form: destination is first operand (intel syntax operand 0)
            if i.operands and i.operands[0].type == CS_OP_MEM and i.operands[0].mem.disp == 0x62:
                print(f"  {a:#07x}  {i.mnemonic} {i.op_str}")
                n += 1
print("total store sites:", n)

print("\n== ALL refs disp==0x62 count (control) ==")
tot = sum(1 for a, i in insns.items()
          if any(op.type == CS_OP_MEM and op.mem.disp == 0x62 for op in i.operands))
print("all-mem-ref sites:", tot)

# ---- (2) [esp+0x730]/[esp+0x734] inside 0x4cd90 (span 2307 -> ..0x4d693)
print("\n== refs [esp+0x730] / [esp+0x734] / [esp+0x73c] inside 0x4cd90 ==")
body = decode_all(0x4cd90, 0x4cd90 + 2307)
for a, i in sorted(body.items()):
    for op in i.operands:
        if op.type == CS_OP_MEM and op.mem.disp in (0x730, 0x734, 0x73c) \
           and i.reg_name(op.mem.base) == "esp":
            dst = (i.operands and i.operands[0].type == CS_OP_MEM
                   and i.operands[0].mem.disp in (0x730, 0x734, 0x73c))
            print(f"  {a:#07x} {'W' if dst else 'r'}  {i.mnemonic} {i.op_str}")
            break
