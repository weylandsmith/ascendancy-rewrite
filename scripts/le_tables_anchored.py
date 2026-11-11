#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""le_tables_anchored.py — parse the LE object/page/fixup tables using ONLY
offsets measured by scripts/le_header_dump.py on this exact file, and
cross-validate against runtime measurements (slot 46, 2026-10-05).

HEADER FACTS (le_header_dump.py 2026-10-05, values FROM LE sig):
  +0x10=0x200(512) +0x14=121 +0x18=1 +0x1c=0x63774(cbFixup) +0x20=2
  +0x24=0xa7710(cbImage) +0x28=0x1000(PageSize) +0x2c=211(=+0x14*2-31? NO:242?
  recheck) -> 211=0xd3  +0x30=0x14794  +0x38=0x149b1  +0x40=196
  +0x44=2  +0x48=244  +0x50=728  +0x58=728  +0x5c=736  +0x68=737  +0x6c=1225
  +0x70=0x14a74  +0x78=0x14a74   (all FILE offsets if the canonical map holds)
RUNTIME FACTS (r1_live_probe.py/r1_pointer_measure.py, slot 46):
  live code linear base L0 = 0x1d4000 (code bytes there; NOP pad before a
  56 57 55 push triple = a linked module start);
  code/data transition ~0x241800..0x242000; BSS zero-run starts ~0x24a948;
  pointer clusters: targets [0x1d4000,0x24177c] and [0x242000,0x2e48e2].

TESTS
  V1 object table at the +0x2c value (0xd3) AND at +0x30/+0x38 values:
     entry-size sweep 16/20/24/28; require monotone non-overlapping
     [memory, memory+size), first object size ~ code span (0x6E000 measured
     gap), SUM of sizes == cbImage 0xa7710 EXACT, second object memory ==
     0x242000 (runtime-measured data linear base) for at least one map.
  V2 page-table stride run of 121: locate it empirically from LE onward at
     stride +0x100 low-byte-flags (loader.md said file 0x2b40 — re-measure).
  V3 fixup walk from the fixup-region start (smallest table offset above the
     code copy end): LE init-record grammar 8-byte headers (recType, srcObj,
     dstObj:u16, cbSrc:u16, cbRec:24) terminating at recType 0; compare fixup
     byte span with cbFixup=0x63774 and count of fixups with 31,514 (the
     disp-only operand count recorded in docs/STATE.md 2026-10-05h).
Exit 0: one object-table parse passes V1 fully. 1: none (record negatives).
"""
import argparse, os, struct, sys, zipfile, collections

EXE = "game/ascend.exe"

def u32(d, o): return struct.unpack_from("<I", d, o)[0]
def u16(d, o): return struct.unpack_from("<H", d, o)[0]

def try_objtab(d, at, n, eb):
    ents = []
    if at + n * eb > len(d): return None
    prev_end = -1
    for i in range(n):
        o = at + i * eb
        mem = u32(d, o); cb = u32(d, o + 4)
        if cb > 0x400000 or mem > 0x80000000: return None
        if mem < prev_end: return None
        prev_end = mem + cb
        ents.append((mem, cb, o))
    return ents

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default="work/r1/r1sav-20261005-160721/save/46.sav")
    args = ap.parse_args()
    d = open(EXE, "rb").read()
    le = u32(d, 0x3C)
    cbImage = u32(d, le + 0x24)
    print(f"file={len(d):#x} le={le:#x} cbImage={cbImage:#x} PageSize={u32(d,le+0x28):#x} "
          f"cbFixup={u32(d,le+0x1c):#x} cPage={u32(d,le+0x14)}")

    # V1 -----------------------------------------------------------------
    found = None
    for fld in (0x2c, 0x30, 0x38, 0x50, 0x58):
        off = u32(d, le + fld)
        for eb in (16, 20, 24, 28):
            ents = try_objtab(d, off, 121, eb)
            if not ents: continue
            tot = sum(e[1] for e in ents)
            ok_sum = tot == cbImage
            second = ents[1][0] if len(ents) > 1 else None
            print(f"V1 hdr+{fld:#x}={off:#x} eb={eb}: parses; sum={tot:#x} "
                  f"sum==cbImage:{ok_sum}; obj0 size={ents[0][1]:#x}; obj1 mem={second and hex(second)}")
            if ok_sum and not found:
                found = (fld, eb, ents, off)
    if found:
        fld, eb, ents, off = found
        print(f"\nV1 WINNER: hdr+{fld:#x} eb={eb} at {off:#x}")
        for i, (mem, cb, o) in enumerate(ents[:12]):
            extra = d[o + 8:o + eb].hex()
            print(f"  obj{i}: mem={mem:#010x} size={cb:#x} +0x20[{extra}]")
        print(f"  total objects: {len(ents)}; mem top = {ents[-1][0] + ents[-1][1]:#x}")
        # runtime cross-check: linear bases vs pointer clusters
        mems = sorted(set(m for m, _, _ in ents))
        print(f"  unique linear bases: {[hex(m) for m in mems[:16]]}")
    else:
        print("\nV1: NO parse has sum==cbImage")

    # V2 -----------------------------------------------------------------
    best = (0, None); p = le
    while p + 484 <= len(d):
        v0 = u32(d, p); run, q = 1, p + 4
        while q + 4 <= len(d) and u32(d, q) == v0 + 0x100 * run:
            run += 1; q += 4
        if run > best[0]: best = (run, p); p = max(p + 4, q)
        else: p += 4
    print(f"\nV2 longest +0x100-stride u32 run in file: len={best[0]} "
          f"at {hex(best[1]) if best[1] is not None else 'nowhere'}")
    if best[0] >= 64 and best[1] is not None:
        at = best[1]
        vals = [u32(d, at + 4 * i) for i in range(min(best[0], 130))]
        print(f"  first 10: {[hex(v) for v in vals[:10]]} low bytes: {sorted(set(v & 0xFF for v in vals))[:6]}")

    # V3 -----------------------------------------------------------------
    # candidate fixup-region starts: table offsets seen, sorted
    cands = sorted(set(u32(d, le + f) for f in (0x2c, 0x30, 0x38, 0x40, 0x48, 0x50, 0x58, 0x70))
                   if True else set())
    for st in cands:
        if st is None or st < le or st >= len(d): continue
        p = st; nrec = 0; types = collections.Counter(); ok = True; fixbytes = 0
        while p + 8 <= len(d):
            rt = d[p]; src = d[p + 1]; dst = u16(d, p + 2)
            cbs = u16(d, p + 4); cbr = d[p + 7] << 16 | u16(d, p + 5)
            if cbr == 0 or cbr > 0x100000 or rt > 6:
                ok = False; break
            nrec += 1; types[rt] += 1; fixbytes += max(cbr - 8, 0)
            p += cbr
            if rt == 0: break
        print(f"V3 from {st:#x}: records={nrec} types={dict(types)} walk_ok={ok} end={p:#x} "
              f"span={p - st:#x} (cbFixup=0x63774) fixdata~{fixbytes:#x}")
    return 0 if found else 1

if __name__ == "__main__":
    sys.exit(main())
