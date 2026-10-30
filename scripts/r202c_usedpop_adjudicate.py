#!/usr/bin/env python3
"""t202c — adjudicate what +0x4c USED-POP actually equals on live records.
Candidates per recalc S6 law (INACTIVE UPOP sum) vs ACTIVE UPOP sum vs
pop - ACTIVE UPOP. Skips item 23 (Ship) and item flags&0x40 and slot
flags&2 per the recalc loop verbatim. RC=0.
"""
import os, sys, re, struct, zipfile
sys.path.insert(0, "/home/hrethric/projects/ascendancy/scripts")
from r1_sav_scan import build_anchors, find_base
ROOT = "/home/hrethric/projects/ascendancy"
P0 = 0x26D07B
RUN = sys.argv[1] if len(sys.argv) > 1 else f"{ROOT}/work/r1/playcap"
for f in sorted(os.listdir(os.path.join(RUN, "save"))):
    if not f.endswith(".sav"):
        continue
    mem = zipfile.ZipFile(os.path.join(RUN, "save", f)).read("Memory")
    anch = build_anchors(open(f"{ROOT}/work/ascend_payload.bin", "rb").read())
    votes, _ = find_base(mem, anch)
    H = votes.most_common(1)[0][0] - 0x1BF450
    B = H + 0x1BF450
    IT = lambda i: B + 0x82bb0 + 0x73e40 + 0x28 * i
    n = 0
    while mem[P0 + n * 123 + H] and re.match(
            rb"[A-Z][A-Za-z]{2,}(?: [IVX]+)?\x00",
            mem[P0 + n * 123 + H:P0 + n * 123 + H + 40]):
        n += 1
    match_act = match_inact = match_pop_minus_act = 0
    tot = 0
    other = []
    ocap = []
    for k in range(n):
        j = P0 + k * 123 + H
        rec = j - 0x24
        cells = struct.unpack_from("<H", mem, rec + 0x18)[0]
        capw = struct.unpack_from("<H", mem, rec + 0x1a)[0]
        if cells not in (7, 11, 23, 45, 73) or capw != cells + 10:
            continue
        pop = struct.unpack_from("<H", mem, rec + 0x42)[0]
        cap = struct.unpack_from("<H", mem, rec + 0x4a)[0]
        used = struct.unpack_from("<H", mem, rec + 0x4c)[0]
        ptr = struct.unpack_from("<I", mem, rec + 0x10)[0]
        if not (0x100000 < ptr < 0x800000):
            continue
        act = inact = 0
        items = []
        for si in range(capw):
            s = ptr + 0x88 + 4 * si
            it = mem[s + 1]
            fl = struct.unpack_from("<H", mem, s + 2)[0]
            if it == 0xff:
                continue
            ia = IT(it)
            items.append((si, it, mem[ia + 3], mem[ia + 4], fl))
            if it == 23 or (mem[ia + 6] & 0x40) or (fl & 2):
                continue
            if fl & 1:
                act += mem[ia + 4]
            else:
                inact += mem[ia + 4]
        tot += 1
        if used == act:
            match_act += 1
        if used == inact:
            match_inact += 1
        if used == max(0, pop - act):
            match_pop_minus_act += 1
        if used not in (act, inact, max(0, pop - act)) and len(other) < 6:
            other.append((k, cap, pop, used, act, inact, items[:12]))
        if used >= cap and len(ocap) < 4:
            nm = mem[j:j + 30].split(b"\x00")[0].decode("ascii", "replace")
            ocap.append((k, nm, mem[rec + 0x57], cap, pop, used, items))
    print(f"{f}: tot={tot} used==actU {match_act} used==inactU {match_inact} "
          f"used==pop-actU {match_pop_minus_act}")
    for o in other:
        print("   OTHER:", o)
    if ocap:
        for o in ocap:
            print("   OVERCAP:", o)
