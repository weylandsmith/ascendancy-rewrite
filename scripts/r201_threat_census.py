#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t201 — corpus census of planet threat bytes sys+0x58 / sys+0x59.

CONVENTION (validated in-script): PLANET_P0 name-anchored stride-123 walk
(r1_record_census law, base phys static across campaigns, per-run member H
via r1_sav_scan.find_base — never hard-coded). System object = name - 0x24
(STATE in-hand law), so sys field X lands at window j + (X - 0x24).
Self-check leg: IND(sys+0x44) max ~77, RES(+0x46) max ~52, PROS(+0x48) max
16 over the corpus (t198 measured) — printed; if the ranges match, the
window is right and the threat-byte census at j+0x34/j+0x35 is trustworthy.
Also census owner(sys+0x57) and gate word(sys+0x1e = j-0x6, printed via
cells/cap sanity instead since j-6 belongs to the previous record's tail —
the table layout makes sys-base fields < 0x24 UNREADABLE this way, so the
gate leg is skipped; threat bytes are >= 0x24, fine).
RC=0 always.
"""
import os, sys, re, struct, zipfile, collections
sys.path.insert(0, "/home/hrethric/projects/ascendancy/scripts")
from r1_sav_scan import build_anchors, find_base

ROOT = "/home/hrethric/projects/ascendancy"
RUN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "work/r1/playcap")
PAY = os.path.join(ROOT, "work/ascend_payload.bin")
PLANET_P0 = 0x26D07B
STRIDE = 123
NAME_RE = rb"[A-Z][A-Za-z]{2,}(?: [IVX]+)?\x00"


def main():
    pay = open(PAY, "rb").read()
    anch = build_anchors(pay)
    agg58 = collections.Counter()
    agg59 = collections.Counter()
    joint = collections.Counter()
    ind_max = res_max = pros_max = 0
    own_c = collections.Counter()
    tot = 0
    for f in sorted(os.listdir(os.path.join(RUN, "save"))):
        if not f.endswith(".sav"):
            continue
        try:
            mem = zipfile.ZipFile(os.path.join(RUN, "save", f)).read("Memory")
        except Exception as e:
            print(f"{f}: {e!r}")
            continue
        votes, _ = find_base(mem, anch)
        if not votes:
            print(f"{f}: base unresolved")
            continue
        H = votes.most_common(1)[0][0] - 0x1BF450
        n = 0
        while True:
            j = PLANET_P0 + n * STRIDE + H
            if j >= len(mem) or mem[j] == 0:
                break
            if not re.match(NAME_RE, mem[j:j + 40]):
                break
            n += 1
        per58 = collections.Counter()
        for k in range(n):
            j = PLANET_P0 + k * STRIDE + H
            ind = struct.unpack_from("<H", mem, j + 0x20)[0]   # sys+0x44
            res = struct.unpack_from("<H", mem, j + 0x22)[0]   # sys+0x46
            pros = struct.unpack_from("<H", mem, j + 0x24)[0]  # sys+0x48
            b58 = mem[j + 0x34]                                # sys+0x58
            b59 = mem[j + 0x35]                                # sys+0x59
            own = mem[j + 0x33]                                # sys+0x57
            ind_max = max(ind_max, ind); res_max = max(res_max, res)
            pros_max = max(pros_max, pros)
            agg58[b58] += 1
            agg59[b59] += 1
            joint[(b58, b59)] += 1
            per58[b58] += 1
            own_c[own] += 1
        tot += n
        print(f"{f}: recs={n} t58={dict(sorted(per58.items()))}")
    print("TOTAL recs:", tot)
    print(f"SELF-CHECK IND max {ind_max} (t198: 77), RES max {res_max} (52), "
          f"PROS max {pros_max} (16)")
    print("sys+0x58 census:", dict(sorted(agg58.items())))
    print("sys+0x59 census:", dict(sorted(agg59.items())))
    print("joint top12:", joint.most_common(12))
    print("owner census:", dict(sorted(own_c.items())))


main()
