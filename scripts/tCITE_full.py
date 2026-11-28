#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tCITE pass 4 (full-coverage): apply pass-2/pass-3 adjudication to ALL
1235 candidates (not just CODE-SHAPE). Verdicts:
  REACHABLE  : real instruction site (ghp5 map hole) — doc fine
  JUMPTAB    : u32 of the addr stored outside functions — dispatch target fine
  OPERAND    : sits inside a valid instruction (byte-scan/fixup anchor
               convention) — fine unless prose claims a call/entry SITE
  CALLSITE   : OPERAND *and* prose words name a call/fn/entry/handler site
               -> hand-adjudicate (the ships.md 0x250bb shape)
  DATAWORD   : u32-LE at the address decodes to something unrelated and prose
               is about data — fine
  RESIDUAL   : none of the above — hand-adjudicate.
Prints counts + CALLSITE and RESIDUAL lists.
"""
import os, re, json, bisect
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

ROOT = "/home/hrethric/projects/ascendancy"
data = open(f"{ROOT}/work/ascend_restored.bin", "rb").read()
funcs = []
for line in open(f"{ROOT}/work/functions_full.tsv").read().splitlines()[1:]:
    p = line.split("\t")
    if len(p) >= 2:
        try:
            funcs.append((int(p[0], 16), int(p[1], 16)))
        except ValueError:
            pass
funcs.sort()
starts = [s for s, _ in funcs]
md = Cs(CS_ARCH_X86, CS_MODE_32)
bounds = set()
for s, sz in funcs:
    end = min(s + sz, len(data)); a = s
    while a < end:
        bounds.add(a); got = False
        for ins in md.disasm(data[a:min(end, a + 16)], a):
            if ins.address != a: break
            a = ins.address + ins.size; got = True; break
        if not got: a += 1

def first_insn(addr):
    for ins in md.disasm(data[addr:addr + 16], addr):
        return ins
    return None

def reach(addr):
    for b in range(addr - 32, addr + 1):
        if b not in bounds: continue
        for ins in md.disasm(data[b:b + 48], b):
            if ins.address == addr: return b
            if ins.address > addr: break
    return None

def jumptab_named(addr):
    enc = addr.to_bytes(4, "little"); i = 0
    while True:
        i = data.find(enc, i)
        if i < 0: return False
        j = bisect.bisect_right(starts, i) - 1
        if j < 0 or i >= min(funcs[j][0] + funcs[j][1], len(data)):
            return True
        i += 1

SITE = re.compile(r"\b(fn|entry|handler|dispatch|caller|callee|switcher|router|router|builder|builder|chain|tail|body|arm|gate|gate|loop|loop|block|branch|leg|leg|start|start|anchor|anchor|site|site|path|path|sole|sole|calls?|calls?)\b", re.I)
cands = json.load(open("/tmp/tcite_cands.json"))
from collections import Counter
vc = Counter()
callsite, residual = [], []
for c in cands:
    a = int(c["addr"], 16)
    if a in bounds:
        vc["BOUNDRY?!"] += 1
        continue
    if reach(a) is not None:
        vc["REACHABLE"] += 1; continue
    if jumptab_named(a):
        vc["JUMPTAB"] += 1; continue
    spans = None
    for k in range(1, 9):
        ins = first_insn(a - k)
        if ins is not None and ins.size > k:
            spans = (k, f"{ins.address:x}:{ins.mnemonic} {ins.op_str}")
            break
    if spans:
        vc["OPERAND"] += 1
        ctx = (c["pre"] + " " + c["post"])
        if SITE.search(ctx):
            callsite.append((c, spans))
    else:
        vc["RESIDUAL"] += 1
        residual.append(c)
print(f"total_candidates={len(cands)} verdicts={dict(vc)}")
print("=== CALLSITE (mid-instruction cite + site-role prose: hand adjudicate) ===")
seen = set()
for c, sp in callsite:
    key = (c["doc"], c["addr"])
    if key in seen: continue
    seen.add(key)
    print(f"{c['doc']}:{c['line']} {c['addr']} enclosing={sp[1]} | ...{c['pre']} << {c['post']}...")
print("=== RESIDUAL ===")
for c in residual:
    print(f"{c['doc']}:{c['line']} {c['addr']} | ...{c['pre']} << {c['post']}...")
