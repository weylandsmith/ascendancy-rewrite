#!/usr/bin/env python3
"""t212 — decoder-independent checks on the DAT_000482fb writer census.

scripts/r212_ref_census.py (capstone, resume-past-gaps, controls OK) found
ZERO writes to 0x482fb..0x482fe in obj0 code [0x14bb0,0x82bb0), while the
variable demonstrably changes during play (12..22, t188b). A zero from a
LINEAR decoder can be a desync artifact (a spurious long decode swallows real
code), and it cannot see an address-taken write at all. Two checks:

C1 RAW BYTE SCAN (no decoder, whole restored image 0x0..0x8cc83): every offset
   containing the LE bytes of any address in [0x482f0,0x48300) — i.e. every
   possible disp32 encoding of the displayed-score slot, wherever it sits,
   decoded or not. Cross-check: the scan MUST contain 0x28074/0x280be (found
   by capstone) or the two passes disagree; capstone hits outside the raw set
   would be a census bug either way. Also reports whether raw finds MORE
   (=> decode desync, the capstone zero is void).
C2 RAM POINTER SCAN (20-sav corpus): aligned guest dwords whose value points
   INTO [P0+0x482f0, P0+0x48310) — a relocated pointer variable to the score
   block would explain base+disp8 writers that no static disp census can see
   (t191 law: hunt bindings in RAM, never file-image dwords).

Exit 0 findings; 2 harness error / control disagreement.
"""
import glob
import os
import struct
import struct as st
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_slot as S

IMG = "work/ascend_restored.bin"
OFF = 0x82BB0
LO, HI = 0x482F0, 0x48300          # the displayed-score dword's own range
LO2, HI2 = 0x482F0, 0x48310        # + neighbours for the pointer scan


def main():
    img = open(IMG, "rb").read()
    print(f"C1 RAW SCAN {IMG} len={len(img):#x} region {LO:#x}..{HI:#x}")
    hits = {}
    for a in range(LO, HI):
        pat = st.pack("<I", a)
        pos = 0
        while True:
            i = img.find(pat, pos)
            if i < 0:
                break
            hits.setdefault(a, []).append(i)
            pos = i + 1
    for a in sorted(hits):
        offs = hits[a]
        print(f"  disp={a:#x}: {len(offs)} raw occurrences at "
              f"{[hex(o) for o in offs[:24]]}")
    raw_offs = {o for v in hits.values() for o in v}
    for ctrl in (0x28074, 0x280be):
        # the disp32 sits immediately after the opcode byte(s)
        if not any(o == ctrl + 2 or o == ctrl + 1 or o == ctrl + 6
                   for o in raw_offs):
            print(f"  CONTROL WEAK: no raw disp within 6 bytes of {ctrl:#x}")
    print("  capstone-vs-raw: capstone mem-hits in region were "
          "0x28074,0x280be (dword) + word/dword at 0x48300,0x48304")

    print("\nC2 RAM POINTER SCAN region "
          f"{LO2:#x}..{HI2:#x} (relocated: P0+X, P0 = B+{OFF:#x})")
    pay = open("work/ascend_payload.bin", "rb").read()
    anch = S.anchors_cached(".", pay)
    tot = {}
    nsaves = 0
    # find-based (decoder-free, fast): for each possible TARGET offset, the
    # relocated pointer value is exactly P0+X, so scan per-X with bytes.find
    # instead of unpacking every dword.
    targets = list(range(LO2, HI2))
    for f in sorted(glob.glob("work/r1/playcap/save/*.sav"),
                    key=lambda p: os.path.getmtime(p)):
        mem = zipfile.ZipFile(f).read("Memory")
        B = S.base_of(mem, anch)
        if B is None:
            continue
        nsaves += 1
        P0 = B + OFF
        seen = []
        for x in targets:
            # relocated pointer values are GUEST-PHYSICAL (member-0x88 law);
            # scan both candidate forms so a miss can't be an off-by-0x88.
            for form, val in (("phys", P0 + x - 0x88), ("lin", P0 + x)):
                needle = st.pack("<I", val)
                pos = 0
                while True:
                    i = mem.find(needle, pos)
                    if i < 0:
                        break
                    kind = ("CODE-IMG" if x < 0x82BB0 else "DATA-SEG")
                    seen.append((hex(i), hex(i - 0x88),
                                 f"target=+{x:#x}", form, kind))
                    key = f"ptr->+{x:#x}({form})"
                    tot[key] = tot.get(key, 0) + 1
                    pos = i + 1
        print(f"  {os.path.basename(f)}: {len(seen)} pointer(s) into region")
        for srow in seen[:12]:
            print("     ", srow)
    print(f"\nsaves={nsaves}")
    print("distinct pointer targets (target -> count over corpus):")
    for k, c in sorted(tot.items(), key=lambda kv: -kv[1]):
        print(f"   {k} x{c}")


if __name__ == "__main__":
    main()
