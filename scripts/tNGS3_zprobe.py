#!/usr/bin/env python3
"""tNGS cycle 3 Z1 static probe: locate the star-z generator evidence.

(1) f32 shell-radius constants (440/365/290/215/140/65/50) in the payload:
    a shared shell-radius TABLE is the mapgen position-law footprint; its
    consumer site is the z writer candidate.
(2) disasm context around any table hits is left to t442_disasm.py.
Run: ~/tools/revenv/bin/python scripts/tNGS3_zprobe.py
"""
import struct
import sys

PAY = "work/ascend_payload.bin"

def main():
    pay = open(PAY, "rb").read()
    print(f"payload {len(pay)} bytes")
    radii = [440.0, 365.0, 290.0, 215.0, 140.0, 65.0, 50.0]
    pats = [struct.pack("<f", r) for r in radii]
    # find consecutive-radius runs (a table: 440,365,290,215,140,65,50 adjacent)
    joined = b"".join(pats)
    i = pay.find(joined)
    print(f"shell-table (7 f32 run 440..50) at {hex(i) if i>=0 else 'NOT FOUND'}")
    # reverse order too
    i2 = pay.find(b"".join(pats[::-1]))
    print(f"reversed run at {hex(i2) if i2>=0 else 'NOT FOUND'}")
    # any pair adjacency 440,365
    p2 = pats[0] + pats[1]
    locs = []
    start = 0
    while True:
        k = pay.find(p2, start)
        if k < 0:
            break
        locs.append(hex(k))
        start = k + 1
    print(f"adjacent 440,365 f32 pairs: {locs}")
    # individual constants with counts
    for r, p in zip(radii, pats):
        print(f"f32 {r}: {pay.count(p)} occurrences", end="")
        if 0 < pay.count(p) <= 12:
            print(" at", [hex(k) for k in _finds(pay, p)], end="")
        print()

def _finds(pay, p):
    start = 0
    while True:
        k = pay.find(p, start)
        if k < 0:
            return
        yield k
        start = k + 1

if __name__ == "__main__":
    sys.exit(main())
