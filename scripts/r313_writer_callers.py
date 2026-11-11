#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t313 STEP 1g: callers of the FLEETWND writer fns + slot-3 dispatch route.

Block map (r313_fleetwnd_map.py) shows fn boundaries: writer store 0x51fc2 is
inside fn [0x51f3b..0x51fb4], store 0x52003 inside fn [0x51ff6..0x52036].
Census: (1) E8 direct calls to 0x51f3b / 0x51ff6 / 0x51b64 whole image;
(2) indirect call [reg+0x94] (slot 3 via cp+0x88 base) anywhere;
(3) u32 refs to 0x51f3b/0x51ff6 rebased in the sav (are they table members?).
"""
import re, struct, sys, zipfile

data = open("/home/hrethric/projects/ascendancy/work/ascend_payload.bin", "rb").read()
P0 = 0x1bf450
SAV = "/home/hrethric/projects/ascendancy/work/r1/t299-leg-20261105-192246/save/58.sav"
mem = zipfile.ZipFile(SAV).read("Memory")

def e8_callers(target):
    out = []
    i = 0x14bb0
    n = min(0x8CC83, len(data))
    while i < n - 5:
        if data[i] == 0xE8:
            rel = struct.unpack_from("<i", data, i + 1)[0]
            if (i + 5 + rel) & 0xFFFFFFFF == target:
                out.append(i)
        i += 1
    return out

for t in (0x51f3b, 0x51ff6, 0x51b64, 0x51cc4):
    cs = e8_callers(t)
    print(f"E8 callers of {t:#x}: {[hex(c) for c in cs]}")

print("\nindirect call [reg+disp32] with disp in {0x88,0x8c,0x90,0x94} (vtable slots via cp):")
# ff /2 = call far-form opcode ff 90..97 disp32; capture disp
pat = re.compile(rb"\xff[\x90-\x97](....)", re.S)
seen = {}
for m in pat.finditer(data):
    disp = struct.unpack("<I", m.group(1))[0]
    if disp in (0x88, 0x8c, 0x90, 0x94, 0x98):
        seen.setdefault(disp, []).append(m.start())
for d, hits in sorted(seen.items()):
    print(f"  disp {d:#x}: {len(hits)} site(s) {[hex(h) for h in hits[:12]]}")

print("\nsav u32 refs (rebased) to writer fns — table membership:")
for v in (0x51f3b, 0x51ff6):
    n = struct.pack("<I", v + P0)
    hits = [m.start() for m in re.finditer(re.escape(n), mem)]
    print(f"  {v:#x}+P0 = {v+P0:#x}: {[hex(h) for h in hits]}")
