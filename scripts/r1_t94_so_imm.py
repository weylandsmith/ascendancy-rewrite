#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t94 helper 2: find code that references the SO order-name table via the
POOL-RELATIVE immediate law (imm = str_off - 0x82BB0; block base 0x88e60 ->
0x62b0). Individual names sit at base+20*k, so also flag sites whose window
contains an imul/imul-style *0x14 or lea base+20 pattern, plus every code
immediate in [0x62b0..0x6350] step 20 (the 8 pool-rel name imms)."""
import struct, subprocess, sys, os, bisect

ROOT = "/home/hrethric/projects/ascendancy"
IMG = os.path.join(ROOT, "work/ascend_restored.bin")
FUNCS = os.path.join(ROOT, "work/functions_full.tsv")
CODE = (0x14bb0, 0x82bb0)
NAMES = ['SONothing', 'SOGoStar', 'SOColonize', 'SOOrbitPlanet', 'SOPatrol',
         'SODefendPlanet', 'SOAttack', 'SOGoSpace']

data = open(IMG, 'rb').read()

def load_funcs():
    addrs, names = [], {}
    with open(FUNCS) as f:
        f.readline()
        for ln in f:
            p = ln.rstrip("\n").split("\t")
            try:
                a = int(p[0], 16)
            except Exception:
                continue
            addrs.append(a); names[a] = p[1] if len(p) > 1 else "?"
    addrs.sort()
    return addrs, names

def containing(a, addrs, names):
    i = bisect.bisect_right(addrs, a) - 1
    return names[addrs[i]] if i >= 0 else None

addrs, fnames = load_funcs()

print("== pool-rel name imm sites (b3 0x62b0 + 20k, k=0..7) ==")
for k, nm in enumerate(NAMES):
    v = (0x88e60 + 20 * k - 0x82bb0)
    pat = v.to_bytes(4, 'little')
    hits = []
    i = CODE[0]
    while True:
        j = data.find(pat, i)
        if j < 0 or j >= CODE[1]:
            break
        hits.append(j); i = j + 1
    print(f"k={k} {nm:14s} imm 0x{v:x}: " + ", ".join(f"0x{h:x}[{containing(h,addrs,fnames)}]" for h in hits))

print("\n== imul 0x14 (69/6B 03..07 14) sites in code ==")
for rm in range(8):
    for op in (0x69, 0x6B):
        if op == 0x6B and rm == 4:
            continue
        pat = bytes([op, 0xC0 | (rm << 3) | rm, 0x14]) if False else None
# generic: find 0x69 /r imm8=0x14 and 0x6B /r imm8=0x14 over all reg pairs
hits = []
for op in (0x69, 0x6B):
    for reg in range(8):
        for rm in range(8):
            pat = bytes([op, 0xC0 | (reg << 3) | rm, 0x14])
            i = CODE[0]
            while True:
                j = data.find(pat, i)
                if j < 0 or j >= CODE[1]:
                    break
                hits.append(j); i = j + 1
for h in sorted(set(hits)):
    # disasm window +-16 to see context
    lo = (h - 24) & ~0xF
    r = subprocess.run(["objdump", "-b", "binary", "-D", "-m", "i386", "-M", "intel",
                        f"--start-address=0x{lo:x}", f"--stop-address=0x{h+24:x}", IMG],
                       capture_output=True, text=True)
    tail = [ln for ln in r.stdout.splitlines() if ":" in ln][:80]
    print(f"--- 0x{h:x} [{containing(h,addrs,fnames)}]")
    for ln in tail[-8:]:
        print("   ", ln.strip())
