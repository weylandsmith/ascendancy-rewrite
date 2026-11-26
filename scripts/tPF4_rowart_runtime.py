#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tPF-4 PLANLIST ROW-ART RUNTIME READ (no capture, no debugger).

LAW (docs/re/_wip_tPF4.md P4, raw bytes 0x3c84c..0x3c915): the PLANLIST row
shape-id producer writes
    out_shape := WORD[ds:0x6fd80]                      (default for every row)
    out_shape := WORD[ds:0x6fd60 + race*2]  iff item==0x17 (Ship)
and the case bodies blit shape-ids WORD[ds:0x6fd90/0x6fd92/0x6fd94/0x6fd9c].
Those slots live IN the data segment (unlike the 0x48c33 heap pointer), so a
banked save holds the values AS THE GAME SET THEM: this is a cited live-RAM
measurement, not a guess.

Pointer law (CLOSED, docs/re/r1-savestate.md): ds-relative D -> guest LINEAR
0x242000 + D -> Memory-member offset + H. Base self-verifies per save via the
639/479/640/480 + 'DATA' signature at ds:0x48518.

EXIT 0 = slots read in >=1 save; 1 = negative everywhere; 2 harness.
"""
import glob, os, struct, sys, zipfile
from collections import Counter

D_BASE = 0x242000
SIG_DIMS = (639, 479, 640, 480)
# label -> ds offset (WORD slots; the 0x6fd60 race table is 21 u16)
SLOTS = [("shape_default", 0x6fd80), ("row_A", 0x6fd90), ("row_B", 0x6fd92),
         ("row_C", 0x6fd94), ("row_D_loop", 0x6fd9c), ("ship_race_base", 0x6fd60)]


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
    per = {name: Counter() for name, _ in SLOTS}
    ship_rows = Counter()
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
            print(f"{slot}: signature mismatch dims={dims} tag={tag!r}")
            continue
        ok += 1
        vals = []
        for name, off in SLOTS:
            if name == "ship_race_base":
                t = struct.unpack_from("<21H", mem, D_BASE + off + H)
                ship_rows[t] += 1
                vals.append("race21=" + ",".join(str(v) for v in t))
            else:
                v = struct.unpack_from("<H", mem, D_BASE + off + H)[0]
                per[name][v] += 1
                vals.append(f"{name}=0x{v:04x}")
        print(f"{os.path.basename(slot)} H=0x{H:x} " + " ".join(vals))
    print(f"\n== {ok}/{len(slots)} saves decoded ==")
    for name, _ in SLOTS:
        if name == "ship_race_base":
            print(f"  {name:16s} {len(ship_rows)} distinct table(s); "
                  f"top {ship_rows.most_common(2)}")
        else:
            print(f"  {name:16s} {len(per[name])} distinct: {per[name].most_common(6)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
