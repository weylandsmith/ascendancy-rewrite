#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t313 STEP 1b: direct-call census for fn 0x51b68 (imagebase-0 payload).

If fn 0x51b68 is NOT a class slot (t313 scan: zero rebased hits), its callers
must be plain `call rel32` (E8) sites. Payload is the restored imagebase-0
code image (OQ-008: loader model usable for control flow, imagebase 0; obj0
code span [0x14bb0,0x82bb0) @0x1d4000, obj1 [0x82bb0,0x8cc83) @0x242000 —
both are in work/ascend_payload.bin contiguous image). A hit is:
    E8 <rel32>  where  site + 5 + rel32 == 0x51b68   (mod 2^32)
Self-control: census calls to fn 0x51834 (STATUSWND handler; expect callers =
the router/dispatcher indirect only, so maybe 0 direct — note either way).
"""
import struct, sys

data = open("/home/hrethric/projects/ascendancy/work/ascend_payload.bin", "rb").read()
print(f"payload={len(data)} bytes")

LO, END = 0x14bb0, 0x8CC83     # scan span = both obj code ranges (image offsets)

def call_sites(target):
    out = []
    i = LO
    n = len(data)
    while i < min(END, n - 5):
        if data[i] == 0xE8:
            rel = struct.unpack_from("<i", data, i + 1)[0]
            if (i + 5 + rel) & 0xFFFFFFFF == target:
                out.append(i)
        i += 1
    return out

for t, label in ((0x51b68, "TARGET label builder"),
                 (0x51834, "CONTROL STATUSWND handler"),
                 (0x51630, "CONTROL ctor fn"),
                 (0x51b64, "CONTROL fn 0x51b64 (grid slot 9 neighbour)")):
    cs = call_sites(t)
    print(f"{label} {t:#x}: {len(cs)} direct call site(s) {[hex(c) for c in cs]}")
