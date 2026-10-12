#!/usr/bin/env python3
"""r1_t78_read.py RUN_DIR... — print total-stars T (DAT_00016143 hi-u16)
per save slot via the pointer law (base-of-memory anchor vote >= 5;
member = B + 0x82bb0 + X). Exit 0 if any slot yields a T."""
import os, sys, zipfile, struct, glob
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_sav_scan as SS
from r1_t75_read import base_of

def T_of(d):
    b = base_of(d)
    if not b:
        return None, 0
    off = b + 0x82bb0 + 0x16143
    if off + 4 > len(d):
        return None, b
    return struct.unpack("<I", d[off:off + 4])[0] >> 16, b


found = False
for run in sys.argv[1:]:
    ts = Counter()
    for sp in sorted(glob.glob(os.path.join(run, "save", "*.sav"))):
        try:
            d = zipfile.ZipFile(sp).read("Memory")
        except Exception:
            continue
        if len(d) < 0x90000:
            continue
        t, b = T_of(d)
        if t:
            ts[t] += 1
    print(f"{run}: T votes {dict(ts)}")
    if ts:
        found = True
sys.exit(0 if found else 1)
