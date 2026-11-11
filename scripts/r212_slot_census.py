#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t212 — runtime census of the displayed-score slot block + binding hunt.

Static leg (scripts/r212_ref_census.py, controls OK) found over obj0 code
[0x14bb0,0x82bb0): the ONLY disp32 refs into 0x482f0..0x48310 are
  R dword [0x482fb] @0x28074, @0x280be           (the score presenter)
  W word  [0x48300] @0x2519b inc / 0x25217,0x25225 (the 0x250aa debug-gated block)
  the 0x48304 per-star attacked-mark array family (t205/t206)
ZERO disp32 writes into 0x482fb..0x482fe. So either
  (i)  the variable is byte/word-sized at 0x482fb and written via base+disp1
       forms (my disp32-only census cannot see disp8 encodings with a struct
       base), or
  (ii) the writer lives OUTSIDE obj0 code (obj1 data-segment code, or an
       overlay) — t191 law: hunt bindings via branch edges / RAM, never
       file-image dwords.

Per save (work/r1/playcap/save/*.sav, mtime order, 'Memory' member):
  C1 raw bytes 0x482f0..0x4831f hexdump + dword[0x482fb]/[0x482ff]/[0x48300]/
     [0x48304] interpretations + turn u32[0x12e10] + T + star-owner counts
     (popcount byte[star+0x15] per star row at 0x13bc5 stride 0x60).
  C2 RAM aligned-dword scan for P0+0x28074 and P0+0x28059 (who references the
     displayer function at runtime; P0 = B+0x82bb0, pointer law OQ-011).
Exit 0 findings; 2 harness error.
"""
import glob
import os
import struct
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_slot as S

OFF = 0x82BB0
TURN = 0x12E10
STARS_WORD = 0x16145
STARS_T = 0x16143
STAR_BASE = 0x13BC5
LO, HI = 0x482F0, 0x48320


def hexdump(mem, p, n=0x30):
    out = []
    for i in range(0, n, 16):
        chunk = mem[p + i:p + i + 16]
        hexs = " ".join(f"{b:02x}" for b in chunk)
        asc = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        out.append(f"    {i:+04x}  {hexs}  |{asc}|")
    return "\n".join(out)


def main():
    pay = open("work/ascend_payload.bin", "rb").read()
    anch = S.anchors_cached(".", pay)
    saves = sorted(glob.glob("work/r1/playcap/save/*.sav"),
                   key=lambda p: os.path.getmtime(p))
    refs28074, refs28059 = set(), set()
    n = 0
    for f in saves:
        mem = zipfile.ZipFile(f).read("Memory")
        B = S.base_of(mem, anch)
        if B is None:
            print(f"  {os.path.basename(f)}: no base vote", file=sys.stderr)
            continue
        P = B + OFF
        n += 1
        turn = struct.unpack_from("<I", mem, P + TURN)[0]
        T = struct.unpack_from("<I", mem, P + STARS_T)[0] >> 16
        nst = struct.unpack_from("<H", mem, P + STARS_WORD)[0]
        d5fb = struct.unpack_from("<I", mem, P + 0x482FB)[0]
        d5ff = struct.unpack_from("<I", mem, P + 0x482FF)[0]
        d600 = struct.unpack_from("<I", mem, P + 0x48300)[0]
        d604 = struct.unpack_from("<I", mem, P + 0x48304)[0]
        owned = sum(1 for k in range(min(nst, 60))
                    if mem[P + STAR_BASE + 0x60 * k + 0x15])
        print(f"{os.path.basename(f)} mtime={os.path.getmtime(f)} t={turn} "
              f"nst={nst} T={T} owned_stars={owned}")
        print(f"  dword[482fb]={d5fb} dword[482ff]={d5ff} "
              f"dword[48300]={d600:#x} (lo-words {d600 & 0xffff},{d600 >> 16}) "
              f"dword[48304]={d604:#x}")
        print(hexdump(mem, P + LO, HI - LO))
        # C2 binding hunt: aligned RAM dwords == P0 + displayer addrs
        P0 = P
        for target, acc in ((0x28074, refs28074), (0x28059, refs28059)):
            needle = struct.pack("<I", P0 + target)
            pos = 0
            while True:
                i = mem.find(needle, pos)
                if i < 0:
                    break
                if i % 4 == 0:
                    acc.add((os.path.basename(f), hex(i),
                             f"guest={i - 0x88:#x}",
                             f"rel_to_5fb={i - 0x88 - (0x482fb)}"))
                pos = i + 1
    print(f"\nsaves={n}")
    print(f"runtime dwords == P0+0x28074: {len(refs28074)}")
    for r in sorted(refs28074):
        print("  ", r)
    print(f"runtime dwords == P0+0x28059: {len(refs28059)}")
    for r in sorted(refs28059):
        print("  ", r)


if __name__ == "__main__":
    main()
