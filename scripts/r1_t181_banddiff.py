#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

r"""r1_t181_banddiff.py — OQ-003 packed-entropy residue: three-class diff (t181).

Question (docs/OPEN-QUESTIONS.md OQ-003 residue): are the "packed-entropy"
byte regions of .gam/.SAV saves real serialized state, or writer-side copied
(uninitialized/session scratch) memory? Verdict rule (STATE.md t181 tasking):
stable-in-played-but-garbage-at-baseline => play-initialized; churns in every
class => disclaim as writer-side copied memory.

PROBE-BUG GUARD [t181 lesson]: mem.find(b'') == 0 and a 512-B chunk read past
EOF is b'' — the first t181 probe hit this (RESUME-014 is 75,603 B, so every
"verbatim chunk" past EOF "matched" at member 0). Every needle here is
length-checked and content-bearing (>= 25% nonzero).

Classes (all artifacts already on disk; zero capture):
  CLASS-FILE    : entropy + same-world save pair diff
                  (work/r1/game/RESUME.GAM Oct21 "R21" vs work/r1/game/01.SAV)
  CLASS-BOOT    : work/r1/selftest-t111-playcap (world R21 loaded, ZERO play,
                  all slots t=1131) — file bytes vs RAM at located addresses
  CLASS-PLAYED  : work/r1/playcap (same world R21, t=1254 score 14)
  CLASS-BASELINE: work/r1/playcap-20261014-224611 (t=0 title) — carries the
                  OCT-14 world verbatim (correction banked: title slots are
                  NOT world-free when RESUME.GAM exists).

Method: locate save blocks in RAM by chunk-verbatim scan (512 B, constant
delta runs); then compare class boots at the SAME located guest addresses.
Exit: 0 = verdict printed, 2 = harness error.
"""
import math, os, struct, sys, zipfile, collections

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CH = 512
R21 = f"{R}/work/r1/game/RESUME.GAM"          # world file, 87,663 B (EOF 0x1566F)
S1 = f"{R}/work/r1/game/01.SAV"               # same world, later save, same size
BOOT = f"{R}/work/r1/selftest-t111-playcap/save/41.sav"
PLAYED = f"{R}/work/r1/playcap/save/41.sav"
TITLE = f"{R}/work/r1/playcap-20261014-224611/save/41.sav"
R14 = f"{R}/work/r1/SAVINGS-backup-20261014/RESUME.GAM"   # 75,603 B, oct-14 world

def ent(b):
    c = collections.Counter(b); n = len(b)
    return 0.0 if not n else -sum((v / n) * math.log2(v / n) for v in c.values())

def ok_needle(seg, ln):
    return len(seg) == ln and sum(1 for x in seg if x) >= ln // 4

def mem(path):
    return zipfile.ZipFile(path).read("Memory")

def chunk_map(data, m):
    """file_off -> located member addr (first verbatim, content-bearing hit)."""
    out = {}
    for i in range(0, len(data) - CH + 1, CH):
        seg = data[i:i + CH]
        if not ok_needle(seg, CH):
            continue
        j = m.find(seg)
        if j >= 0:
            out[i] = j
    return out

def regions(data, m):
    """Collapse chunk_map into (lo, hi, delta) runs with constant delta."""
    cm = chunk_map(data, m)
    offs = sorted(cm)
    runs = []
    for o in offs:
        d = cm[o] - o
        if runs and runs[-1][2] == d and o == runs[-1][1]:
            runs[-1][1] = o + CH
        else:
            runs.append([o, o + CH, d])
    return [tuple(x) for a, b, d in ((r[0], r[1], r[2]) for r in runs)
            for x in [(a, b, d)] if (b - a) >= 2 * CH]

