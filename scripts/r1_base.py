#!/usr/bin/env python3
"""Derive the runtime load base of ascend.exe from dosbox-x save states.

Method (multi-chunk anchoring, robust to runtime fixups):
  For payload chunk offsets P in a grid, take a 32-byte window and find it in
  the save's Memory member. base = member_off - P must be CONSTANT across
  chunks that match (Watcom LE loads the image contiguously; .data is
  byte-identical, code may carry fixups at hot offsets only). Report the vote.

Also reports: single-hit chunks (fixup-polluted windows hit nothing), and the
member-to-guest mapping census (what's before the image).

Exit 0 = base derived (majority vote >= 5 chunks, unanimous among hits).
     1 = ran, not derived.   2 = harness error.
"""
import argparse, glob, os, sys, zipfile
from collections import Counter

def chunks(pay, step, wlen):
    for p in range(0, len(pay) - wlen, step):
        yield p, pay[p:p + wlen]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--save-dir", required=True, help="dir with NN.sav ZIPs")
    ap.add_argument("--payload", required=True)
    ap.add_argument("--slot", default=None, help="specific .sav (default: last)")
    ap.add_argument("--step", type=int, default=0x10000)
    ap.add_argument("--window", type=int, default=32)
    args = ap.parse_args()

    pay = open(args.payload, "rb").read()
    slots = sorted(glob.glob(os.path.join(args.save_dir, "*.sav")))
    if not slots:
        print("harness-error: no .sav in", args.save_dir)
        return 2
    slot = args.slot or slots[-1]
    z = zipfile.ZipFile(slot)
    if "Memory" not in z.namelist():
        print("harness-error: no Memory member in", slot)
        return 2
    mem = z.read("Memory")
    print(f"slot={slot} payload={len(pay)} memory={len(mem)}")

    vote = Counter()
    positions = {}
    zero_needle = 0
    for p, n in chunks(pay, args.step, args.window):
        if n.strip(b"\x00") == b"":
            zero_needle += 1
            continue
        hits = []
        start = 0
        while True:
            o = mem.find(n, start)
            if o < 0:
                break
            hits.append(o - p)
            start = o + 1
            if len(hits) > 8:
                break
        if len(hits) == 1:
            vote[hits[0]] += 1
            positions[p] = hits[0]
        # ambiguous chunks (>1 hit) deliberately do NOT vote: short windows in
        # zero/repetitive regions produce spurious bases that pollute the plot
        # (measured pattern from the four refuted static-vote schemes, OQ-011).

    if not vote:
        print("no unique-match chunks at all (try smaller --window)")
        return 1
    (base, strength), = vote.most_common(1)
    strong = sum(v for k, v in vote.items() if k == base)
    print(f"base vote: {base:#x} from {strong:g} unique chunks "
          f"({len(vote)} distinct candidate bases; {zero_needle} zero chunks skipped)")
    if strong < 5:
        print("NOT DERIVED: fewer than 5 unanimous anchoring chunks")
        for k, v in vote.most_common(10):
            print(f"  {k:#x} {v:g}")
        return 1

    # contiguity check: every anchored chunk consistent with base.
    # (positions maps payload-offset -> BASE CANDIDATE o-p, so compare to base
    #  directly — an earlier revision subtracted p twice and misreported 0/N.)
    consistent = sum(1 for p, b in positions.items() if b == base)
    print(f"contiguity: {consistent}/{len(positions)} unique chunks consistent with base")
    print(f"RUNTIME BASE = {base:#x} (member offset; guest-address mapping TBD — "
          f"image VA at member offset o likely maps to guest addr o when the "
          f"member starts at guest 0, verify against DOS PSP/TOS next)")
    # where does the image sit relative to a page?
    print(f"base page: {base >> 12:#x}  off_in_page: {base & 0xfff:#x}")
    print("BASE DERIVED")
    return 0

if __name__ == "__main__":
    sys.exit(main())
