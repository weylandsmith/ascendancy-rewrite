#!/usr/bin/env python3
"""t213 — linear-sweep CFG for the 0x15b00..0x15e60 region + predecessor query.

Purpose: the t211 S4 Amendment banked the al-form [ship+0x62] writers
0x15c6d / 0x15d98 as a value-source residue. This builds a local CFG (edges
from capstone branch operands + fallthrough, insns decoded contiguously from
region start with gap-skip, t201 count-guard printed) and prints
  (1) decoded-insn count (guard: expect ~region/3),
  (2) predecessor lists for requested addresses,
  (3) every store to [esp+0x50] / [esp] (phase-byte local) with its value op,
  (4) every read of the stack arg at [esp+0x84] and [ebp+0xb0]/[ebp+0xab],
  (5) SCC membership of the region (t210 law: SCC not back-edge).
Usage: r213_cfg_15b.py IMG [pred:ADDR ...]
"""
import sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

IMG, LO, END = sys.argv[1], 0x15b00, 0x15e60
img = open(IMG, "rb").read()
md = Cs(CS_ARCH_X86, CS_MODE_32)
md.detail = True

insns = {}          # addr -> insn
order = []
off = LO
gaps = 0
while off < END:
    got = False
    for ins in md.disasm(img[off:END], off):
        insns[ins.address] = ins
        order.append(ins.address)
        off = ins.address + ins.size
        got = True
    if not got:
        gaps += 1
        off += 1
print(f"DECODED={len(insns)} GAPS={gaps} (guard: region {END-LO} bytes)")

preds = {}
succs = {}
for a, ins in insns.items():
    nxt = a + ins.size
    tgt = None
    if ins.id == 0:
        continue
    m = ins.mnemonic
    if m.startswith("j"):
        ops = ins.operands
        if ops and ops[0].type == 2:  # CS_OP_IMM (t210/t212 law: 2, not 3)
            tgt = ops[0].imm
            if not (LO <= tgt < END):
                tgt = f"OUT:{tgt:#x}"
        if tgt is not None:
            succs.setdefault(a, []).append(tgt)
            preds.setdefault(tgt, []).append(a)
        if m not in ("jmp", "ret"):
            succs.setdefault(a, []).append(nxt)
            preds.setdefault(nxt, []).append(a)
    elif m == "ret":
        pass
    else:
        succs.setdefault(a, []).append(nxt)
        preds.setdefault(nxt, []).append(a)

print("\n--- predecessors ---")
for spec in sys.argv[2:]:
    lbl, addr = spec.split(":")
    a = int(addr, 16)
    print(f"{a:#x} preds: {[hex(p) for p in sorted(preds.get(a, []))]}")

print("\n--- phase-local stores/loads (esp+0x50, esp+0, esp+0x84) ---")
for a in order:
    s = insns[a].op_str
    m = insns[a].mnemonic
    if ("esp + 0x50]" in s) or (s.startswith("al, byte ptr [esp]") or s == "byte ptr [esp], al") or ("esp + 0x84]" in s):
        print(f"  {a:#07x} {m} {s}")

print("\n--- ebp-relative reads in region ---")
for a in order:
    s = insns[a].op_str
    if "ebp + " in s:
        print(f"  {a:#07x} {insns[a].mnemonic} {s}")

# Tarjan SCC (t210 tool law) restricted to in-region edges
import sys as _s
sys.setrecursionlimit(100000)
idx, low, onstk, stack, comp = {}, {}, set(), [], []
cnt = [0]
def strong(v):
    idx[v] = low[v] = cnt[0]; cnt[0] += 1
    stack.append(v); onstk.add(v)
    for w in succs.get(v, []):
        if not isinstance(w, int): continue
        if w not in idx:
            strong(w); low[v] = min(low[v], low[w])
        elif w in onstk:
            low[v] = min(low[v], idx[w])
    if low[v] == idx[v]:
        c = []
        while True:
            w = stack.pop(); onstk.discard(w); c.append(w)
            if w == v: break
        if len(c) > 1: comp.append(c)
for v in sorted(insns):
    if v not in idx: strong(v)
print("\n--- nontrivial SCCs in region ---")
for c in comp:
    print(f"  size {len(c)}: {hex(min(c))}..{hex(max(c))}")
