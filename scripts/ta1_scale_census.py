#!/usr/bin/env python3
"""tA1: census every call site of the affine stretch blitter FUN_0005d5a1.

Blitter head (decompile 0x5d5a1): if (param_8==0x10000 && param_9==0x10000 &&
param_7==0) -> native 1:1 path (0x5caac / 0x5cf96); else the affine path.
cdecl pushes are REVERSED, so at a call site the last three imm32 pushes
before the earlier args are (param_9, param_8, param_7) -- i.e. reading the
push run TOP-DOWN gives p7? NO: top-down push order is p10..p1, so the FIRST
pushes of the run carry the HIGHEST params. The window printed here is raw
disasm; interpret per-site against the ABI note in the header of
docs/re/_wip_t423c3.md C3-F8.

Usage: python3 scripts/ta1_scale_census.py            # list sites
       python3 scripts/ta1_scale_census.py 0x52872     # window one site
"""
import re, re as _re, subprocess, sys

BIN = "work/ascend_restored.bin"
TARGET = 0x5D5A1
data = open(BIN, "rb").read()

sites = []
for m in re.finditer(rb"\xe8(?=....)", data):
    i = m.start()
    rel = int.from_bytes(data[i+1:i+5], "little", signed=True)
    if i + 5 + rel == TARGET:
        sites.append(i)

if len(sys.argv) > 1:
    sites = [int(sys.argv[1], 16)]
else:
    print(f"rel32 call sites of 0x{TARGET:x}: {len(sites)}")
    print(" ".join(hex(s) for s in sites))

for s in sites:
    start = max(0, s - 60)
    out = subprocess.run(
        ["objdump", "-D", "-b", "binary", "-m", "i386",
         f"--start-address={start}", f"--stop-address={s+5}", BIN],
        capture_output=True, text=True).stdout
    body = out.splitlines()
    keep = [l for l in body if re.match(r"^\s*[0-9a-f]+:", l)]
    print(f"\n=== site 0x{s:x} ===")
    for l in keep:
        print(l)
