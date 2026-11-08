#!/usr/bin/env python3
"""t339 — cross-function reachability + poster-site report.
(1) callers of fn 0x30c9c (child-list msg router entry) and of 0x30e0e/0x30edc arms.
(2) BFS from fn 0x156d4 entry over CALL edges (bounded by function extents
    from work/functions_full.tsv; j-edges inside each fn), reporting every
    reached site that calls 0x56ca4/0x56ad4 with the edx/ebx provenance line,
    and every reached `mov edx,0x1c01`-class immediate."""
import re, collections, bisect

INSN = re.compile(r"^\s+([0-9a-f]+):\s*((?:[0-9a-f]{2}[ ]?)+)\s+(.*)$")
addr = []; mnem = []; ops = []
for line in open("work/r331_disasm.txt", errors="replace"):
    m = INSN.match(line)
    if not m: continue
    addr.append(int(m.group(1), 16))
    t = m.group(3).split("#")[0].strip(); p = t.split(None, 1)
    mnem.append(p[0] if p else ""); ops.append(p[1] if len(p) > 1 else "")

fn = []
with open("work/functions_full.tsv") as f:
    next(f)
    for line in f:
        q = line.split()
        if len(q) >= 2:
            try: fn.append((int(q[0], 16), int(q[1])))
            except: pass
fn.sort()
starts = [a for a, s in fn]
def fnof(a):
    i = bisect.bisect_right(starts, a) - 1
    if i < 0: return None
    s, z = fn[i]
    return (s, s + z) if a < s + z else None

# index insns per address
pos = {a: i for i, a in enumerate(addr)}

def jtargets(a):
    mn, op = mnem[pos[a]], ops[pos[a]]
    out = []
    if mn == "jmp" or (mn.startswith("j") and mn != "jmp"):
        try: out.append(int(op.split()[-1], 16))
        except: pass
    return out

# (1) callers of 0x30c9c / fallthrough-arms
print("== call sites -> 0x30c9c (child-router), 0x30edc, 0x30e0e ==")
for i, (a, mn, o) in enumerate(zip(addr, mnem, ops)):
    if mn == "call":
        try: t = int(o.split()[0], 16)
        except: continue
        if t in (0x30c9c, 0x30edc, 0x30e0e, 0x30ce8):
            print(f"  {hex(a)}: {mn} {hex(t)}  (in {fnof(a)})")

# (2) BFS from 0x156d4 over call-edges + intra-fn j-edges
def callees_of(a):
    """all direct call targets textually inside a's function extent."""
    ext = fnof(a)
    lo, hi = ext if ext else (a, a + 1)
    out = set()
    i0 = pos.get(a, 0)
    # scan from a to end of function
    for i in range(i0, len(addr)):
        if addr[i] >= hi: break
        if mnem[i] == "call":
            try:
                t = int(ops[i].split()[0], 16)
                if t < 0x100000: out.add(t)
            except: pass
    return out

def jclosure(a):
    seen = {a}; dq = collections.deque([a])
    ext = fnof(a) or (a, a + 1)
    while dq:
        x = dq.popleft()
        for t in jtargets(x):
            if t not in seen and ext[0] <= t < ext[1]:
                seen.add(t); dq.append(t)
    return seen

start = 0x156d4
visited_f = set(); dq = collections.deque([start])
edges = {}
depth = {start: 0}
while dq:
    f0 = dq.popleft()
    if f0 in visited_f or len(visited_f) > 3000: continue
    visited_f.add(f0)
    cs = [c for c in callees_of(f0) if fnof(c)]
    edges[f0] = sorted(cs)
    for c in cs:
        depth[c] = depth[f0] + 1
        if c not in visited_f: dq.append(c)

print(f"\n== BFS from fn 0x156d4: {len(visited_f)} fns reachable (call-depth<=...) ==")

POST_SITES = []
for f0 in visited_f:
    ext = fnof(f0)
    if not ext: continue
    i0 = pos.get(f0, 0)
    for i in range(i0, len(addr)):
        if addr[i] >= ext[1]: break
        if mnem[i] == "call" and ops[i].strip() in ("0x56ca4", "0x56ad4"):
            # provenance: nearest prior edx write
            ed = "?"
            for j in range(i - 1, max(i - 8, 0), -1):
                o = ops[j]
                if o.split(",")[0].strip() == "edx" and mnem[j].startswith(("mov", "xor")):
                    ed = f"{hex(addr[j])}: {mnem[j]} {o}"; break
            POST_SITES.append((f0, depth.get(f0), addr[i], ops[i].strip(), ed))
for f0, d, a, t, ed in sorted(POST_SITES, key=lambda x: x[2]):
    print(f"  fn {hex(f0)} d={d}: {hex(a)} call {t}  edx<- {ed}")

print("\n== reached `mov edx,0x1c01/0x1c02` immediates ==")
for f0 in visited_f:
    ext = fnof(f0)
    if not ext: continue
    i0 = pos.get(f0, 0)
    for i in range(i0, len(addr)):
        if addr[i] >= ext[1]: break
        if mnem[i] == "mov" and ops[i].strip() in ("edx,0x1c01", "edx,0x1c02", "ebx,0x1c01"):
            print(f"  fn {hex(f0)} d={depth.get(f0)}: {hex(addr[i])}: mov {ops[i]}")

# does any reached fn contain the 0x15ebf-branch head or gate block?
for tgt in (0x15ebf, 0x15fed, 0x16147, 0x161d1):
    ext = fnof(tgt)
    print(f"named {hex(tgt)} inside fn {ext} {'REACHED' if ext and ext[0] in visited_f else 'n/a'}")
