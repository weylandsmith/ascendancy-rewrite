#!/usr/bin/env python3
"""t421 C3 (fixed base): runtime-verbatim check of the 0x892ac table.

LAW (OQ-011, r1_pointer_law C1): image bytes sit at mem[B + file_offset];
P0 = B - H is the POINTER-decode constant, not the byte base. The first C3
cut wrongly read mem[P0+0x892ac]. Correct probe: mem[B+0x892ac].
Exit 0 iff >=1 slot readable and byte-verbatim vs both file images.
"""
import os, sys, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base
from r1_pointer_law import bda_h

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pay = open(os.path.join(ROOT, "work/ascend_payload.bin"), "rb").read()
res = open(os.path.join(ROOT, "work/ascend_restored.bin"), "rb").read()
assert pay[0x892ac:0x892ac+8] == res[0x892ac:0x892ac+8], "file images disagree"
want = pay[0x892ac:0x892ac+8]
print("want (both file images):", want.hex(' '))
anch = build_anchors(pay)
checked = matched = 0
seen_runs = set()
base = os.path.join(ROOT, "work/r1")
for rt, dirs, fs in os.walk(base):
    if os.path.basename(rt) != "save":
        continue
    run = os.path.dirname(rt)
    if run in seen_runs:
        dirs[:] = []
        continue
    for f in sorted(fs):
        if not f.endswith(".sav"):
            continue
        try:
            mem = zipfile.ZipFile(os.path.join(rt, f)).read("Memory")
        except Exception:
            continue
        hs = bda_h(mem)
        if len(hs) != 1:
            continue
        votes, _ = find_base(mem, anch)
        if not votes:
            continue
        B, _ = votes.most_common(1)[0]
        got = mem[B + 0x892ac: B + 0x892ac + 8]
        checked += 1
        ok = got == want
        matched += ok
        print(f"{os.path.relpath(rt, ROOT)}/{f}: B={B:#x} got={got.hex(' ')} "
              f"{'MATCH' if ok else 'DIFFER'}")
        break  # one slot per run
    seen_runs.add(run)
    dirs[:] = []
print(f"checked {checked} runs, matched {matched}")
sys.exit(0 if matched >= 1 else 1)
