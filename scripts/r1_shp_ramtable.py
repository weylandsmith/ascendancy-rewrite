#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t68: runtime blit-table vs file-directory delta census.

For every loaded shape slot in a checkpoint:
  C := PAY + 0x88 (verbatim copy base, S10/S14 law)
  for sel in 0..count-1: val = u32[C+8+8*sel]; entry_rel = val;
  delta(sel) = entry_rel + 0x18 - starts[?]. We do NOT assume which record
  the sel addresses: compute delta against EVERY record start and keep
  only sels whose nearest delta is within +-0x40; print delta histogram
  per library, plus per-sel table for 1starmap family + raceflag.
"""
import zipfile, struct, glob, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_shp_unifiedlaw as U

CK = sys.argv[1] if len(sys.argv) > 1 else \
     "work/r1/r1ad-20261011-180908/ck/ck072.sav"
CACHE = 0x2e1194

raw = zipfile.ZipFile(CK).read("Memory")
files = {}
for p in glob.glob("extracted/**/*.shp", recursive=True) + \
          glob.glob("extracted/**/*.tmp", recursive=True):
    try:
        d, count, te, tsz, starts, ends = U.parse(p)
        files[os.path.basename(p)] = (d, count, te, tsz, starts, ends)
    except Exception:
        pass

for slot in range(200):
    PAY = struct.unpack_from("<I", raw, CACHE + 4 * slot)[0]
    if not (0x10000 < PAY < 0x800000):
        continue
    magic = raw[PAY + 0x88:PAY + 0x8c]
    if magic != b"1.10":
        continue
    # identify file by verbatim content (size + first 64 bytes at copy)
    sz = struct.unpack_from("<I", raw, CACHE + 0x320 + 4 * slot)[0]
    match = None
    head = raw[PAY + 0x88:PAY + 0x88 + 64]
    for nm, (d, count, te, tsz, starts, ends) in files.items():
        if len(d) in (sz, sz - 2, sz + 2) and d[:64] == head:
            match = nm
            break
    if not match:
        continue
    d, count, te, tsz, starts, ends = files[match]
    hist = collections.Counter()
    rows = []
    for sel in range(count):
        val = struct.unpack_from("<I", raw, PAY + 0x88 + 8 + 8 * sel)[0]
        best = min(range(count), key=lambda k: abs(val + 0x18 - starts[k]))
        delta = val + 0x18 - starts[best]
        hist[delta] += 1
        rows.append((sel, val, best, delta))
    print(f"slot {slot} {match} count={count} PAY={hex(PAY)} hist={dict(hist)}")
    if match.startswith("1starmap") or match == "raceflag.shp":
        for r in rows[:12]:
            print("   sel", r)
