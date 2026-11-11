#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r1_live_probe.py — decide WHICH guest-physical copy of the image is LIVE.

Measured context (2026-10-05, slot 46 of r1sav-20261005-160721):
  * verbatim payload copy at member B=0x1bf4d8 (physical P0=B-H, H via BDA scan)
    — delta-0 across the file span (r1_pointer_measure Q5: pages match to
    file end, zeros after).
  * dereference rv values cluster [0x1d4000,0x24177c] (D=L0=0x1d4000, pv in
    [0,0x6E000)) and [0x242000,0x2e48e2] (D=L1=0x242000).
  * Q4: with linear==physical identity both clusters are in RAM.

Two competing readings:
  (A) RUNNING IMAGE lives at linear==physical 0x1d4000..0x27d710 (linked fixed
      base; the 0x1BF450 copy is a raw staging/stub buffer). Then the runtime
      bytes at 0x1d4000+X must equal payload[X] (delta-0 verbatim copy) and
      the data object at 0x242000+Y equals payload[fo1+Y] for a single fo1.
  (B) RUNNING IMAGE lives at P0=0x1BF450 (the copy we found) and pointer
      values are L+stored with the extender remapping linear->physical —
      then bytes at 0x1d4000 would NOT be a verbatim payload image (there
      would be no second full copy).

TESTS (all byte-census, no field maps):
  X1  copy census over guest RAM: every offset where mem[?:] matches
      payload[0:64] head-window? head is fixup-garbage at runtime, so use a
      mid-image high-entropy anchor set instead (build_anchors): report ALL
      copy locations, not just the unanimous one.
  X2  verbatimness at linear 0x1d4000: compare mem region starting at member
      (0x1d4000 + H) — if linear==physical, this is guest phys 0x1d4000 —
      against payload[0:0x8c000] page-sampled; and against payload[0x6E000:]
      too (data-obj reading). Print per-64K match rates.
  X3  data-object base fo1 census: for slots with D==L1 the law (A) predicts
      the pointed-at RUNTIME bytes are the file bytes of objB: check whether
      strings under mem[H+rv:] equal payload[fo1+pv'] for ONE constant fo1,
      solved by sampling: take pointer slots whose pv is large; fo1_est =
      (member offset of target bytes found by mem.find of a runtime string) -
      ... too indirect; INSTEAD: search payload for the page-table stride run
      independently (run>=100 stepping +0x100) -> pt_off; law (A)+single-object
      predicts L1 - L0 == pt_off (the +0x6E000 gap = file offset of whatever
      follows objA); report equality.
  X4  CPU CS:EIP cross-check: ZIP has a CPU member; parse for 32-bit EIP/CS
      if layout allows a cheap scan: find values in [0x1d4000,0x27d710) near
      plausible register block offsets; report candidates ONLY as strings of
      evidence (no claim).
Exit 0 if one reading dominates cleanly, 1 ambiguous, 2 harness error.
"""
import argparse, os, struct, sys, zipfile, re
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base

L0, L1, GAP = 0x1d4000, 0x242000, 0x6E000

def bda_h(mem):
    return [h for h in range(0, 0x2000)
            if struct.unpack_from("<H", mem, h + 0x413)[0] == 0x280
            and struct.unpack_from("<H", mem, h + 0x44A)[0] == 80]

def rate(mem, base, pay, poff, n=16, blk=0x1000, head=0x40):
    """page-sampled verbatimness rate: first `head` bytes of each blk."""
    hit = 0
    for i in range(n):
        o = i * blk
        a = mem[base + o:base + o + head]
        b = pay[poff + o:poff + o + head]
        if a == b: hit += 1
    return hit, n

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--needle", default="work/ascend_payload.bin")
    ap.add_argument("--slot")
    args = ap.parse_args()
    pay = open(args.needle, "rb").read()
    anch = build_anchors(pay)
    savedir = os.path.join(args.run_dir, "save")
    slots = sorted(f for f in os.listdir(savedir) if f.endswith(".sav"))
    if args.slot: slots = [f for f in slots if f == args.slot]

    # X3 independent: page-table stride run in the payload file
    def stride_run(d, at):
        v0 = struct.unpack_from("<I", d, at)[0]
        run, q = 1, at + 4
        while q + 4 <= len(d):
            if struct.unpack_from("<I", d, q)[0] == v0 + 0x100 * run:
                run += 1; q += 4
            else:
                break
        return run, v0
    best = (0, None)
    p = 0
    while p + 400 < min(len(pay), 0x20000):
        r, _ = stride_run(pay, p)
        if r > best[0]:
            best = (r, p); p += 4 * r
        else:
            p += 4
    pt_run, pt_off = best
    print(f"X3 payload page-table stride run: len={pt_run} at payload offset {pt_off:#x}")
    print(f"X3 GAP ({GAP:#x}) == pt_off ({pt_off:#x})? {pt_off == GAP}   "
          f"GAP/0x1000 = {GAP//0x1000} pages")

    verdictA = verdictB = 0
    for f in slots:
        z = zipfile.ZipFile(os.path.join(savedir, f))
        mem = z.read("Memory")
        H = bda_h(mem)[0]
        votes, _ = find_base(mem, anch)
        B, n = votes.most_common(1)[0]
        P0 = B - H
        print(f"\n=== {f}: H={H:#x} B={B:#x} P0={P0:#x}")

        # X1 all copy locations of mid-image anchors
        locs = Counter()
        for poff, w in anch[::3]:
            start = 0
            while True:
                o = mem.find(w, start)
                if o < 0: break
                locs[o - poff - H] += 1     # in GUEST PHYSICAL terms
                start = o + 1
        print("X1 copy-vote (guest physical): " +
              ", ".join(f"{a:#x}:{c}" for a, c in locs.most_common(5)))

        # X2 verbatimness census
        for name, lin in (("lin0x1d4000", 0x1d4000), ("P0", P0)):
            base = lin + H
            hit, tot = rate(mem, base, pay, 0)
            hit2, tot2 = rate(mem, base, pay, GAP)
            print(f"X2 {name}: vs payload[0:] {hit}/{tot}  vs payload[{GAP:#x}:] {hit2}/{tot2}")

        # verdict bookkeeping: A if mem[0x1d4000+H:] ~ payload[0:]
        hitA, tot = rate(mem, 0x1d4000 + H, pay, 0)
        verdictA += hitA; verdictB += (tot - hitA)
    print(f"\nVERDICT COUNTS: A(live@0x1d4000 verbatim)={verdictA} "
          f"not-A={verdictB}  -> {'A' if verdictA > verdictB else 'B/ambiguous'}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
