#!/usr/bin/env python3
"""t313 STEP 1c: name the three class grids at RAM 0x248018/30/48.

t313 scan result: fn 0x51834+P0 hits 0x248050, and the code-decoding walk
finds an 18-slot run 0x248018..0x24805c terminated by garbage 0x3c8efa35.
That is THREE consecutive 6-slot grids (t301/t304 shape slot0 entry/slot1
router 0x30d08/slot2 handler, then slot3, 0x311b8, 0x316f0):
  A base 0x248018 {520a8,30d08,528ec,52160,311b8,316f0}
  B base 0x248030 {51b20,30d08,51cc4,51b64,311b8,316f0}
  C base 0x248048 {51630,30d08,51834,51680,311b8,316f0}   <- t310 'STATUSWND'
t310's 'grid 0x248040 slot 4' was an 8-byte-shifted read of grid C; the true
slot index of 0x51834 is 2 (the handler slot) — the t301/t304 law holds.

This script: dump the header region above the grids, and for every plausible
RAM pointer candidate, scan RAM for refs and name the window (magic
0x12345678 at ref-0xa7, NAME at rec+0x20, per t310 verbatim law).
"""
import re, struct, sys, zipfile

SAV = sys.argv[1]
P0 = 0x1bf450
if "--p0" in sys.argv:
    P0 = int(sys.argv[sys.argv.index("--p0") + 1], 16)
mem = zipfile.ZipFile(SAV).read("Memory")

def u32(a):
    return struct.unpack_from("<I", mem, a)[0]

def refs(val):
    n = struct.pack("<I", val)
    return [m.start() for m in re.finditer(re.escape(n), mem)]

def name_for(val):
    """ref r holds the class ptr at rec+0xa7 -> rec = r-0xa7; magic at rec,
    NAME at rec+0x20 (ships.md +0x08 rect/+0x20 NAME/+0xa7 class law)."""
    out = []
    for r in refs(val):
        rec = r - 0xa7 if r >= 0xa7 else -1
        magic = u32(rec) if rec >= 0 else 0
        if magic == 0x12345678:
            nm = mem[rec + 0x20: rec + 0x20 + 32].split(b"\0")[0].decode("cp437", "replace")
            rect = [u32(rec + 8 + 4 * i) for i in range(4)]
            out.append((hex(r), hex(rec), nm, rect))
    return out

print("header region 0x247F80..0x248018:")
for a in range(0x247F80, 0x248018, 4):
    v = u32(a)
    tag = ""
    if P0 <= v < P0 + 0x8CC83:
        tag = f"-> fn {v - P0:#x}"
    elif 0x240000 <= v < 0x300000:
        tag = "-> RAM ptr"
    print(f"  {a:#08x} {v:#010x} {tag}")

print("\nclass-ptr naming for candidate header values:")
for a in range(0x247F80, 0x248018, 4):
    v = u32(a)
    if not (0x240000 <= v < 0x300000):
        continue
    named = name_for(v)
    nr = refs(v)
    print(f"  hdr {a:#08x} = {v:#x}: {len(nr)} ref(s); magic-named: {named}")

print("\ngrid slot tables (6-slot law, base = first slot):")
GRIDS = {"A": 0x248018, "B": 0x248030, "C": 0x248048}
for k, base in GRIDS.items():
    slots = [u32(base + 4 * i) for i in range(6)]
    print(f"  grid {k} base {base:#x}: " + ", ".join(f"[{i}]{s - P0:#x}" for i, s in enumerate(slots)))
    # the class ptr for a grid: t310 found class ptr 0x247fc0 whose refs named
    # STATUSWND. Check whether any window rec holds (rec+0xa7) == a value that
    # itself points at THIS grid base.
for k, base in GRIDS.items():
    hits = refs(base)
    print(f"  refs to grid base {k} {base:#x}: {[hex(h) for h in hits]}")
    for h in hits:
        magic = u32(h - 0xa7) if h >= 0xa7 else 0
        if magic == 0x12345678:
            nm = mem[h + 0x20: h + 0x20 + 32].split(b"\0")[0].decode("cp437", "replace")
            print(f"    MAGIC-OK window rec {h:#x} NAME={nm!r}")
