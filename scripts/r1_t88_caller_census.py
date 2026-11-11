#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t88: caller census + RNG-constant uniqueness over the restored image.

Static verification for the W6-A3 generic-gun-fire findings (combat.md S2g).
Re-runnable, side-effect-free. Exit 0 iff all expectations hold:
  1. 0x4b740 (hit path) has EXACTLY 6 rel32 callers, the banked set
     {0x1a146 batmode, 0x39d9f AI-ability, 0x3a0b3 item-23 ability,
      0x4bb56 generic-gun shot, 0x4d191 self-destruct, 0x4d2dd dispatcher-tail}
  2. 0x4a360 (shot dispatcher) has EXACTLY 1 caller: 0x49f45
  3. the LCG multiplier 0x41c64e6d appears EXACTLY once in code (at 0x7825b),
     i.e. no second/inline RNG exists to hide a hit roll
  4. no rel32 call into rng {0x78249,0x7824f,0x78273} inside
     [0x4ae24,0x4c790) (the shot-resolution module) and none inside
     [0x4b740,0x4b8e4) (the hit path)
"""
import struct, sys

IMG = "/home/hrethric/projects/ascendancy/work/ascend_restored.bin"
CODE_LO, CODE_HI = 0x14BB0, 0x82BB0   # obj0 code range (OQ-011, CLOSED)

data = open(IMG, "rb").read()

def callers(target):
    res = []
    for i in range(CODE_LO, CODE_HI - 5):
        if data[i] == 0xE8:
            off = struct.unpack("<i", data[i + 1:i + 5])[0]
            if i + 5 + off == target:
                res.append(i)
    return res

fails = 0
def check(name, got, want):
    global fails
    ok = got == want
    print(f"{'OK ' if ok else 'FAIL'} {name}: {got if not isinstance(got,list) else [hex(x) for x in got]}")
    if not ok:
        print(f"     expected: {want if not isinstance(want,list) else [hex(x) for x in want]}")
        fails += 1

want_740 = {0x1A146, 0x39D9F, 0x3A0B3, 0x4BB56, 0x4D191, 0x4D2DD}
got = set(callers(0x4B740))
check("callers(0x4b740)", got, want_740)
check("callers(0x4a360)", set(callers(0x4A360)), {0x49F45})

needle = struct.pack("<I", 0x41C64E6D)
locs = []
i = CODE_LO
while True:
    i = data.find(needle, i, CODE_HI)
    if i < 0:
        break
    locs.append(i)
    i += 1
check("LCG constant embeddings", locs, [0x7825B])

RNG = {0x78249, 0x7824F, 0x78273}
for lo, hi in ((0x4AE24, 0x4C790), (0x4B740, 0x4B8E4), (0x4A360, 0x4A475)):
    inside = [i for i in range(lo, hi - 5)
              if data[i] == 0xE8
              and i + 5 + struct.unpack("<i", data[i + 1:i + 5])[0] in RNG]
    check(f"rng calls in [{hex(lo)},{hex(hi)})", inside, [])

print("T88 CENSUS", "OK" if fails == 0 else f"FAIL x{fails}")
sys.exit(0 if fails == 0 else 1)
