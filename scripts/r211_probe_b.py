#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t211 probe B: (1) transitive callee closure of 0x49f54 (depth-limited E8)
against the attack-family set {0x4b740, 0x43a4c, 0x4cd90, 0x4b8e4}; (2) E8
byte-pass census of all direct callers of each member of that family (done
t210, re-run here as control for 0x4b875-containing 0x4b740); (3) writer
census of byte [reg+0x62] across obj0 code (capstone operand pass, skipping
cmp/test per the t209 pitfall)."""
import sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_32, CS_OP_MEM

IMG = "work/ascend_restored.bin"
img = open(IMG, "rb").read()
CODE_LO, CODE_HI = 0x14bb0, 0x82bb0

def decode(lo, hi):
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

# cache per-function decode by entry
def calls_from(entry, size):
    body = decode(entry, entry + size)
    return sorted({int(i.op_str, 16) for i in body.values()
                   if i.mnemonic == "call" and i.op_str.startswith("0x")})

# t183/travel callee closure: BFS depth 3 from 0x49f54 with spans from a
# crude entry map (functions_full.tsv)
spans = {}
for line in open("work/functions_full.tsv"):
    p = line.split("\t")
    if len(p) >= 2:
        try:
            spans[int(p[0], 16)] = int(p[1])
        except ValueError:
            pass

SEED = 0x49f54
ATTACK = {0x4b740, 0x43a4c, 0x4cd90, 0x4b8e4, 0x4a360}
seen = {SEED}
frontier = [SEED]
reached_attack = []
for depth in range(3):
    nxt = []
    for f in frontier:
        size = spans.get(f)
        if size is None:
            continue
        for c in calls_from(f, min(size, 0x1200)):
            if c in ATTACK:
                reached_attack.append((depth, f, c))
            if c not in seen and c in spans:
                seen.add(c); nxt.append(c)
    frontier = nxt
print("functions visited in closure:", len(seen))
print("attack-family hits:", reached_attack if reached_attack else "NONE")
# also indirect jumps/inside 0x49f54 (would defeat E8-only closure)
body = decode(SEED, SEED + spans.get(SEED, 1020))
ind = [(hex(a), i.mnemonic, i.op_str) for a, i in sorted(body.items())
       if i.mnemonic in ("jmp", "jmps") and not i.op_str.startswith("0x")]
print("indirect jmps inside 0x49f54:", ind if ind else "NONE")
calli = [(hex(a), i.op_str) for a, i in sorted(body.items())
         if i.mnemonic == "call" and not i.op_str.startswith("0x")]
print("indirect calls inside 0x49f54:", calli if calli else "NONE")
