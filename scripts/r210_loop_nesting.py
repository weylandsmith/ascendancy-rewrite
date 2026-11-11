#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t210 — CFG loop-nesting census for the callers of 0x4b740.

PITFALL THIS SCRIPT EXISTS FOR (t210): a back-edge is NOT 'target <= site'.
The 0x3a174 defense loop's back-edges are `jne 0x3a2c9` @0x3a30e and
`je 0x3a2c9` @0x3a31f — targets NUMERICALLY ABOVE the site (forward-encoded
loop bodies: the loop HEAD sits mid-range). The only sound static loop test
is: build the CFG (fallthrough + taken-branch edges) inside a function
boundary and find SCCs of size > 1 (Tarjan). Function entry is approximated
by scanning back to the last `ret`+nop/0xCC padding boundary.

Usage: r210_loop_nesting.py [IMG] caller_hex [caller_hex ...]
Prints, per caller: function window, enclosing SCC (loop) if any, the
back-edges, and the mode-register (edx) provenance lines near the call.
"""
import sys
from capstone import Cs, CS_ARCH_X86, CS_MODE_32, CS_OP_IMM
# PITFALL (t210, self-caught): capstone operand types are INVALID=0 REG=1
# IMM=2 MEM=3. Comparing `operands[0].type == 3` silently means MEM and yields
# a branch-edge-less CFG (zero SCCs, zero back-edges — false 'no loop').

IMG = sys.argv[1] if len(sys.argv) > 1 else "work/ascend_restored.bin"
CALLERS = [int(x, 16) for x in sys.argv[2:]]
img = open(IMG, "rb").read()

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
            off += 1  # skip undecodable byte (t207 seed-restart idiom)
    return out

def find_entry(c, max_back=0x3000):
    """Nearest preceding ret followed by nop/CC padding ~= function boundary.
    Returns ALL plausible boundaries (each ret+1), so callers can pick the one
    that decodes aligned (insns[C] must be exactly the E8 call)."""
    lo = c - max_back
    insns = decode(lo, c)
    bests = []
    for a in sorted(insns):
        ins = insns[a]
        if ins.mnemonic in ("ret", "retf") and a < c - 1:
            nxt = a + ins.size
            if nxt < len(img) and img[nxt] in (0x90, 0xCC, 0xC3):
                bests.append(nxt)
    return bests or [lo]

def sccs(insns, lo, hi):
    """Tarjan SCC over addresses in [lo,hi) with edges: fallthrough + branch."""
    graph = {}
    for a, ins in insns.items():
        edges = []
        if ins.mnemonic.startswith("j"):
            if ins.operands and ins.operands[0].type == CS_OP_IMM:  # imm target
                t = ins.operands[0].imm
                if lo <= t < hi:
                    edges.append(t)
                if ins.mnemonic != "jmp":
                    nxt = a + ins.size
                    if nxt in insns:
                        edges.append(nxt)
            else:
                edges.append(("indirect", a))
        elif ins.mnemonic in ("ret", "retf", "iret"):
            pass
        else:
            nxt = a + ins.size
            if nxt in insns:
                edges.append(nxt)
        graph[a] = edges
    # --- iterative Tarjan ---
    index = {}
    low = {}
    on = {}
    st = []
    scc_out = []
    counter = [0]
    for v0 in sorted(insns):
        if v0 in index:
            continue
        work = [(v0, iter(graph.get(v0, [])))]
        path = []
        while work:
            v, it = work[-1]
            if v not in index:
                counter[0] += 1
                index[v] = low[v] = counter[0]
                st.append(v); on[v] = True
            pushed = False
            for w in it:
                if isinstance(w, tuple):
                    continue
                if w not in index:
                    work.append((w, iter(graph.get(w, []))))
                    pushed = True
                    break
                elif on.get(w):
                    low[v] = min(low[v], index[w])
            if pushed:
                continue
            if low[v] == index[v]:
                comp = []
                while True:
                    w = st.pop(); on[w] = False
                    comp.append(w)
                    if w == v:
                        break
                scc_out.append(comp)
            work.pop()
            if work:
                p = work[-1][0]
                low[p] = min(low[p], low[v])
    return scc_out, graph

for C in CALLERS:
    chosen = None
    for entry in sorted(find_entry(C), reverse=True):  # NEAREST boundary first
        if entry >= C:
            continue
        insns = decode(entry, C + 0x600)
        if C in insns and insns[C].mnemonic == "call":
            chosen = (entry, insns)
            break
    if chosen is None:  # fallback: raw window ending past C
        entry = max(find_entry(C), default=C - 0x1800)
        insns = decode(entry, C + 0x600)
        chosen = (entry, insns)
    entry, insns = chosen
    hi = max(insns) + 1 if insns else entry
    comps, graph = sccs(insns, entry, hi)
    enc = [c for c in comps if len(c) > 1 and min(c) <= C <= max(c)]
    print(f"=== caller {C:#x} fn≈{entry:#x}..{hi:#x} aligned={C in insns and insns[C].mnemonic=='call'} SCCs>1: {len([c for c in comps if len(c)>1])}")
    if enc:
        for c in sorted(enc, key=lambda x: -min((m for m in x if m <= C), default=0)):
            s = min(c); e = max(c)
            bedges = []
            for a in c:
                for w in graph.get(a, []):
                    if not isinstance(w, tuple) and w in c and (w not in c or True):
                        pass
            for a in sorted(c):
                ins = insns[a]
                if ins.mnemonic.startswith("j") and ins.operands and ins.operands[0].type == CS_OP_IMM:
                    t = ins.operands[0].imm
                    if t in c:
                        bedges.append((hex(a), hex(t), ins.mnemonic))
            print(f"    ENCLOSING SCC {s:#x}..{e:#x} contains-call; back/target-edges {bedges[:8]}")
    else:
        print("    NOT inside any loop (acyclic path from entry)")
