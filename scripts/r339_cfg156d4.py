#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t339 — CFG reachability inside fn 0x156d4 (BatControlWnd msg tree,
file_off 0x156d4 size 0x9f7 per work/functions_full.tsv).
Edges: fallthrough, jmp, jcc (both arms), call (into target). call-indirect
stops. Reports forward-reachable sets from the banked branch heads and which
named targets {0x15ebf 0x1c01-branch, 0x16147/0x16181 gate block, 0x1615d,
0x161d1, 0x1616f relay, 0x1620e/0x16248 ring posts} each reaches."""
import re, collections, collections.abc

INSN = re.compile(r"^\s+([0-9a-f]+):\s*((?:[0-9a-f]{2}[ ]?)+)\s+(.*)$")
LO, HI = 0x156d4, 0x164c0

ins = {}   # addr -> (mnem, ops)
order = []
with open("work/r331_disasm.txt", errors="replace") as f:
    for line in f:
        m = INSN.match(line)
        if not m: continue
        a = int(m.group(1), 16)
        if not (LO <= a < HI): continue
        t = m.group(3).split("#")[0].strip()
        p = t.split(None, 1)
        ins[a] = (p[0] if p else "", p[1] if len(p) > 1 else "")
        order.append(a)
order.sort()
print(f"fn 0x156d4: {len(ins)} insns decoded, {hex(order[0])}..{hex(order[-1])}")

def succ(a):
    mn, op = ins[a]
    nxt = None
    # next instruction by address (may have a gap = nested fn)
    later = [x for x in order if x > a]
    nxt = later[0] if later and later[0] < HI else None
    if mn in ("jmp",):
        try: return {int(op.split()[0], 16)}
        except Exception: return set()
    if mn.startswith("j"):
        try: t = {int(op.split()[-1], 16)}
        except Exception: t = set()
        return t | ({nxt} if nxt else set())
    if mn == "call":
        try:
            t = int(op.split()[0], 16)
            return {t} if t < 0x100000 else set()
        except Exception:
            return set()   # indirect
    if mn in ("ret", "retf", "hlt"):
        return set()
    return {nxt} if nxt else set()

def reach(start, cap=4000):
    seen = set(); dq = collections.deque([start])
    while dq and len(seen) < cap:
        a = dq.popleft()
        if a in seen: continue
        seen.add(a)
        if a in ins:
            dq.extend(succ(a))
    return seen

NAMED = {0x15ebf: "0x1c01-branch", 0x16147: "gate-0x16147", 0x16181: "gate-0x16181",
         0x1615d: "post-0x1615d", 0x1616f: "relay-0x1616f", 0x161d1: "post-0x161d1",
         0x1620e: "ringpost-0x1620e", 0x16248: "ringpost-0x16248",
         0x156d4: "ENTRY", 0x162ac: "subtree-head", 0x163e4: "cmp-0x324",
         0x162bd: "cmp-0x325", 0x158f3: "branch-0x325-target",
         0x16420: "grid-slot3-fn", 0x1642c: "0x1c01-receiver-site"}
HEADS = [0x156d4, 0x15ebf, 0x162ac, 0x163e4, 0x162bd, 0x158f3, 0x1625c]
for h in HEADS:
    r = reach(h)
    hits = [f"{hex(t)}({NAMED[t]})" for t in NAMED if t in r and t != h]
    posts = sorted(a for a in r if a in ins and ins[a][0] == "call"
                   and ins[a][1].strip() in ("0x56ca4", "0x56ad4"))
    print(f"from {hex(h)}: |R|={len(r)} named={hits}")
    if posts:
        print(f"   posts: " + ", ".join(f"{hex(a)}->{ins[a][1].strip()}" for a in posts))

# reverse map: who j-edges into the gate block 0x16140..0x161d1 range heads
print("\nin-edges into 0x16147 / 0x16181 / 0x16140-block (within fn):")
for a in order:
    mn, op = ins[a]
    if mn.startswith("j"):
        try: t = int(op.split()[-1], 16)
        except Exception: continue
        if 0x16140 <= t <= 0x161d1:
            print(f"  {hex(a)}: {mn} {op}")
# what falls through into 0x16140..0x16147?
prev = [a for a in order if a < 0x16147][-3:]
for a in prev:
    print(f"  before: {hex(a)}: {ins[a][0]} {ins[a][1]}")
