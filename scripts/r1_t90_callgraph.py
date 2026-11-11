#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t90: AI turn-loop call-graph census over the restored image (W6-A3).

Rebuilds rel32 (E8) call edges over obj0 code [0x14bb0,0x82BB0)
(OQ-011 pointer law), maps call sites to functions_full.tsv entries
(HEX columns — banked t83 trap), and pins the caller-set expectations
that docs/re/aicode.md §1..§4 cite. Exit 0 iff all pinned sets match.
Writes work/t90_callgraph.pkl {edges, rcall, rows} for downstream passes.
Side-effect-free besides the pkl.
"""
import struct, sys, bisect, pickle

ROOT = "/home/hrethric/projects/ascendancy"
IMG = f"{ROOT}/work/ascend_restored.bin"
FUNCS = f"{ROOT}/work/functions_full.tsv"
PKL = f"{ROOT}/work/t90_callgraph.pkl"
CODE_LO, CODE_HI = 0x14BB0, 0x82BB0

# Pinned caller sets (aicode.md t90). Exact site sets.
PINNED = {
    0x3f130: {0x3eade},                      # build selector: queue-empty planets only
    0x3ecb8: {0x3ea75},                      # attitude scorer: per-race decision block
    0x3e6e0: {0x25083, 0x250a5},             # per-race AI: master-turn loop + player row
    0x24f24: {0x55f06},                      # master turn: END-TURN dispatcher only
    0x41260: {0x16eb0, 0x2554f},             # race.cpp cmd exec: turn + one UI-side
}
# Pinned edge-presence (caller_func -> must-call target)
PINNED_EDGES = {
    0x3ea54: {0x3ecb8, 0x3ef2c, 0x44690, 0x3eb88, 0x3f130, 0x40018, 0x43b50, 0x40178, 0x40ec0},
    0x40018: {0x46d3c, 0x7824f},
    0x40178: {0x4aa10, 0x4105c, 0x39894},
    0x46aec: {0x46cac, 0x55a60, 0x78a90, 0x76e08},
}

def main():
    rows = []
    with open(FUNCS) as f:
        for line in f:
            p = line.split()
            if len(p) >= 2 and p[0] != "file_off":
                try:
                    rows.append((int(p[0], 16), int(p[1], 16)))
                except ValueError:
                    pass
    rows.sort()
    starts = [s for s, _ in rows]

    def owner(a):
        i = bisect.bisect_right(starts, a) - 1
        if i >= 0 and a < rows[i][0] + rows[i][1]:
            return rows[i][0]
        return None

    data = open(IMG, "rb").read()
    edges, rcall = {}, {}
    for i in range(CODE_LO, CODE_HI - 5):
        if data[i] == 0xE8:
            off = struct.unpack("<i", data[i + 1:i + 5])[0]
            t = i + 5 + off
            if CODE_LO <= t < CODE_HI:
                cf = owner(i)
                if cf is not None:
                    edges.setdefault(cf, set()).add(t)
                    rcall.setdefault(t, set()).add(i)
    pickle.dump({"edges": edges, "rcall": rcall, "rows": rows}, open(PKL, "wb"))

    rc = 0
    for t, want in PINNED.items():
        got = rcall.get(t, set())
        ok = got == want
        rc |= 0 if ok else 1
        print(f"callers(0x{t:x}) {'OK' if ok else 'MISMATCH'}: {sorted(hex(x) for x in got)}")
    for cf, want in PINNED_EDGES.items():
        got = edges.get(cf, set())
        missing = want - got
        ok = not missing
        rc |= 0 if ok else 1
        print(f"edges(0x{cf:x}) {'OK' if ok else 'MISSING ' + ','.join(hex(x) for x in sorted(missing))}")
    print("T90 CALLGRAPH " + ("OK" if rc == 0 else "FAILED"))
    return rc

if __name__ == "__main__":
    sys.exit(main())
