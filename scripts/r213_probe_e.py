#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t213 probe E — the decisive site-1 soundness check:
is EVERY predecessor-chain into 0x15c63 downstream of the bl=1 init block
0x15c14..0x15c34?  Prints in-edges (whole function, branches+fallthrough) of
the block heads on the site-1 chain, plus a worklist REACHABILITY test:
set R = blocks reachable from 0x15c34 (post-init) and R0 = blocks reachable
from the function entry WITHOUT passing through 0x15c14 (i.e. 0x15c14 removed);
then report whether 0x15c6d is in R0 (a stale-[esp+0x50] path would exist).
Usage: r213_probe_e.py [IMG]"""
import sys
from collections import deque
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

IMG = sys.argv[1] if len(sys.argv) > 1 else "work/ascend_restored.bin"
img = open(IMG, "rb").read()
FLO, FHI = 0x156D4, 0x17C25


def decode(lo, hi):
    out = {}
    off = lo
    while off < hi:
        md = Cs(CS_ARCH_X86, CS_MODE_32)
        md.detail = True
        got = False
        for ins in md.disasm(img[off:hi], off):
            out[ins.address] = ins
            off = ins.address + ins.size
            got = True
        if not got:
            off += 1
    return out


fn = decode(FLO, FHI)
succ = {}
pred = {}
for a, ins in fn.items():
    s = []
    if ins.mnemonic.startswith("j"):
        for op in ins.operands:
            if op.type == 2 and op.imm in fn:
                s.append(op.imm)
    if ins.mnemonic not in ("jmp", "ret", "retf") and a + ins.size in fn:
        s.append(a + ins.size)
    succ[a] = s
    for w in s:
        pred.setdefault(w, []).append(a)

print("== in-edges of the site-1 chain block heads ==")
for t in (0x15B5A, 0x15BB2, 0x15BB8, 0x15BC1, 0x15BC9, 0x15BD0, 0x15BDD, 0x15C00, 0x15C38, 0x15C4F):
    print(f"  {t:#07x} <- {[hex(x) for x in sorted(pred.get(t, []))]}")


def reach(start, blocked=()):
    seen, q = set(), deque([start])
    while q:
        v = q.popleft()
        if v in seen or v in blocked:
            continue
        seen.add(v)
        q.extend(succ.get(v, []))
    return seen


R = reach(FLO)                      # all reachable blocks from entry
R0 = reach(FLO, blocked=(0x15C14,)) # entry WITHOUT the init block
print("\n== reachability ==")
print(f"  reachable blocks from entry: {len(R)};  without 0x15c14: {len(R0)}")
print(f"  0x15c6d (site 1 store) reachable WITHOUT init block 0x15c14: {0x15C6D in R0}")
print(f"  0x15d98 (site 2 store) reachable from entry: {0x15D98 in R}")
lost = sorted(hex(x) for x in (R - R0))
print(f"  blocks LOST when 0x15c14 is cut ({len(lost)}): {lost[:25]}")
# which of the lost blocks contain a phase store?
print("  phase stores inside lost set:", [x for x in lost if x in ("0x15c6d",)] or "none among [0x15c6d,0x15d98]")
# does any lost block dominate 0x15d98? (crude: is 0x15d98 in R0 -> no dominance concern)
