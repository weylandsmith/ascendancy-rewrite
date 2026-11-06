#!/usr/bin/env python3
"""t317: FLEETWND gate datum + widget-field probe (offline, offline saves).

Reads per save (all via zipfile 'Memory' member):
  - FLEETWND magic rec 0xfe7a90 (RAW guest addr, t315 law): [+0x41] slot-id,
    [+0xab] instance block, gate datum GUEST 0x600058 (u8) + 0x600059..c.
  - STATSHIPLST widget fields named by the t317 S1 click-road read:
    +0x8/+0xc/+0x10/+0x14 rect (ebp=X in [+8..+0x10], ebx=Y in [+0xc..+0x14]),
    +0x4f msg-0xc road byte (0x30 => emit road; else btn_hdlr road),
    +0x63 registry target slot (fn 0x33320 edx), +0x10 x1, +0xbf strip width,
    +0x41 own slot-id, +0x63 expectation 95 (t316).
  STATSHIPLST rec located by NAME bytes in the magic-rec window set (t313/t315
  law: magic u32 0x12345678 at rec+0, NAME at rec+0x20, RAW guest addrs).

Usage: r317_gate_probe.py <sav> [<sav> ...]
"""
import re, struct, sys, zipfile

MAGIC = struct.pack("<I", 0x12345678)
FLEETWND_REC = 0xfe7a90
GATE = 0x600058


def probe(path):
    mem = zipfile.ZipFile(path).read("Memory")
    def u8(a):
        return mem[a] if 0 <= a < len(mem) else None
    def u16(a):
        return struct.unpack_from("<H", mem, a)[0] if 0 <= a <= len(mem)-2 else None
    def u32(a):
        return struct.unpack_from("<I", mem, a)[0] if 0 <= a <= len(mem)-4 else None

    gate = u8(GATE)
    datum = mem[GATE+1:GATE+5].hex() if GATE+5 <= len(mem) else "?"
    # FLEETWND rec fields
    f = ""
    if u32(FLEETWND_REC) == 0x12345678:
        name = mem[FLEETWND_REC+0x20:FLEETWND_REC+0x40].split(b"\0")[0].decode("ascii", "replace")
        f = (f"FLEETWND rec ok name={name!r} slot41={u8(FLEETWND_REC+0x41)} "
             f"inst_ab={u32(FLEETWND_REC+0xab):#x} "
             f"rect={u32(FLEETWND_REC+8)},{u32(FLEETWND_REC+0xc)}"
             f",{u32(FLEETWND_REC+0x10)},{u32(FLEETWND_REC+0x14)}")
    else:
        f = "FLEETWND rec MAGIC MISSING"
    # STATSHIPLST rec via magic-rec + NAME census
    lines = []
    for m in re.finditer(re.escape(MAGIC), mem):
        r_ = m.start()
        nm = mem[r_+0x20:r_+0x40].split(b"\0")[0]
        if b"STATSHIPLST" in nm:
            lines.append(f"  STATSHIPLST rec={r_:#x} slot41={u8(r_+0x41)} "
                         f"rect={u16(r_+8)},{u16(r_+0xc)},{u16(r_+0x10)},{u16(r_+0x14)} "
                         f"x1_10={u32(r_+0x10)} bf_28={u16(r_+0xbf)} "
                         f"4f={u8(r_+0x4f):#04x} target63={u16(r_+0x63)}")
    print(f"{path}\n  GATE[0x600058]={gate} datum59..c={datum}  {f}")
    for l in lines or ["  STATSHIPLST rec NOT FOUND"]:
        print(l)


for p in sys.argv[1:]:
    probe(p)
