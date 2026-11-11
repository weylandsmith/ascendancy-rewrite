#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t316: dump the window registry at obj 0x7a35c (payload off) from a save.

Laws (binding, docs/re/_wip_t316.md S1 + t313/t315):
- fn 0x56ca4 indexes [obj + edx*12 + 4] -> WINDOW magic rec; entry valid iff
  [e+4]!=0; count at [obj+0x3000] (fn 0x56d1c loop bound, max 0x400);
  name string at [e+4]+0x20 (fn 0x56d1c strcmp mode).
- BYTES map to RAM at B+off; POINTER VALUES carry P0 = B-0x88. Data absolutes
  (0x7a35c, 0x9f100) are data-seg relocatable => read at B+off.
- B re-derived: payload code pattern at 0x51834 -> B (r315_handler_scan law).
- Control: FLEETWND magic rec 0xfe7a90 (P0-relative) must appear as a
  registry entry window if FLEETWND is in the registry at all.

Usage: r316_registry_dump.py <sav>
"""
import re, struct, sys, zipfile

SAV = sys.argv[1]
mem = zipfile.ZipFile(SAV).read("Memory")
PAYLOAD = "/home/hrethric/projects/ascendancy/work/ascend_payload.bin"

def u32(a):
    return struct.unpack_from("<I", mem, a)[0]

pl = open(PAYLOAD, "rb").read()
hits = [m.start() for m in re.finditer(re.escape(pl[0x51834:0x51834 + 48]), mem)]
Bs = sorted({h - 0x51834 for h in hits})
print(f"code-pattern hits {[hex(h) for h in hits]} -> B {Bs and [hex(b) for b in Bs]}")
B = Bs[0]
P0 = B - 0x88
print(f"sav={SAV} mem={len(mem)} B={B:#x} P0={P0:#x}")

def name_at(a):
    return mem[a:a + 32].split(b"\0")[0].decode("cp437", "replace")

REG = B + 0x7a35c
count = u32(REG + 0x3000)
print(f"\n== REGISTRY obj reg={REG:#x} count[{REG+0x3000:#x}]={count}")
mode4226 = u32(REG + 0x4226)
print(f"[[obj+0x4226]] = {mode4226:#x} (>>16 = {mode4226 >> 16})")
g = u32(B + 0x9f100)
print(f"global 0x9f100 @ {B+0x9f100:#x} = {g:#x}")

fleet_rec = P0 + 0xfe7a90
entries = []
nvalid = 0
for i in range(min(count if count else 0, 0x400)):
    e = REG + i * 12
    w = u32(e + 4)
    if w == 0:
        continue
    nvalid += 1
    nm = ""
    if B <= w < len(mem) or P0 <= w < len(mem):
        rec = w
        magic = u32(rec) if rec + 4 <= len(mem) else 0
        nm = name_at(rec + 0x20) if magic == 0x12345678 else f"NOTMAGIC({magic:#x})"
    entries.append((i, w, nm, u32(e), u32(e + 8), w == fleet_rec))
print(f"valid entries: {nvalid}")
for i, w, nm, e0, e8, isf in entries:
    flag = " <== FLEETWND" if isf else ""
    print(f"  idx {i:3d} win={w:#08x} name={nm!r} e0={e0:#x} e8={e8:#x}{flag}")

# STATSHIPLST magic rec(s): string scan -> magic-back-walk
print("\n== STATSHIPLST rec + widget field +0x63")
str_hits = [m.start() for m in re.finditer(re.escape(b"STATSHIPLST"), mem)]
print(f"string hits {[hex(h) for h in str_hits]}")
recs = set()
for h in str_hits:
    for back in range(0, 0x40):
        if h - back >= 0 and u32(h - back) == 0x12345678:
            recs.add(h - back)
            break
for r in sorted(recs):
    cp = u32(r + 0xa7)
    print(f"rec {r:#08x} cp={cp:#x} [+0x63]={u32(r+0x63)} [+0xaf]={mem[r+0xaf]} "
          f"[+0xab]={u32(r+0xab):#x} name={name_at(r+0x20)!r}")
    idx = u32(r + 0x63)
    if 0 <= idx < 0x400:
        e = REG + idx * 12
        w = u32(e + 4)
        nm = name_at(w + 0x20) if w and u32(w) == 0x12345678 else "?"
        print(f"   -> registry[{idx}] win={w:#x} name={nm!r} "
              f"{'IS FLEETWND' if w == fleet_rec else ''}")
