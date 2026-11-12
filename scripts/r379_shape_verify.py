#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t379 follow-up — VERIFY the one-law reconciliation of the M5 shapes.

r379_shape_census.py measured (banks on disk, zero capture):
  t1253: count word 41, window range(41) covers slots 0..40, s12 live
         (handle 0x00020000 kind 4 'Medium'), s40 'Intil-Za' present.
  t1254: count word 40, window range(40) covers 0..39, s12 DEAD MARKER
         (0xffff0000 kind 0 name ''), s40 STILL handle 0x00000000 kind 1
         'Intil-Za' in the FULL window.
Hypothesis under test here: there is ONE death shape (in-place corpse:
marker + kind 0 + name cleared + count DEC) and the "slot vanished" reading
is an OBSERVATION-LAYER artifact — the watcher enumerates range(count)
(r1_playcap_watch.py process(): base, n = ship_array_law; for k in
range(min(n, 0x6b))), so when the count decrements the highest slot drops out
of the ROWS without any vendor write to that record.

Tests:
 T1 BYTE IDENTITY of slot 40's whole 0x162 record across the boundary
    (sha256 head-to-head). Identical => the vendor never touched it.
 T2 CHANGED-SLOT CENSUS over the full 0..0x6a window: which records differ
    between the two banks (expect s12 among them; s40 must NOT appear).
    NOTE: ships genuinely moved/refreshed across a turn, so a nonzero census
    is expected — the load-bearing claim is only that s40 is absent.
 T3 COUNTER PAIR: the array count u16 (0x4348b == u32@0x43489>>16) versus
    the C4 finalizer's DEC word [ds:0x3067b] (docs/re/_wip_t364.md C4, with
    the guard ds:0x30679>>16 >= 0). Are they the same counter?

Usage: r379_shape_verify.py OLDSAVE NEWSAVE
"""
import hashlib
import os
import struct
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r1_slot as S

COUNT_X = 0x43489
STRIDE = 0x162
SLOTS = 0x6b
C4_WORD_X = 0x3067b      # DEC word (live-ship count) per _wip_t364 C4
C4_GUARD_X = 0x30679     # guard u32 (>>16 >= 0) per _wip_t364 C4


def load(path):
    mem = zipfile.ZipFile(path).read("Memory")
    pay = S.load_payload(os.getcwd())
    anch = S.anchors_cached(os.getcwd(), pay)
    B = S.base_of(mem, anch)
    assert B is not None, f"base failed {path}"
    return mem, B


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    a, b = load(sys.argv[1]), load(sys.argv[2])
    baseA = a[1] + S.OFF + S.SHIP["x"]
    baseB = b[1] + S.OFF + S.SHIP["x"]

    print("T1 slot-40 record byte identity")
    ra = a[0][baseA + 40 * STRIDE: baseA + 41 * STRIDE]
    rb = b[0][baseB + 40 * STRIDE: baseB + 41 * STRIDE]
    ha, hb = hashlib.sha256(ra).hexdigest(), hashlib.sha256(rb).hexdigest()
    print(f"  s40 t1253 sha256 {ha[:24]} len={len(ra)}")
    print(f"  s40 t1254 sha256 {hb[:24]} len={len(rb)}")
    print(f"  T1 {'IDENTICAL (vendor never wrote it)' if ha == hb else 'DIFFERS (vendor wrote the record)'}")
    if ha != hb:
        d = [i for i in range(len(ra)) if ra[i] != rb[i]]
        print(f"  changed byte offsets within record: {['%#x' % i for i in d[:24]]} (n={len(d)})")

    print("T2 changed-slot census (full window)")
    changed, identical = [], []
    for k in range(SLOTS):
        x = a[0][baseA + k * STRIDE: baseA + (k + 1) * STRIDE]
        y = b[0][baseB + k * STRIDE: baseB + (k + 1) * STRIDE]
        (changed if x != y else identical).append(k)
    print(f"  changed={changed}")
    print(f"  unchanged={identical}")
    print(f"  T2 s40 in changed? {40 in changed}  (load-bearing: must be False)")
    print(f"  T2 s12 in changed? {12 in changed}  (load-bearing: must be True)")

    print("T3 counter pair")
    for tag, (mem, B) in (("t1253", a), ("t1254", b)):
        M = B + S.OFF
        arr = struct.unpack_from("<I", mem, M + COUNT_X)[0] >> 16
        c4 = struct.unpack_from("<H", mem, M + C4_WORD_X)[0]
        gd = struct.unpack_from("<I", mem, M + C4_GUARD_X)[0]
        print(f"  {tag}: array count(0x43489>>16)={arr}  C4 word[0x3067b]={c4}  guard u32[0x30679]={gd:#x}>>16={gd >> 16}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
