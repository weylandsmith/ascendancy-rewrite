#!/usr/bin/env python3
"""t313 STEP 1e: name the class of grid B {51b20,30d08,51cc4,51b64,311b8,316f0}.

Calibrated laws (this session, on run 192246 58.sav):
  - window rec: magic 0x12345678 at rec+0x00, NAME at rec+0x20, CLASS PTR at
    rec+0xa7 (VERIFIED: ref 0xfda063 to 0x247fc0 == STATUSWND rec 0xfd9fbc
    +0xa7).
  - class ptr -> vtable tail at cp+0x88/+0x8c/+0x90 = (entry, router 0x30d08,
    handler) — VERIFIED for STATUSWND: cp 0x247fc0 -> 0x248048 {51630,30d08,
    51834} = grid C. So grid B's cp = 0x248030-0x88 = 0x247fa8, grid A's cp =
    0x247f90.
Methods: (1) refs to cp named by rec-0xa7; (2) full window census: every magic
rec in RAM -> group by +0xa7 class ptr; (3) constructor imm: disasm fn 0x51b20
for `mov [reg+0xa7], imm32` (t310 route for STATUSWND: fn 0x51630 imm 0x5fc0).
"""
import re, struct, sys, zipfile
from collections import defaultdict

SAV = sys.argv[1]
P0 = 0x1bf450
mem = zipfile.ZipFile(SAV).read("Memory")

def u32(a):
    return struct.unpack_from("<I", mem, a)[0]

def refs(val):
    n = struct.pack("<I", val)
    return [m.start() for m in re.finditer(re.escape(n), mem)]

print("== method 1: refs to candidate class ptrs, named at rec=ref-0xa7 ==")
for cp, tag in ((0x247f90, "grid A cp"), (0x247fa8, "grid B cp"),
                (0x247fc0, "STATUSWND cp (control)")):
    named = []
    for r in refs(cp):
        rec = r - 0xa7
        if rec >= 0 and u32(rec) == 0x12345678:
            nm = mem[rec+0x20:rec+0x20+32].split(b"\0")[0].decode("cp437", "replace")
            named.append((hex(r), hex(rec), nm))
    print(f"  {tag} cp {cp:#x}: named {named}")

print("\n== method 2: full window census grouped by class ptr (+0xa7) ==")
groups = defaultdict(list)
nrec = 0
for m in re.finditer(re.escape(struct.pack("<I", 0x12345678)), mem):
    rec = m.start()
    nm = mem[rec+0x20:rec+0x20+32].split(b"\0")[0].decode("cp437", "replace")
    if not (2 <= len(nm) <= 24) or not all(32 <= ord(c) < 127 for c in nm):
        continue
    cp = u32(rec + 0xa7) if rec + 0xab < len(mem) else 0
    groups[cp].append((hex(rec), nm))
    nrec += 1
print(f"  {nrec} magic+name recs, {len(groups)} distinct class ptrs")
for cp, ws in sorted(groups.items()):
    tail = ""
    if P0 <= cp < P0 + 0x8CC83 + 0x100000:  # RAM-side cps
        try:
            v = [u32(cp + o) for cp2 in [cp] for o in (0x88, 0x8c, 0x90)]
            if all(P0 <= x < P0 + 0x8CC83 for x in v):
                tail = "  vtable tail " + ", ".join(f"{x-P0:#x}" for x in v)
        except Exception:
            pass
    names = sorted({w[1] for w in ws})
    print(f"  cp {cp:#08x}: {len(ws)} win {names[:6]}{'...' if len(names)>6 else ''}{tail}")

print("\n== the three family grids, for eyeball match ==")
for base, tag in ((0x248018, "A"), (0x248030, "B"), (0x248048, "C/STATUSWND")):
    slots = [u32(base + 4*i) for i in range(6)]
    print(f"  {tag}: " + ", ".join(f"{s-P0:#x}" for s in slots))