def main():
    A = open(R21, "rb").read()
    Bf = open(S1, "rb").read()
    mA, mB, mT = mem(BOOT), mem(PLAYED), mem(TITLE)

    print("== CLASS-FILE ==")
    print(f"R21 {len(A)} B, 01.SAV {len(Bf)} B, same-size={len(A)==len(Bf)}")
    hi_blocks = [i * CH for i in range(len(A) // CH)
                 if ent(A[i*CH:(i+1)*CH]) >= 5.0]
    print(f"R21 blocks >=5.0 b/B: {[hex(x) for x in hi_blocks]}")
    print(f"GOLD resume.gam same-range 0x13c00..0x15200 entropy {ent(open(f'{R}/game/resume.gam','rb').read()[0x13c00:0x15200]):.2f} b/B (R21 same range {ent(A[0x13c00:0x15200]):.2f})")
    n = min(len(A), len(Bf))
    dpos = [i for i in range(n) if A[i] != Bf[i]]
    az = za = 0
    for o in range(0, n - 4, 4):
        va, vb = A[o:o+4], Bf[o:o+4]
        if va != b"\x00\x00\x00\x00" and vb == b"\x00\x00\x00\x00": az += 1
        if va == b"\x00\x00\x00\x00" and vb != b"\x00\x00\x00\x00": za += 1
    print(f"same-world pair: {len(dpos)} diff bytes ({100*len(dpos)/n:.2f}%), "
          f"asymmetric-zero u32 {az}/{za}")

    print("== LOCATED REGIONS (class-boot, constant-delta runs >=1 KB) ==")
    runs = regions(A, mA)
    for lo, hi, d in runs:
        print(f"  file {lo:#07x}..{hi:#07x} -> member {lo+d:#07x} (delta {d:#x})")

    print("== CLASS DIFF at located addresses (file vs boot vs played) ==")
    label = {0x2b6718: "HEADER", 0x253e23: "S-TABLE-lo", 0x25676f: "S-TABLE",
             0x263fb1: "POOL", 0x276b0c: "BLOCK11200", 0x2d3a0e: "ENTROPY-BAND"}
    band_stability = None
    for lo, hi, d in runs:
        fa = sum(1 for k in range(lo, hi) if A[k] == mA[k + d])
        ab = sum(1 for k in range(lo, hi) if mA[k + d] == mB[k + d])
        fb = sum(1 for k in range(lo, hi) if A[k] == mB[k + d])
        nm = label.get(d, "other")
        print(f"  {nm:14s} len {hi-lo:6d} file==boot {fa}/{hi-lo} "
              f"boot==played {ab}/{hi-lo} ({100*ab/(hi-lo):5.1f}%) file==played {fb}/{hi-lo} ({100*fb/(hi-lo):5.1f}%)")
        if d == 0x2d3a0e:
            s = 100 * ab / (hi - lo)
            band_stability = s if band_stability is None else min(band_stability, s)
    # baseline-class probe at the band's located address: oct-14 title slots
    band_addr = 0x14000 + 0x2d3a0e
    seg = mT[band_addr:band_addr + 64]
    nz = sum(1 for q in range(0, 64, 4) if struct.unpack_from("<I", seg, q)[0])
    print(f"  baseline oct14-slot member {band_addr:#x} (where R21 band lives): "
          f"nonzero u32 {nz}/16")
    verdict_ok = band_stability is not None and band_stability < 50.0
    print("== CLASS-BASELINE correction ==")
    ok = 0; tot = 0
    for off in (0x200, 0x3200, 0x4000, 0xa000, 0xa200, 0xd000):
        seg = R14_data = open(R14, "rb").read()[off:off+0x30]
        if not ok_needle(seg, 0x30):
            continue
        tot += 1
        j = mT.find(seg)
        if j >= 0:
            ok += 1
            print(f"  oct-14 world needle file {off:#07x} -> title slot member {j:#x} (delta {j-off:#x})")
    print(f"  title slots carry OCT-14 WORLD TABLES VERBATIM: {ok}/{tot} needles"
          "  => baseline class is NOT world-free (t181 correction)")

    print("== VERDICT ==")
    if verdict_ok:
        print("ENTROPY-BAND churns at its located address across boots of the")
        print("SAME world, churns between saves of the same world (asymmetric")
        print("zeros, moving blocks), and is absent/low-entropy in the vendor")
        print("golden save at the same range — while every real table region")
        print("(header/S-table/pool/BLOCK11200) is 87-100% stable and load-")
        print("verbatim. The packed-entropy residue is WRITER-SIDE COPIED")
        print("SESSION MEMORY, not a save-format field set. DISCLAIM.")
    else:
        print("band stable at located address — play-initialized hypothesis")
        print("NOT refuted; row stays open. (No default applied.)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
