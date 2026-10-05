#!/usr/bin/env python3
"""r1_pointer_measure.py — MEASURE the pointer law (no assumed LE field map).

Model under measurement (from r1_pointer_law.py run 2026-10-05 on slot 46):
  runtime image = payload verbatim at member B (delta-0 across the file span;
  fixups applied IN PLACE at pointer slots);
  pointer slots hold rv = L(obj of target) + stored_value, L0=0x1d4000,
  L1=0x242000 (clusters); stored_value = intra-object offset of the TARGET
  (canonical LE fixup semantics: LE stores intra-object offsets).
Open questions this script answers numerically:
  Q1 rv-value clusters (0x10000 buckets) over all delta!=0 slots -> object
     linear regions; cluster edges at 0x1000 fine grain = object boundaries.
  Q2 per-cluster pv spans at 0x64-granularity profile (is pv for L1 bounded by
     an objB memory size ~0xa3000, as the two-contiguous-objects model needs?)
  Q3 vtable spike: runs >=8 of slots with delta==L0 (pointer tables in the
     loaded image) -> Watcom prologue byte rate at payload[pv] (fixes the
     empty-range bug of r1_pointer_law.py T3).
  Q4 K skew: linear -> physical: rv - K must land in [0, memsize) with
     K = L0 - physBase (objA at image start) — report both K candidates
     (L0-based and L1-based) and any rv-K out of RAM.
  Q5 runtime image extent: last member offset where mem==payload, first
     divergence run after it (fixup area vs BSS).
"""
import argparse, os, struct, sys, zipfile
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base

L0, L1 = 0x1d4000, 0x242000
WATCOM_START = (0x55, 0xB8, 0x53, 0x56, 0x57, 0xE8, 0x9C, 0xC8, 0x6A, 0x68, 0xB9, 0xBA, 0xBB, 0xBE, 0xBF, 0x33, 0x31, 0x2B, 0x8B, 0xF6, 0xF7, 0x81, 0x83, 0xE9, 0xEB, 0x90)

def bda_h(mem):
    return [h for h in range(0, 0x2000)
            if struct.unpack_from("<H", mem, h + 0x413)[0] == 0x280
            and struct.unpack_from("<H", mem, h + 0x44A)[0] == 80]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--needle", default="work/ascend_payload.bin")
    ap.add_argument("--slot")
    args = ap.parse_args()
    pay = open(args.needle, "rb").read()
    PS = len(pay)
    anch = build_anchors(pay)
    savedir = os.path.join(args.run_dir, "save")
    slots = sorted(f for f in os.listdir(savedir) if f.endswith(".sav"))
    if args.slot: slots = [f for f in slots if f == args.slot]

    for f in slots:
        mem = zipfile.ZipFile(os.path.join(savedir, f)).read("Memory")
        H = bda_h(mem)[0]
        votes, _ = find_base(mem, anch)
        B, n = votes.most_common(1)[0]
        phys = B - H
        print(f"=== {f}: H={H:#x} B={B:#x} image_phys={phys:#x} memsize={len(mem):#x}")
        end = min(PS - 4, len(mem) - B - 4)

        # Q1 rv clusters
        rvhist = Counter()
        per = {L0: [], L1: []}
        for o in range(0, end, 4):
            rv = struct.unpack_from("<I", mem, B + o)[0]
            pv = struct.unpack_from("<I", pay, o)[0]
            d = rv - pv
            if d and rv < 0x4000000:
                rvhist[rv >> 16] += 1
                if d in per and pv: per[d].append((o, pv, rv))
        print("Q1 rv buckets (>=64K units, count): " +
              ", ".join(f"{b:#x}:{c}" for b, c in sorted(rvhist.items()) if c >= 30))
        for D in (L0, L1):
            rvs = [r for _, _, r in per[D]]
            print(f"Q1 D={D:#x}: n={len(rvs)} rv span {min(rvs):#x}..{max(rvs):#x}")

        # fine edges at 0x1000 within each cluster
        for D, lo, hi in ((L0, 0x1d0000, 0x250000), (L1, 0x240000, 0x300000)):
            pages = Counter()
            for o, pv, rv in per[D]:
                pages[rv >> 12] += 1
            on = sorted(pages)
            print(f"Q1 fine D={D:#x}: first rv pages {[hex(x << 12) for x in on[:4]]}, "
                  f"last {[hex(x << 12) for x in on[-4:]]}, npages={len(on)}")

        # Q2 pv profile
        for D in (L0, L1):
            pvs = [p for _, p, _ in per[D]]
            buckets = Counter(p >> 16 for p in pvs)
            print(f"Q2 D={D:#x} pv>>16 buckets: " +
                  ", ".join(f"{b:#x}:{c}" for b, c in sorted(buckets.items())))

        # Q3 vtable spike (delta==L0 runs, anywhere in payload span)
        tables = 0; hit = tot = 0; tpos = []
        o = 0
        while o + 32 <= end:
            run = []
            q = o
            while q + 4 <= end and len(run) < 40:
                rv = struct.unpack_from("<I", mem, B + q)[0]
                pv = struct.unpack_from("<I", pay, q)[0]
                if rv - pv == L0 and 0 < pv < 0x6E000:
                    run.append(pv); q += 4
                else:
                    break
            if len(run) >= 8:
                tables += 1
                tpos.append(o)
                for pv in run:
                    tot += 1
                    hit += 1 if pay[pv] in WATCOM_START else 0
                o = q - 4
            else:
                o += 4
        print(f"Q3 delta-L0 pointer runs>=8: {tables} tables at "
              f"{[hex(x) for x in tpos[:12]]}{'...' if len(tpos) > 12 else ''}")
        print(f"Q3 prologue-byte rate at target: {hit}/{tot} "
              f"({100.0 * hit / max(tot, 1):.0f}%)  [refutation control was 25/169=15%]")
        if tot:
            firsts = Counter()
            for pv in [r for t in tpos for r in range(0, 0)]: pass
        # target pv distribution of table slots (code start addresses)
        tpvs = sorted(set(pv for t in tpos for pv in
                          [struct.unpack_from('<I', pay, t + 4 * i)[0]
                           for i in range(8)]))
        print(f"Q3 distinct target pv: {len(tpvs)} min {tpvs[0]:#x} max {tpvs[-1]:#x}" if tpvs else "Q3 none")

        # Q4 skew candidates
        for name, Lb in (("L0", L0), ("L1", L1)):
            K = Lb - phys
            bad0 = sum(1 for _, _, r in per[L0] + per[L1] if not 0 <= r - K < len(mem))
            print(f"Q4 K({name})={K:#x}: rv-K outside RAM {bad0}/{len(per[L0])+len(per[L1])}")

        # Q5 image extent / divergence profile
        last_same = None; runs = []
        cur_run = 0
        for o in range(0, PS - 4, 0x1000):
            same = mem[B + o:B + o + 0x16] == pay[o:o + 0x16]
            if same: last_same = o; cur_run += 1
        print(f"Q5 last 4KB page (0x16B head) matching payload at 0x{last_same:x}" if last_same else "Q5 none")
        tail = mem[B + PS:B + PS + 64]
        print(f"Q5 first 64B after payload copy: {tail.hex()}")
        print()
    return 0

if __name__ == "__main__":
    sys.exit(main())
