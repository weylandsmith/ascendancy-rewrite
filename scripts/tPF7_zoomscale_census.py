#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tPF7_zoomscale_census.py — MEASURE f32[ds:0x9f108] (the reswin/cosmos pump
delta-scale, seam TRSV1b-A) across all banked save states.

LAW (cited):
  * POINTER LAW (OQ-011 CLOSED, STATE.md): ds-relative static D lives at guest
    LINEAR 0x242000 + D; a guest linear L lives at Memory-member offset L + H
    (H per-run, BDA-signature derived).  => member(D) = 0x242000 + D + H.
    Same pattern as scripts/tPF2d_label_registry.py (verified there).
  * f32[0x9f108] consumers: reswin pump 0x47cac (rot +-3deg scale) and 0x47cf4
    (dolly +-1 scale) — docs/re/research.md S8, _wip_tRSV1b; cosmos camera
    delta scale — docs/re/_wip_t416.md F3; debug zoom keys 0x275b0/0x275e4
    MULTIPLY it by a pool const (docs/re/debugflags.md table rows 0x0c/0x0d).
  * Prior readings CONFLICT: _wip_t416 S-d "port documents scale 1.0";
    _wip_tNGS S12 "measured ~0 in bank-41.sav (denormal)". This census
    settles it per-bank.

METHOD: for each .sav under the given dirs, decode H via BDA, read f32 at
member 0x242000+0x9f108+H, also read the neighbours 0x9f100..0x9f118 for
context, classify (0 / denormal / normal float). Print per-dir histogram.
EXIT 0 always (census prints; interpretation is the consumer's job).
"""
import math, os, struct, sys, zipfile

D_BASE = 0x242000
TARGET = 0x9f108

def bda_h(mem):
    return [h for h in range(0, 0x2000)
            if struct.unpack_from("<H", mem, h + 0x413)[0] == 0x280
            and struct.unpack_from("<H", mem, h + 0x44A)[0] == 80]

def classify(f):
    if f == 0.0:
        return "zero"
    if math.isnan(f):
        return "nan"
    if abs(f) < 1e-30:
        return "denormal-ish"
    return "normal"

def main():
    dirs = sys.argv[1:] or ["work/r1"]
    from collections import Counter
    hist = Counter()
    rows = []
    for d in dirs:
        for root, _, files in os.walk(d):
            for fn in sorted(files):
                if not fn.endswith(".sav"):
                    continue
                p = os.path.join(root, fn)
                try:
                    with zipfile.ZipFile(p) as z:
                        names = z.namelist()
                        memname = "Memory" if "Memory" in names else None
                        if memname is None:
                            continue
                        mem = z.read(memname)
                except Exception as e:
                    rows.append((p, "ERR", str(e)[:60]))
                    continue
                hs = bda_h(mem)
                if len(hs) != 1:
                    rows.append((p, "H?", str(hs)))
                    continue
                h = hs[0]
                off = D_BASE + TARGET + h
                if off + 4 > len(mem):
                    rows.append((p, "OOB", ""))
                    continue
                f = struct.unpack_from("<f", mem, off)[0]
                nb = [struct.unpack_from("<f", mem, off - 8 + i * 4)[0]
                      if 0 <= off - 8 + i * 4 + 4 <= len(mem) else None
                      for i in range(7)]
                c = classify(f)
                hist[c] += 1
                rows.append((p, c, f"{f:.6e}", nb))
    nz = [r for r in rows if r[1] == "normal"]
    for r in rows:
        if r[1] != "zero":
            print("  ", r)
    print("HISTOGRAM:", dict(hist))
    print("TOTAL:", len(rows))
    if nz:
        vals = sorted(set(round(r[2], 9) for r in nz))
        print("NORMAL VALUES:", vals[:20])

main()
