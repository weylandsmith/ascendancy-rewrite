#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""ebx_relative_test.py — test the Watcom position-independent (-FPi) data
model, in which data addresses are [EBX+disp32] rather than absolute.

WHY: scripts/vtable_base_test.py showed no single absolute base C explains the
pointer tables, while 806 decoded instructions use [EBX...]. Under -FPi the
Watcom runtime sets EBX once to a data base, so EVERY data reference satisfies
    string_file_offset = K + disp32
for one single K. That is one unknown instead of an address-sized mystery, and
it is testable statically: vote K over the disassembler's EBX-relative
displacements and check whether one K explains ~all string anchors.

If a K wins, absolute data identity becomes recoverable (VA = file_offset + K
for DATA, code stays at VA = file_offset), which is what OQ-011 needs.
If none wins, -FPi is refuted too and OQ-011 needs runtime evidence
(dosbox memory dump) — recorded, not guessed.
"""
import re, sys, struct, collections, random
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

IMG = "work/ascend_payload.bin"
FUNCS = "work/functions.tsv"


def main() -> int:
    d = open(IMG, "rb").read()
    N = len(d)

    bodies = []
    try:
        for ln in open(FUNCS).read().splitlines()[1:]:
            parts = ln.split("\t")
            if len(parts) >= 2:
                o, s = int(parts[0], 16), int(parts[1])
                if s > 0:
                    bodies.append((o, o + s))
    except FileNotFoundError:
        print("no work/functions.tsv; falling back to a whole-image linear sweep")
        bodies = [(0, N)]
    print(f"image={N} code_bodies={len(bodies)} code_bytes={sum(b-a for a,b in bodies)}")

    anchors = [m.start() for m in re.finditer(rb'DATA\\[A-Za-z%0-9._]{2,32}', d)]
    print(f"anchors={len(anchors)} span={anchors[0]:#x}..{anchors[-1]:#x}")

    md = Cs(CS_ARCH_X86, CS_MODE_32)
    md.detail = True
    disps = []
    insns = 0
    ebx_insns = 0
    for a, b in bodies:
        for ins in md.disasm(d[a:b], a):
            insns += 1
            has_ebx = "ebx" in ins.op_str.lower()
            if not has_ebx:
                continue
            ebx_insns += 1
            # disp32 appears as the decimal/hex number inside [ebx + N]
            m = re.search(r"\[\s*ebx\s*([+-])\s*(0x[0-9a-f]+|\d+)\s*\]", ins.op_str.lower())
            if not m:
                continue
            sign = -1 if m.group(1) == "-" else 1
            val = int(m.group(2), 0)
            disps.append(sign * val)
    print(f"insns={insns} ebx_insns={ebx_insns} ebx_disps={len(disps)}")
    if len(disps) < 50:
        print("VERDICT: too few EBX-relative displacements to test -FPi")
        return 2

    # Vote: K such that (K + disp) hits an anchor start, allowing a hit to be
    # the anchor OR any byte within the anchor string (data refs often point at
    # the struct holding the pointer, so require the strict start; the control
    # below measures how often a random K would hit anyway).
    anchor_set = set(anchors)
    best = collections.Counter()
    for dp in disps:
        for a in anchors:
            k = a - dp
            best[k] += 1
    top = best.most_common(6)
    uniq = len(disps)
    exp = len(anchors) * uniq / max(anchors[-1] - anchors[0], 1)
    print(f"control: expected hits per K by chance ~ {exp:.3f}")

    # SPACING CONTROL. Measured anchor gaps are 15..31 bytes inside the string
    # cluster while EBX displacements are overwhelmingly multiples of 4, so a K
    # near the cluster accrues hits by arithmetic alone. Re-run the identical
    # vote with anchor positions randomised UNIFORMLY INSIDE THE SAME SPAN
    # (same count, same displacements). If the control reproduces the real
    # top-K count, the "signal" is spacing, not a data base.
    import random
    lo, hi = anchors[0], anchors[-1]
    ctrl_top = []
    for _ in range(10):
        rnd = sorted(random.randrange(lo, hi) for _ in anchors)
        c = collections.Counter()
        for dp in disps:
            for a in rnd:
                c[a - dp] += 1
        ctrl_top.append(c.most_common(1)[0][1])
    real = max(best.values())
    print(f"control top-K hit counts (10 trials, randomised anchors): {ctrl_top}")
    if real <= max(ctrl_top):
        print(f"VERDICT: REFUTED by control. real_top={real} control_top={max(ctrl_top)} — "
              "the vote is explained by anchor spacing, not a data base K.")
        return 2

    for k, h in top:
        print(f"  K={k:#x} hits={h}/{uniq} disps explain ({100*h/uniq:.2f}% of displacements)")
    if top and top[0][1] >= max(10, 0.15 * uniq):
        print(f"VERDICT: -FPi supported, K={top[0][0]:#x}")
        return 0
    print("VERDICT: no single K explains a meaningful share of EBX-relative "
          "displacements; the -FPi model is not confirmed statically.")
    return 2


if __name__ == "__main__":
    sys.exit(main())
