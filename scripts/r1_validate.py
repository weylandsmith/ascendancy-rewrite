#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""Validate a candidate runtime load base B by pointer density (R1).

The refuted static schemes (OQ-011) voted on code-immediates WITHOUT a memory
image. With the save-state Memory member we do the decisive version: collect
every u32 LE present at aligned positions in guest RAM ONCE, then count how
many sampled payload file-offsets P have (B+P) in that set. The true base
must light up many of the 31,514 disp-only operands; wrong bases stay near
the accidental-hit rate (set size / 2^32).

Exit 0 = validated (candidate > 4x max control AND > 50 hits).
     1 = ran, not decisive.   2 = harness error.
"""
import argparse, glob, os, random, struct, sys, zipfile

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--save-dir", required=True)
    ap.add_argument("--payload", required=True)
    ap.add_argument("--base", required=True, help="candidate base (hex ok)")
    ap.add_argument("--ram-hi", type=lambda x: int(x, 0), default=16 * 1024 * 1024)
    ap.add_argument("--controls", type=int, default=50)
    ap.add_argument("--samples", type=int, default=4000)
    args = ap.parse_args()

    pay = open(args.payload, "rb").read()
    slots = sorted(glob.glob(os.path.join(args.save_dir, "*.sav")))
    if not slots:
        print("harness-error: no .sav"); return 2
    mem = zipfile.ZipFile(slots[-1]).read("Memory")
    BASE = int(args.base, 0)
    IMG_LO, IMG_HI = BASE, BASE + len(pay)

    # one pass: every aligned u32 in guest RAM, with its position for reporting
    pos = {}
    for o in range(0, min(args.ram_hi, len(mem)) - 4, 4):
        v = struct.unpack_from("<I", mem, o)[0]
        if v not in pos:
            pos[v] = o
    print(f"guest RAM u32 set: {len(pos)} distinct aligned values over {args.ram_hi>>20} MiB")

    rng = random.Random(20261005)
    offs = set()
    while len(offs) < args.samples:
        P = rng.randrange(0, len(pay) - 4) & ~3
        if pay[P:P+4] != b"\x00\x00\x00\x00":
            offs.add(P)
    offs = sorted(offs)

    def score(B, report=False):
        n = 0
        for P in offs:
            v = (B + P) & 0xFFFFFFFF
            o = pos.get(v)
            if o is None:
                continue
            # exclude hits that land inside the image itself (self-references
            # exist for every base offset in code — not evidence of the base)
            if IMG_LO <= o <= IMG_HI:
                continue
            n += 1
            if report and n <= 15:
                print(f"   payload+{P:#06x} -> member+{o:#08x} value={v:#x}")
        return n

    cn = score(BASE, report=True)
    print(f"candidate B={BASE:#x}: {cn}/{len(offs)} sampled payload offsets "
          f"point to guest RAM outside the image")
    ctrl = []
    for _ in range(args.controls):
        kick = rng.randrange(0x10000, 32 * 1024 * 1024) & ~3
        ctrl.append(score((BASE + kick) & 0xFFFFFFFF))
    ctrl.sort(reverse=True)
    exp = len(offs) * len(pos) / (1 << 32)
    print(f"controls: max={ctrl[0]} median={ctrl[len(ctrl)//2]} all={ctrl}")
    print(f"random-set expectation: {exp:.2f}")
    if cn > 4 * max(1, ctrl[0]) and cn > 50:
        print("VERDICT: base VALIDATED (pointer density decisive)")
        return 0
    print("VERDICT: not decisive")
    return 1

if __name__ == "__main__":
    sys.exit(main())
