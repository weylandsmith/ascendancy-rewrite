#!/usr/bin/env python3
"""r1_planet_layout.py — planet/star record law from resume.gam + live RAM.

Measured 2026-10-05k:
  * resume.gam (game/resume.gam, 23,968 B) carries the CURRENT campaign:
    50 star records (51 B stride, first name at file 0x9966) and 151 planet
    records (123 B stride, first name at file 0x9b1a).
  * The autosave Memory member holds the same two tables verbatim: planet
    record 0 name at member index 0x26d07b+H (phys 0x26d07b, pointer-law H).
    Names + order identical 151/151; every byte equal EXCEPT two fields.
  * So resume.gam IS the on-disk mirror of the live game-state tables —
    a second, pointer-free static source for structure law.

This script re-derives the layout from scratch each run (no baked offsets
beyond the pointer-law H) and prints the byte-position histogram that pins
the owner-dependent fields.

Usage: python3 r1_planet_layout.py [--sav PATH] [--gam game/resume.gam]
"""
import argparse
import collections
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base  # noqa: E402

STRIDE_P = 123
NAME_RE = rb"[A-Z][A-Za-z]{2,}(?: [IVX]+)?\x00"
# STAR SIDE [measured 2026-10-05k]: resume.gam has NO stride-51 star-name
# table (best run = 1); 0x9966 holds a 4-byte-cell grid (vals 0-9,0xff).
# Star naming was ALREADY closed in docs/re/mapgen.md (names.txt pool +
# shuffle): the pool is resident in NEW-GAME slots (Vega/Alpheratz/Fomalhaut
# verbatim in run-204919 slot 48 at phys 0x2e8338, stride-20 records) but
# NOT in resumed-from-save slots (title-screen slot 41: 0 hits, and
# game/resume.gam: 0 hits — save slot numbers ≠ same game). Don't re-litigate.


def first_table(raw, stride):
    """Locate a stride-k table of NUL-terminated name records: find the
    longest run of names spaced exactly `stride` apart."""
    hits = [m.start() for m in re.finditer(NAME_RE, raw)]
    hs = set(hits)
    best = (0, None)
    for h in hits:
        n = 0
        p = h
        while p in hs:
            n += 1
            p += stride
        if n > best[0]:
            best = (n, h)
    return best  # (count, first_name_offset)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sav", default="work/r1/r1deep-20261005-210149/save/41.sav")
    ap.add_argument("--gam", default="game/resume.gam")
    args = ap.parse_args()

    if not os.path.exists(args.sav):
        print(f"[planet] no capture at {args.sav}; skipping")
        return 0
    gam = open(args.gam, "rb").read()
    mem = zipfile.ZipFile(args.sav).read("Memory")
    pay = open("work/ascend_payload.bin", "rb").read()
    votes, _ = find_base(mem, build_anchors(pay))
    if not votes:
        print("[planet] base not found"); return 2
    idx0 = votes.most_common(1)[0][0]   # member index of payload file 0
    H = idx0 - 0x1BF450                 # law: phys p lives at member idx p+H

    n_file_p, p0_file = first_table(gam, STRIDE_P)
    print(f"[planet] resume.gam: {n_file_p} planets stride {STRIDE_P} "
          f"first@{p0_file if p0_file is None else hex(p0_file)} "
          f"(no star-name table: 4-byte grid @0x9966)")
    if n_file_p < 100 or p0_file is None:
        print("[planet] planet table not located in resume.gam"); return 1

    # live RAM tables: anchor on the same first names
    first_name = gam[p0_file:gam.index(b"\x00", p0_file) + 1]
    i = mem.find(first_name, H)
    if i < 0:
        print("[planet] planet table not resident in this slot"); return 1
    p0_ram = i - H
    print(f"[planet] RAM planet table phys {p0_ram:#x} (member idx {i:#x})")

    n_ram = 0
    while True:
        off = p0_ram + n_ram * STRIDE_P
        j = off + H
        if j >= len(mem) or mem[j:j + len(first_name)] == b"\x00" * len(first_name):
            break
        m = re.match(NAME_RE, mem[j:j + 40])
        if not m:
            break
        n_ram += 1
    print(f"[planet] RAM planets: {n_ram}")

    # byte-equality census file vs RAM
    ndiff = collections.Counter()
    mismatch_names = 0
    for k in range(min(n_file_p, n_ram)):
        a = gam[p0_file + k * STRIDE_P: p0_file + (k + 1) * STRIDE_P]
        b = mem[p0_ram + k * STRIDE_P + H: p0_ram + (k + 1) * STRIDE_P + H]
        if a != b:
            # names identical? (offset 0..0x12)
            if a[:0x13] != b[:0x13]:
                mismatch_names += 1
            for d in range(STRIDE_P):
                if a[d] != b[d]:
                    ndiff[d] += 1
    print(f"[planet] differing byte offsets (count/{min(n_file_p,n_ram)}): "
          f"{ndiff.most_common()}")
    print(f"[planet] name-field mismatches: {mismatch_names}")

    # owner-field reading: the two differing bytes as COUNTERS, not constants
    for d in (0x68, 0x69):
        fv = [gam[p0_file + k * STRIDE_P + d] for k in range(min(n_file_p, n_ram))]
        rv = [mem[p0_ram + k * STRIDE_P + H + d] for k in range(min(n_file_p, n_ram))]
        def wraps(s):
            return sum(1 for i in range(1, len(s)) if s[i] < s[i - 1])
        deltas = collections.Counter((rv[i] - fv[i]) & 0xFF
                                     for i in range(len(fv)) if fv[i] != rv[i])
        print(f"  +0x{d:02x}: file range {min(fv)}..{max(fv)} wraps={wraps(fv)} | "
              f"ram range {min(rv)}..{max(rv)} wraps={wraps(rv)} | "
              f"delta hist {deltas.most_common(3)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
