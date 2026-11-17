#!/usr/bin/env python3
"""t421 C1: fast raw-byte referrer census for the 0x892ac seam.

Restored image holds intra-object offsets at fixup sites (t421 F1a), so the
census searches BOTH forms of every u32 whose ABSOLUTE value lands in
0x89280..0x89340:
    absolute form  v          (non-fixup immediates / data pointers)
    intra form     v-0x82bb0  (obj1-data-targeting immediates at fixup sites)
Hits are then disassembled in a narrow window to classify insn vs data.
"""
import os, struct, sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

ROOT = "/home/hrethric/projects/ascendancy"
res = open(os.path.join(ROOT, "work/ascend_restored.bin"), "rb").read()
pay = open(os.path.join(ROOT, "work/ascend_payload.bin"), "rb").read()
OBJ1 = 0x82bb0
LO, HI = 0x89280, 0x89340

def scan(buf, name):
    print(f"== {name} ({len(buf):#x} bytes) ==")
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    seen = set()
    for v in range(LO, HI):
        for form, delta in (("abs", 0), ("intra", OBJ1)):
            pat = struct.pack('<I', v - delta)
            if len(pat) < 4 or pat[0] == 0 and pat[1] == 0:
                pass
            start = 0
            while True:
                p = buf.find(pat, start)
                if p < 0:
                    break
                start = p + 1
                key = (p, v, form)
                if key in seen:
                    continue
                seen.add(key)
    # collapse: for each hit offset, disassemble the containing insn window
    offs = sorted({p for (p, v, f) in seen})
    print(f"  raw u32 hits: {len(seen)} at {len(offs)} offsets")
    for p in offs:
        w_lo = max(0, p - 2)
        # decode backwards is impossible; sweep a small window and keep insns covering p..p+4
        cands = []
        for back in range(0, 12):
            s = p - back
            for i in md.disasm(res[s:s+24], s):
                if i.address <= p and p + 4 <= i.address + i.size:
                    cands.append((s, f"{i.address:#07x}: {i.mnemonic} {i.op_str}", i.size))
                    break
            if cands:
                break
        tag = cands[0][1] if cands else "(no clean insn decode -> data region)"
        in_code = 0x14bb0 <= p < 0x82bb0
        print(f"  off {p:#07x} code={in_code} : {tag}")

scan(res, "ascend_restored.bin")
scan(pay, "ascend_payload.bin")
