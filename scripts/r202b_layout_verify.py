#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t202b — layout self-verify for r202_triage_census item/diplo addressing.
Item table member = B+0x82bb0+0x73e40 stride 0x28, name30@+10 (OQ-014).
Print names for rows 0..38; compare against extracted planitem.txt order.
Diplo: print raw bytes at rows 0..7 of image 0x12e16 stride 0x1ee:
[+0] owner candidate, name-looking run at several offsets, [+0x19d].
RC=0.
"""
import os, sys, zipfile
sys.path.insert(0, "/home/hrethric/projects/ascendancy")
from r1_sav_scan import build_anchors, find_base

ROOT = "/home/hrethric/projects/ascendancy"
RUN = os.path.join(ROOT, "work/r1/playcap")
f = "60.sav"
mem = zipfile.ZipFile(os.path.join(RUN, "save", f)).read("Memory")
anch = build_anchors(open(os.path.join(ROOT, "work/ascend_payload.bin"), "rb").read())
votes, _ = find_base(mem, anch)
H = votes.most_common(1)[0][0] - 0x1BF450
B = H - 0x1BF450
print("H", hex(H), "B", hex(B))
base = B + 0x82bb0 + 0x73e40
names = []
for it in range(39):
    ia = base + 0x28 * it
    nm = mem[ia + 10: ia + 40].split(b"\x00")[0]
    mp, up, rq = mem[ia + 3], mem[ia + 4], mem[ia + 5]
    cost = int.from_bytes(mem[ia + 8: ia + 10], "little")
    names.append(nm.decode("ascii", "replace"))
    print(f"item {it:2d} mpop={mp:3d} upop={up:3d} req={rq:3d} cost={cost:5d} {nm[:30]!r}")
# planitem.txt reference order
try:
    pi = open(os.path.join(ROOT, "extracted/ascend00/planitem.txt"), "rb").read()
    ref = [l.split(b",")[0] for l in pi.splitlines() if l and not l.startswith(b"#")]
    ok = sum(1 for a, r in zip(names, ref) if a.encode() == r)
    print(f"planitem.txt name-order match {ok}/{min(39,len(ref))}")
except Exception as e:
    print("planitem.txt:", e)
dip = B + 0x82bb0 + 0x12e16
for r in range(8):
    a = dip + 0x1ee * r
    row = mem[a: a + 0x1ee]
    # find printable runs
    runs = []
    i = 0
    while i < 0x120:
        if 32 <= row[i] < 127:
            j = i
            while j < 0x120 and 32 <= row[j] < 127:
                j += 1
            if j - i >= 4:
                runs.append((i, row[i:j].decode("ascii", "replace")))
            i = j
        else:
            i += 1
    print(f"row {r} byte0={row[0]} ab19d={row[0x19d]} runs={runs[:4]}")
