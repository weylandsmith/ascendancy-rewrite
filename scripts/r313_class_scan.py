#!/usr/bin/env python3
"""t313 STEP 1: offline class-grid RAM scan for fn 0x51b68's rebased value.

Route (t310 S5 law, binding): class tables exist ONLY in guest RAM (file-image
scan is structurally blind). Scan the sav 'Memory' member (member offset ==
guest linear address) for u32 == 0x51b68 + P0. Control: 0x51834 + P0 must hit
exactly 1 (RAM 0x248050, t310). For every hit: dump the containing slot grid
(walk both directions while values decode as code-range fns), record slot
index, then for the grid BASE walk backwards to find the class-object header
and scan RAM for refs to the class ptr -> window rec (magic 0x12345678 at
rec-0xa7 per t310 verbatim; NAME at rec+0x20).

Usage: r313_class_scan.py <sav> [--p0 HEX]
"""
import re, struct, sys, zipfile, collections

SAV = sys.argv[1]
P0 = 0x1bf450
if "--p0" in sys.argv:
    P0 = int(sys.argv[sys.argv.index("--p0") + 1], 16)

mem = zipfile.ZipFile(SAV).read("Memory")
CODE_END = P0 + 0x8CC83          # obj1 image end (pointer law OQ-011)
print(f"sav={SAV} mem={len(mem)} P0={P0:#x} code=[{P0:#x},{CODE_END:#x})")

def u32(a):
    return struct.unpack_from("<I", mem, a)[0]

def is_code(v):
    return P0 <= v < CODE_END and (v & 1) == 0

def scan(val):
    n = struct.pack("<I", val)
    return [m.start() for m in re.finditer(re.escape(n), mem)]

def grid_of(addr):
    """Walk both directions from a slot hit while u32s decode as code fns."""
    lo = addr
    while lo - 4 >= 0 and is_code(u32(lo - 4)):
        lo -= 4
    hi = addr
    while hi + 4 + 4 <= len(mem) and is_code(u32(hi + 4)):
        hi += 4
    return lo, hi  # inclusive slot range

def report(val, label):
    hits = scan(val)
    print(f"\n== {label}: value {val:#x} -> {len(hits)} hit(s) {[hex(h) for h in hits]}")
    for h in hits:
        lo, hi = grid_of(h)
        nslots = (hi - lo) // 4 + 1
        slot = (h - lo) // 4
        print(f"  hit {h:#08x}: grid base {lo:#08x} nslots={nslots} slot_index={slot}")
        for i in range(nslots):
            v = u32(lo + 4 * i)
            print(f"    slot[{i}] {v:#08x} -> fn {v - P0:#x}")
        term = u32(hi + 4) if hi + 8 <= len(mem) else None
        print(f"    terminator after grid: {term:#010x}" if term is not None else "")
    return hits, (lo if hits else None)

# --- controls + target -------------------------------------------------
ctl_hits, statuswnd_grid = report(0x51834 + P0, "CONTROL fn 0x51834 (expect 1 @0x248050)")
btn = report(0x32ecf + P0, "CONTROL btn_hdlr 0x32ecf (t310: 4 hits)")
tgt_hits, tgt_grid = report(0x51b68 + P0, "TARGET fn 0x51b68 (label builder)")

# --- class-object header for the target grid ---------------------------
# t310: class ptr 0x247FC0 for STATUSWND grid base 0x248040 => header at
# grid_base - 0x80. Check the same delta for the target grid, then name it.
def name_class(classptr, tag):
    n = struct.pack("<I", classptr)
    refs = [m.start() for m in re.finditer(re.escape(n), mem)]
    print(f"\n== {tag}: refs to class ptr {classptr:#x}: {[hex(r) for r in refs]}")
    for r in refs:
        magic = u32(r - 0xa7) if r >= 0xa7 else None
        rec = r  # candidate window rec
        name = None
        if magic == 0x12345678:
            raw = mem[rec + 0x20: rec + 0x20 + 32]
            name = raw.split(b"\0")[0].decode("cp437", "replace")
            print(f"  ref {r:#08x} MAGIC-OK window rec, NAME={name!r}")
        else:
            print(f"  ref {r:#08x} magic@-0xa7={magic:#x} (code-imm or other)")

if tgt_hits:
    h = tgt_hits[0]
    lo, hi = grid_of(h)
    for delta in (0x80, 0x84, 0x40, 0x7c):
        cp = u32(lo - delta)
        print(f"\nheader probe grid_base-{delta:#x} = {cp:#x}",
              "(plausible class-ptr RAM)" if 0x240000 <= cp < 0x260000 else "")
        if 0x240000 <= cp < 0x260000:
            name_class(cp, f"target grid base-{delta:#x}")
else:
    print("\nTARGET ZERO HITS — bank negative, check P0 via controls first.")
