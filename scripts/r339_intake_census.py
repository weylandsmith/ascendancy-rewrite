#!/usr/bin/env python3
"""t339 — static intake decode helper over work/r331_disasm.txt.

Parses the whole-image objdump once, then answers:
  1. every `call 0x56ca4` (POST-TO-HANDLE) site with a backward edx provenance
     window (last edx assignment before the call: imm / reg / memory).
  2. every `call 0x56ad4` (RING-A poster) site with ebx (param) provenance.
  3. all sites loading immediates in the 0x324..0x335 band (state-16-family
     SENDMESSAGE values 804..813 etc.) anywhere in the image.
  4. stores to record fields +0x63 and reads of +0x63 (partner-slot road).
Exit 0 always (census tool, not a gate)."""
import re, sys, collections

PATH = "work/r331_disasm.txt"
INSN = re.compile(r"^\s+([0-9a-f]+):\s*((?:[0-9a-f]{2}[ ]?)+)\s+(.*)$")

addr = []      # int addresses
mnem = []      # mnemonic first token
ops  = []      # rest
idx  = {}      # addr -> position

with open(PATH, "r", errors="replace") as f:
    for line in f:
        m = INSN.match(line)
        if not m:
            continue
        a = int(m.group(1), 16)
        text = m.group(3).split("#")[0].strip()
        parts = text.split(None, 1)
        addr.append(a); mnem.append(parts[0] if parts else "")
        ops.append(parts[1] if len(parts) > 1 else "")
        idx[a] = len(addr) - 1

N = len(addr)
print(f"parsed {N} insns, span {hex(addr[0])}..{hex(addr[-1])}")

def edx_prov(pos, depth=6):
    """walk backward from pos for the last writer of edx (crude, no flow)."""
    out = []
    lo = max(0, pos - depth)
    for i in range(pos - 1, lo - 1, -1):
        o = ops[i]; m_ = mnem[i]
        if m_ in ("push", "pop", "call", "ret", "ret", "jmp", "jcc") and m_ != "push":
            # call clobbers; keep walking but note
            if m_ in ("call", "ret", "jmp", "jcc"):
                out.append(f"({m_})")
                continue
        dst = o.split(",")[0].strip() if o else ""
        if dst == "edx" or dst == "dx" or dst == "r16:edx":
            out.append(f"{hex(addr[i])}: {m_} {o}")
            if m_.startswith("mov") or m_.startswith("xor") or m_ == "cmov":
                return " | ".join(reversed(out))
        if m_ == "xor" and "edx" in o:
            out.append(f"{hex(addr[i])}: {m_} {o}")
            return " | ".join(reversed(out))
    return " | ".join(reversed(out)) or "(none within window)"

def ebx_prov(pos, depth=6):
    out = []
    lo = max(0, pos - depth)
    for i in range(pos - 1, lo - 1, -1):
        o = ops[i]; m_ = mnem[i]
        if m_ in ("call", "ret", "jmp", "jcc"):
            out.append(f"({m_})"); continue
        dst = o.split(",")[0].strip() if o else ""
        if dst == "ebx":
            out.append(f"{hex(addr[i])}: {m_} {o}")
            if m_.startswith("mov") or m_.startswith("xor"):
                return " | ".join(reversed(out))
        if m_ == "xor" and "ebx" in o:
            out.append(f"{hex(addr[i])}: {m_} {o}")
            return " | ".join(reversed(out))
    return " | ".join(reversed(out)) or "(none within window)"

# ---- 1. POST-TO-HANDLE 0x56ca4 call sites
print("\n== call 0x56ca4 (POST-TO-HANDLE) sites ==")
c = 0
for p, m_ in enumerate(mnem):
    if m_ == "call" and ops[p].strip() == "0x56ca4":
        c += 1
        print(f"  {hex(addr[p])}: edx<- {edx_prov(p)}")
print(f"total {c}")

# ---- 2. RING-A poster 0x56ad4 sites (param in ebx? verify at callee; report ebx+edx)
print("\n== call 0x56ad4 (RING-A poster) sites (ebx=param law t337) ==")
c = 0
for p, m_ in enumerate(mnem):
    if m_ == "call" and ops[p].strip() == "0x56ad4":
        c += 1
        print(f"  {hex(addr[p])}: ebx<- {ebx_prov(p)}  edx<- {edx_prov(p, depth=3)}")
print(f"total {c}")

# ---- 3. immediates 0x324..0x335 (804..821)
print("\n== immediates 0x324..0x335 (state-16 SENDMESSAGE band 804..821) ==")
band = set(range(0x324, 0x336))
hits = []
immre = re.compile(r"0x(3[23][0-9a-f])\b")
for p in range(N):
    m_ = immre.search(ops[p])
    if m_ and int(m_.group(1), 16) in band:
        hits.append((addr[p], mnem[p], ops[p]))
for a, m_, o in hits:
    print(f"  {hex(a)}: {m_} {o}")
print(f"total {len(hits)}")

# ---- 4. +0x63 traffic
print("\n== reads/stores of [reg+0x63] (partner-slot road) ==")
p63 = re.compile(r"\[(e[a-d]x|ebp|esi|edi)\+0x63\]")
reads = collections.Counter(); writes = []
for p in range(N):
    m_ = p63.search(ops[p])
    if not m_:
        continue
    if mnem[p].startswith("mov") and ops[p].split(",")[0].strip().endswith("+0x63]"):
        writes.append((addr[p], mnem[p], ops[p]))
    else:
        reads[(addr[p], mnem[p], ops[p])] += 1
print("STORES to +0x63:")
for a, m_, o in writes:
    print(f"  {hex(a)}: {m_} {o}")
print(f"READS of +0x63: {sum(reads.values())} sites-context, distinct:")
for (a, m_, o), _ in sorted(reads.items()):
    print(f"  {hex(a)}: {m_} {o}")

sys.exit(0)
