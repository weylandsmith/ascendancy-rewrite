#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""vtable_base_test.py — test whether the payload's pointer tables admit a
single absolute load base C (VA = payload_file_offset + C).

WHY: OQ-011 asks for C. Pointer tables (Watcom C++ vtables: runs of u32 that
are all 4-aligned and in-image, with a repeated value at a fixed slot index
across tables — the shared destructor signature) are the strongest possible
evidence, because EVERY entry in EVERY table must agree on the same C.

METHOD (base-free discovery + base-consistency scoring):
 1. Discover tables without assuming C: maximal runs (>=8) of 4-aligned u32
    values in (0, image_size).
 2. For every candidate C in [0, 0x40000), score how many entries point at a
    Watcom prologue once C is subtracted.
 3. Compare the best score against the random-hit expectation. A real C shows
    a sharp spike near 100%; noise shows a flat plateau.

Run: ~/tools/revenv/bin/python scripts/vtable_base_test.py
"""
import struct, collections, sys

IMG = "work/ascend_payload.bin"


def main() -> int:
    d = open(IMG, "rb").read()
    N = len(d)

    runs, run = [], []
    for p in range(0, N - 3, 4):
        v = struct.unpack_from("<I", d, p)[0]
        if 0 < v < N and (v & 3) == 0:
            run.append((p, v))
        else:
            if len(run) >= 8:
                runs.append(run)
            run = []
    if len(run) >= 8:
        runs.append(run)

    vals = [v for r in runs for _, v in r]
    print(f"image={N} tables(>=8 entries)={len(runs)} entries={len(vals)}")
    for r in sorted(runs, key=lambda r: -len(r))[:5]:
        print(f"  table@{r[0][0]:#08x} len={len(r)} first3={[hex(v) for v in [v for _, v in r[:3]]]}")

    # Shared value at a shared slot index across independent tables is the
    # vtable destructor signature — it proves the runs really are vtables.
    by_slot = collections.defaultdict(collections.Counter)
    for r in runs:
        for i, (_, v) in enumerate(r):
            by_slot[i][v] += 1
    shared = [(i, v, c) for i, ctr in by_slot.items() for v, c in ctr.items() if c >= 4]
    shared.sort(key=lambda t: -t[2])
    print(f"shared(slot,value) x>=4: {len(shared)}", shared[:4])

    def pro(i: int) -> bool:
        if i < 0 or i + 2 >= N:
            return False
        a, b, c = d[i], d[i + 1], d[i + 2]
        return ((a == 0x55 and b == 0x8b and c == 0xec) or (a == 0x55 and b == 0x89)
                or (a == 0x53 and b in (0x56, 0x57)) or (a == 0x56 and b in (0x57, 0x53)))

    # Random expectation: probability a uniformly-chosen in-image offset starts
    # with one of the prologue patterns, measured by direct census.
    census = sum(1 for i in range(N - 3) if pro(i))
    p_rand = census / (N - 3)
    print(f"prologue census={census} random_hit_rate={p_rand:.4f}")

    best = collections.Counter()
    for C in range(0, 0x40000):
        best[C] = sum(1 for v in vals if pro(v - C))
    top = best.most_common(6)
    print("top candidates:", [(hex(c), h) for c, h in top])
    exp = p_rand * len(vals)
    print(f"expected random hits for {len(vals)} entries: {exp:.1f}")
    if top and top[0][1] >= max(3 * exp, 0.5 * len(vals)):
        print(f"VERDICT: C={top[0][0]:#x} survives (hits {top[0][1]}/{len(vals)})")
        return 0
    print("VERDICT: NO absolute load base C explains the pointer tables. "
          f"Best candidate gets {top[0][1] if top else 0}/{len(vals)} vs {exp:.1f} expected "
          "by chance — a flat plateau, not a spike.")
    return 2


if __name__ == "__main__":
    sys.exit(main())
