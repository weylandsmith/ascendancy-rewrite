#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t248 S4: locate the MAINTAINED header counter — u16==60 at t1086 AND
u16==102 at t1254 (B=0x1bf4d8 identical across both corpora; member offsets
directly comparable). Feeds t249 (writer hunt)."""
import struct, sys, zipfile, glob, os
sys.path.insert(0, "scripts")
import r1_slot as S
pay = S.load_payload("."); anch = S.anchors_cached(".", pay)

def u16set(path, want):
    mem = zipfile.ZipFile(path).read("Memory")
    B = S.base_of(mem, anch)
    return mem, B, {o for o in range(0, len(mem)-1, 2)
                    if struct.unpack_from("<H", mem, o)[0] == want}

slots = [s for s in sorted(glob.glob("work/r1/playcap/save/*.sav"), key=os.path.getmtime)
         if os.path.getsize(s) > 200000]
memA, BA, s60 = u16set(slots[-1], 60)
memC, BC, s102 = u16set("work/r1/bank-t1254/48.sav", 102)
both = s60 & s102
print(f"B_A={BA:#x} B_C={BC:#x} | u16==60 @1086: {len(s60)} | u16==102 @1254: {len(s102)} | intersection {len(both)}")
OFF = 0x82bb0
for o in sorted(both):
    dsx = o - BC - OFF
    where = "DATA-SEG" if 0 <= dsx < 0x20000 else ("race-blk" if 0x12e1a <= dsx < 0x12e1a+4*0x1ee else "heap/other")
    v_a = struct.unpack_from("<H", memA, o)[0]
    print(f"  {o:#x} dsx={dsx:#x} {where} A={v_a} C={struct.unpack_from('<H', memC, o)[0]}")
    if len(both) > 40:
        break
# also: does the Ghidra-read shape [obj+0xab]+0x8c7 show up? dump the home-planet
# object pointer at data 0x12e1d (race 0) and read +0xab,+0x8c7 in both slots
for label, mem, B in (("t1086", memA, BA), ("t1254", memC, BC)):
    hp = struct.unpack_from("<I", mem, B + OFF + 0x12e1d)[0]
    print(f"{label}: home-planet ptr {hp:#x}")
    if 0 < hp < len(mem):
        w = struct.unpack_from("<I", mem, hp + 0xab)[0] if hp + 0xaf <= len(mem) else 0
        print(f"   [hp+0xab]={w:#x}")
        if 0 < w < len(mem):
            print(f"   u16@w+0x8c7 = {struct.unpack_from('<H', mem, w+0x8c7)[0]}")
