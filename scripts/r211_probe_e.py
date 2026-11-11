#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t211 probe E: full-obj0 branch-edge scan for target 0x4a350 (and control
targets 0x4a360/0x49f54 which HAVE E8 edges), plus dword-equality scan of the
whole image for 0x4a350 (jumptable candidate — NOTE t191: handler bindings may
live only in RAM; image dwords are unrelocated)."""
from capstone import Cs, CS_ARCH_X86, CS_MODE_32
img = open("work/ascend_restored.bin", "rb").read()

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

TARGETS = {0x4a350, 0x4a360, 0x49f54}
hits = {t: [] for t in TARGETS}
insns = decode_all(0x14bb0, 0x82bb0)
print("decoded:", len(insns))
for a, i in insns.items():
    if i.mnemonic.startswith("j") or i.mnemonic == "call":
        s = i.op_str
        if s.startswith("0x"):
            try:
                t = int(s, 16)
            except ValueError:
                continue
            if t in TARGETS:
                hits[t].append((a, i.mnemonic))
for t in sorted(TARGETS):
    print(f"edges -> {t:#07x}: {len(hits[t])}", [hex(a) for a, m in sorted(hits[t])][:12])

pat = (0x4a350).to_bytes(4, "little")
pos = []
start = 0
while True:
    k = img.find(pat, start)
    if k < 0:
        break
    pos.append(hex(k))
    start = k + 1
print("image dwords == 0x4a350:", pos)
