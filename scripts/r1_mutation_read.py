#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r1_mutation_read.py — t53 STEP 1 offline reader (OQ-003).

Records are NAME-RELATIVE (layout law measured t53 on the scratch file:
chain 0xaae2 stride 123, name at +0x00). In RAM we locate the table by the
injected needle HERMESSEN, then for each injected u16:
  LOADED    live == sentinel        (field blob preserved into RAM verbatim)
  REWRITTEN live != sentinel        (loader recomputed/parsed this field —
                                     proves the field is LIVE state, not static file data)
Stray sentinel hits OUTSIDE the injected records = copied/derived elsewhere.
Exit 0 if the table was found in at least one slot.
Usage: r1_mutation_read.py <run-dir> [needle-count-min]
"""
import os, struct, sys, zipfile

REC = 123
INJ = {1: 0xBEEF, 2: 0xCAFE}
OFFS = (0x0e, 0x20, 0x4a, 0x55)
NEEDLE = b"HERMESSEN"

def main():
    run = sys.argv[1]
    savedir = os.path.join(run, "save")
    files = sorted((f for f in os.listdir(savedir) if f.endswith(".sav")),
                   key=lambda f: int(f[:-4]))
    found_any = False
    for f in files:
        mem = zipfile.ZipFile(os.path.join(savedir, f)).read("Memory")
        pos = mem.find(NEEDLE)
        n = mem.count(NEEDLE)
        if pos < 0:
            print(f, "needle absent (not yet loaded / pre-click slot)")
            continue
        found_any = True
        base = pos  # rec0 start (needle is at name +0x00)
        line = []
        for ri, tag in INJ.items():
            for off in OFFS:
                v = struct.unpack_from("<H", mem, base + REC * ri + off)[0]
                mark = "L" if v == tag else "W"
                line.append(f"r{ri}+0x{off:02x}={v:04x}{mark}")
        print(f, "needle x", n, "rec0@", hex(base),
              "rec1 name", mem[base + REC:base + REC + 20].split(b"\x00")[0].decode("cp437", "replace"))
        print("   ", " ".join(line))
        for tag in set(INJ.values()):
            pat = struct.pack("<H", tag)
            hits, p = [], 0
            while True:
                q = mem.find(pat, p)
                if q < 0: break
                hits.append(q); p = q + 1
            inside = [h for h in hits
                      if any(base + REC * ri <= h < base + REC * (ri + 1) for ri in INJ)]
            print(f"    {hex(tag)}: {len(hits)} total; {len(inside)} inside; outside:",
                  [hex(h) for h in hits if h not in inside][:10])
    if not found_any:
        print("VERDICT: needle never in RAM — resume load NOT proven (negative)")
        sys.exit(1)
    print("VERDICT: table located; L=verbatim W=rewritten per-field above")

if __name__ == "__main__":
    main()
