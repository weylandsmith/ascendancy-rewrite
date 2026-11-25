#!/usr/bin/env python3
"""tPF-3b F7 hypothesis (b) census: every CALL to the line routine 0x5bf71 in
the restored image, with the vertex arithmetic in the 0x40 bytes before it and
whether the site is inside the surface-tile painter 0x3bb19..0x3c335.

A SEPARATE full-boundary pass would be a site whose vertex table is built with
NO shrink arithmetic (compare 0x3bc5b: y+1/x-2/y-1/x+2 = inset; 0x3bd4d:
y+14/x-28/y-14/x+28 = tiny).
"""
import struct, subprocess, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = open(os.path.join(ROOT, "work/ascend_restored.bin"), "rb").read()
TARGET = 0x5BF71
sites = []
for ea in range(0, len(data) - 5):
    if data[ea] != 0xE8:
        continue
    if ea + 5 + struct.unpack_from("<i", data, ea + 1)[0] == TARGET:
        sites.append(ea)
print(f"CALL 0x{TARGET:x} sites: {len(sites)}")
PY = os.path.expanduser("~/tools/revenv/bin/python")
for ea in sites:
    inpaint = "IN-TILE-PAINTER" if 0x3bb19 <= ea <= 0x3c335 else "other"
    out = subprocess.run([PY, os.path.join(ROOT, "scripts/t442_disasm.py"),
                          hex(ea - 0x40), hex(ea + 2)],
                         capture_output=True, text=True).stdout.strip().splitlines()
    # look for shrink arithmetic on the vertex-table offsets
    tbl = [l for l in out if any(f"0x{v:x}]" in l for v in
                                 (0x260, 0x264, 0x278, 0x27c, 0x290, 0x294, 0x2a8, 0x2ac))]
    shrink = [l for l in out if ("inc " in l or "dec " in l or "sub eax," in l
                                 or "add eax," in l) and True]
    print(f"\n=== 0x{ea:x}  [{inpaint}]  table-touching insns {len(tbl)}")
    for l in out[-14:]:
        print("   ", l)
