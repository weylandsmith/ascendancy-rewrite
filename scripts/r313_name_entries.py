#!/usr/bin/env python3
"""t313 STEP 1d: calibrate the window-rec law on t310's KNOWN STATUSWND rec
(0xfd9fbc, name 'STATUSWND'), then name the owner of class entry 0x247FBC
(grid B = {51b20,30d08,51cc4,51b64,311b8,316f0} — the fn holding the t312
writer pair) and every other class entry in the family.

Calibration first: dump rec 0xfd9fbc region, find where 0x247fc0 (t310's
class ptr value) sits relative to the rec and where magic 0x12345678 sits.
That settles the offset law VERBATIM instead of by inference.
"""
import re, struct, sys, zipfile

SAV = sys.argv[1]
P0 = 0x1bf450
mem = zipfile.ZipFile(SAV).read("Memory")

def u32(a):
    return struct.unpack_from("<I", mem, a)[0]

def refs(val):
    n = struct.pack("<I", val)
    return [m.start() for m in re.finditer(re.escape(n), mem)]

def hexdump(a, n):
    for off in range(0, n, 4):
        v = u32(a + off)
        tag = ""
        if P0 <= v < P0 + 0x8CC83: tag = f"fn {v-P0:#x}"
        elif v == 0x12345678: tag = "*** MAGIC ***"
        elif 0x240000 <= v < 0x300000: tag = "RAM ptr"
        asc = mem[a+off:a+off+4].decode("cp437", "replace").replace("\0", ".")
        print(f"    {a+off:#08x} (+{off:#04x}) {v:#010x} {asc:<6} {tag}")

print("== CALIBRATION: t310 STATUSWND rec candidate 0xfd9fbc region ==")
# find magic near it
mag = 0x12345678
near = [r for r in refs(mag) if 0xfd9000 < r < 0xfdb000]
print("  magic hits 0xfd9000..0xfdb000:", [hex(x) for x in near])
for m in sorted(near):
    print(f"  magic @ {m:#x}: name@+0x20 = {mem[m+0x20:m+0x20+24].split(chr(0).encode())[0].decode('cp437','replace')!r}")
base = min(near) if near else 0xfd9fbc
hexdump(base, 0x120)

print("\n== where does 0x247fc0 (t310 'class ptr') sit relative to magic rec? ==")
for r in refs(0x247fc0):
    print(f"  ref {r:#x}; r-magic = {r-base:#x}; r-0xa7 = {r-0xa7:#x}")

print("\n== class-entry family walk (stride 0x20 from 0x247F9C) ==")
for e in range(0x247F5C, 0x24801C, 0x20):
    v0 = u32(e)
    if P0 <= v0 < P0 + 0x8CC83:
        slots = [u32(e + 4*i) for i in range(6)]
        print(f"  entry {e:#x}: " + ", ".join(f"{s-P0:#x}" for s in slots))

print("\n== name every class entry: refs to each stride-0x18 entry start ==")
# The class ptr stored in windows may be ANY of the stride values; scan refs
# for the three grid-owning entries + the entry right above grid B.
for cp in (0x247f9c, 0x247fbc, 0x247fdc, 0x247ffc, 0x248018, 0x248030, 0x248048):
    rs = refs(cp)
    named = []
    for r in rs:
        # try every plausible rec offset: look for magic within r-0x100..r
        for back in (0xa7, 0x9f, 0xa3, 0xa4, 0xa8, 0x100):
            rec = r - back
            if rec >= 0 and u32(rec) == 0x12345678:
                nm = mem[rec+0x20:rec+0x20+32].split(b"\0")[0].decode("cp437", "replace")
                named.append((hex(r), hex(rec), back, nm))
                break
    print(f"  cp {cp:#x}: {len(rs)} refs; named: {named if named else '—'}")
