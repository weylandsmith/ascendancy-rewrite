#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""Scan dosbox-x autosave slots for the live ascend.exe image (R1 via savestate).

Save files are ZIPs (measured 2026-10-05); the 'Memory' member is 17,055,880 B
uncompressed for memsize=16 (16 MiB + 278,664 B extra). The FILE-HEAD bytes of
the payload are a USELESS needle: at runtime the first u32s carry fixups
(measured: file head 'LE\\0\\0' vs runtime copy 0710ec03...). Correct law
(measured, 6/6 unanimous high-entropy anchors on slot 46): a mid-image
high-entropy window W at payload offset P appears at member offset B+P for a
single constant B. This script finds B per slot and only prints a HIT when
>=5 anchors are unanimous (the four refuted static schemes, OQ-011, all died
to weak-vote noise; ambiguous windows don't vote).

Exit 0 = B found unanimously in >=1 slot. 1 = ran, negative. 2 = harness error.
"""
import argparse, os, sys, zipfile
from collections import Counter

def build_anchors(pay):
    """High-entropy, zero-free 128-byte windows at 16 KiB stride."""
    anch = []
    p = 0
    while p + 128 <= len(pay):
        w = pay[p:p + 128]
        if len(set(w)) > 40 and w.strip(b"\x00") == w:
            anch.append((p, w))
        p += 0x4000
    return anch

def find_base(mem, anch, max_hit=5):
    votes = Counter()
    positions = {}
    for p, w in anch:
        hits, start = [], 0
        while True:
            o = mem.find(w, start)
            if o < 0:
                break
            hits.append(o)
            start = o + 1
            if len(hits) > max_hit:
                break
        if len(hits) == 1:
            votes[hits[0] - p] += 1
            positions[p] = hits[0] - p
    return votes, positions

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True,
                    help="dir containing save/ with NN.sav ZIPs")
    ap.add_argument("--needle", required=True, help="payload file")
    ap.add_argument("--min-votes", type=int, default=5)
    args = ap.parse_args()

    pay = open(args.needle, "rb").read()
    anch = build_anchors(pay)
    if len(anch) < args.min_votes:
        print("harness-error: payload yields too few high-entropy anchors")
        return 2

    savedir = os.path.join(args.run_dir, "save")
    if not os.path.isdir(savedir):
        print("harness-error: no save dir")
        return 2
    slots = sorted(f for f in os.listdir(savedir) if f.endswith(".sav"))

    live = 0
    for f in slots:
        try:
            z = zipfile.ZipFile(os.path.join(savedir, f))
            mem = z.read("Memory")
        except Exception as e:
            print(f"{f}: read failed {e!r}")
            continue
        votes, positions = find_base(mem, anch)
        if votes and votes.most_common(1)[0][1] >= args.min_votes:
            base, n = votes.most_common(1)[0]
            consist = sum(1 for b in positions.values() if b == base)
            print(f"HIT {f}: base={base:#x} from {n} unanimous anchors "
                  f"({consist}/{len(positions)} consistent)")
            live += 1
        else:
            top = votes.most_common(1)[0] if votes else (0, 0)
            print(f"{f}: negative (best base {top[0]:#x} votes {top[1]} "
                  f"< {args.min_votes})")
    if live:
        print(f"PAYLOAD HIT in {live} slot(s) — R1 route LIVE via savestate")
        return 0
    print("payload copy not found (did ASCEND.EXE run? check dosbox.out; "
          "note autosave lands in <captures>/save/, see script docstring)")
    return 1

if __name__ == "__main__":
    sys.exit(main())
