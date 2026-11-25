#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tPF-3d RAMP-MAP RUNTIME READ (no capture, no debugger).

LAW (tPF-3d F15, docs/re/_wip_tPF3.md): the polygon filler 0x62d15 does
screen := MAP[old] (0x63023/0x63026) with MAP = [ds:0x48c33] + rampidx*0x100 —
a per-ramp-slot 256-entry COLOUR TRANSLATION on the heap. (The tPF-3c guess
"MAP = [0x4850c+0x14]" is REFUTED: ds:0x48520 holds 640, the screen width;
ds:0x4850c is the surface descriptor {bits,0,0,639,479,640,480,'DATA'}.)

Pointer law (CLOSED, docs/re/r1-savestate.md): ds-relative D lives at guest
LINEAR 0x242000 + D; guest linear L lives at Memory-member offset L + H
(H per-run from the BDA signature). Base self-verifies per save via the
639/479/640/480 + 'DATA' signature at ds:0x48518.

METHOD: per banked .sav, decode H, verify the signature, read [ds:0x48c33],
dump the 256-byte tables for ramp slots {0,1,7,8,9,10,13}, hash each, and
report cross-save consistency (a table identical across N saves is candidate
law data; a per-session heap value that varies is a producer-observation
target, not a constant).

EXIT 0 = tables read in >=1 save; 1 = negative everywhere; 2 harness.
"""
import glob, os, struct, sys, zipfile
from collections import Counter

D_BASE = 0x242000
SIG_DIMS = (639, 479, 640, 480)
RAMP = (0, 1, 7, 8, 9, 10, 13)


def bda_h(mem):
    return [h for h in range(0, 0x2000)
            if struct.unpack_from("<H", mem, h + 0x413)[0] == 0x280
            and struct.unpack_from("<H", mem, h + 0x44A)[0] == 80]


def main():
    slots = []
    for d in sys.argv[1:]:
        slots += sorted(glob.glob(os.path.join(d, "*.sav")))
    if not slots:
        print("harness-error: no .sav under", sys.argv[1:])
        return 2
    hashes = {i: Counter() for i in RAMP}
    ok = 0
    for slot in slots:
        try:
            mem = zipfile.ZipFile(slot).read("Memory")
        except Exception as e:
            print(f"{slot}: unreadable ({e})")
            continue
        hs = bda_h(mem)
        if len(hs) != 1:
            print(f"{slot}: H ambiguous {hs}")
            continue
        H = hs[0]
        dims = struct.unpack_from("<4I", mem, D_BASE + 0x48518 + H)
        tag = mem[D_BASE + 0x48528 + H: D_BASE + 0x48528 + H + 4]
        if tuple(dims) != SIG_DIMS or tag != b"DATA":
            print(f"{slot}: signature MISMATCH dims={dims} tag={tag}")
            continue
        base = struct.unpack_from("<I", mem, D_BASE + 0x48c33 + H)[0]
        line = f"{os.path.basename(slot)} base={base:#x}"
        good = 0
        for i in RAMP:
            o = base + i * 0x100 + H
            tab = mem[o:o + 256]
            if len(tab) < 256:
                line += f" idx{i}=SHORT"
                continue
            hashes[i][tab.hex()] += 1
            good += 1
        print(line + f" tables={good}/{len(RAMP)}")
        ok += good
    print(f"TABLES_READ {ok} across {len(slots)} saves")
    for i in RAMP:
        c = hashes[i]
        if not c:
            print(f"idx {i}: no data")
            continue
        top, n = c.most_common(1)[0]
        ident = all(top[k * 2:k * 2 + 2] == bytes([k]).hex() for k in range(256))
        print(f"idx {i}: {len(c)} distinct variants; modal in {n}/{sum(c.values())} saves; identity={ident}")
        if len(c) == 1:
            print(f"  STABLE hex: {top}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
