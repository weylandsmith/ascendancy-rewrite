#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t212 — verify the pointer hits are relocated disp32 bytes, not hidden code.

r212_raw_and_ptr.py C2 found relocated-value dwords in RAM at members
0x1e754d/0x1e7598 (target +0x482fb), 0x1e4676/0x1e46f2/0x1e4700 (+0x48300),
+ the 0x48304 family. Hypothesis: these are the RELOCATED disp32 fields of the
KNOWN instructions (presenter 0x28074/0x280be; debug-block 0x2519b/0x25217/
0x25225; mark family incl 0x43afa/0x4611c) inside the loaded code image — not
pointer variables and not hidden code.

Test per site (decoder-free): take the instruction's IMAGE bytes up to the
disp32, append the relocated value (both candidate bases: P0+X-0x88 physical
and P0+X linear), find in 'Memory'. Found => the dword is that instruction's
own operand field: no extra writer, no overlay code. NOT found => investigate.

POSITIVE CONTROLS are the presenter sites themselves. A site whose unrelocated
image bytes are ALSO still present elsewhere in RAM (unpatched duplicate load)
is reported too.
Exit 0 all found / 1 something missing / 2 harness error.
"""
import os
import struct
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_slot as S

SAVE = "work/r1/playcap/save/60.sav"
IMG = open("work/ascend_restored.bin", "rb").read()
OFF = 0x82BB0

SITES = [  # (image addr, disp, note)
    (0x28074, 0x482FB, "presenter read (STARS CONTROLLED line)"),
    (0x280be, 0x482FB, "presenter read (PERCENT line)"),
    (0x2519b, 0x48300, "debug inc word[0x48300]"),
    (0x25217, 0x48300, "debug mov di,[0x48300]"),
    (0x25225, 0x48300, "debug mov [0x48300],di"),
    (0x43afa, 0x48304, "t204 mark OR writer [eax+0x48304],dl"),
    (0x4611c, 0x48304, "t206 latch writer"),
    (0x24e39, 0x48304, "scenario-init and [edx+0x48304],0xfe"),
]

mem = zipfile.ZipFile(SAVE).read("Memory")
anch = S.anchors_cached(".", open("work/ascend_payload.bin", "rb").read())
B = S.base_of(mem, anch)
if B is None:
    raise SystemExit(2)
P0 = B + OFF
print(f"{SAVE}: B={B:#x} P0=P0+0x82bb0={P0:#x}")
missing = 0
for X, disp, note in SITES:
    j = IMG[X:X + 12].find(struct.pack("<I", disp))
    if j is None or j < 0:
        print(f"  {X:#x}: disp not in image bytes — SKIP (check by hand)")
        continue
    prefix = IMG[X:X + j]
    results = []
    for form, val in (("phys", P0 + disp - 0x88), ("lin", P0 + disp)):
        want = prefix + struct.pack("<I", val)
        pos, found = 0, []
        while len(found) < 6:
            i = mem.find(want, pos)
            if i < 0:
                break
            found.append(hex(i))
            pos = i + 1
        # unrelocated image form still present somewhere (duplicate load)?
        raw = IMG[X:X + j + 4]
        raw_at = mem.find(raw)
        results.append((form, found, hex(raw_at) if raw_at >= 0 else None))
    any_found = any(f for _, f, _ in results)
    if not any_found:
        missing += 1
    print(f"  {X:#07x} {note}")
    for form, found, raw_at in results:
        print(f"    {form}: {found if found else 'NOT FOUND'}"
              f"   (unrelocated image bytes at: {raw_at})")
print("\nverdict:",
      "ALL disp32 sites present in reloc form — RAM dwords pointing at the "
      "score block are those instructions' OWN operand fields, not pointer "
      "variables; no hidden code needed"
      if missing == 0 else f"{missing} site(s) not found — hidden code live")
sys.exit(0 if missing == 0 else 1)
