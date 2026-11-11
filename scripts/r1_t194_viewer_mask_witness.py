#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""t194: viewer-mask witness for the OQ-026 lane/star visibility consumer.

Static law (ships.md S23 L9, decompiled verbatim):
  FUN_00028fc0 (cosmos list builder) admits lane i IFF
      byte[lane_pool(0x16147) + 0x27*i + 0x20] & DAT_00089324 != 0
  FUN_00021a84(idx) is the SOLE writer of DAT_00089324:
      mask = (idx == 0xff ? 0xff : 1 << (idx & 0x1f)); DAT_0007458e = idx.

Addressing law (pointer law, OQ-011): runtime_u32 = P0 + file_offset; the
save-state Memory member holds the relocated image at B (find_base anchors)
and the data segment at B + 0x82BB0. DAT_00089324 (0x89324 > 0x82BB0-ish
image-segment global) lives at B + 0x89324 -- measured: B+0x89324 == 0x01
matches the law while B+D+0x89324 reads zeros. X_CUR (0x7458E, data seg)
lives at B + 0x82BB0 + 0x7458E.

Prints per-save: mask byte, X_CUR, law check, lanes visible vs withheld.
RC=0 always (witness, not gate).
"""
import os, struct, zipfile, collections, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base

ROOT = "/home/hrethric/projects/ascendancy"
RUN = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "work/r1/playcap")
PAY = os.path.join(ROOT, "work/ascend_payload.bin")
D = 0x82BB0
PHYS = 0x88
X_MASK = 0x89324          # image segment: runtime addr == B + X
X_CUR = D + 0x7458E       # data segment
X_NLANES = D + 0x177D3
POOL = D + 0x16147
S_POOL = 0x27


def main():
    pay = open(PAY, "rb").read()
    anch = build_anchors(pay)
    nsav = nlaw = 0
    mask_vals = collections.Counter()
    for f in sorted(os.listdir(os.path.join(RUN, "save"))):
        if not f.endswith(".sav"):
            continue
        try:
            mem = zipfile.ZipFile(os.path.join(RUN, "save", f)).read("Memory")
        except Exception:
            continue
        votes, _ = find_base(mem, anch)
        if not votes:
            print("%s: NO BASE" % f)
            continue
        B = votes.most_common(1)[0][0]
        nsav += 1
        m = mem[B + X_MASK]
        c = mem[B + X_CUR]
        mask_vals[m] += 1
        pred = 0xFF if c == 0xFF else (1 << (c & 0x1F))
        law = (m == pred)
        nlaw += law
        nl = struct.unpack_from("<H", mem, B + X_NLANES)[0]
        vis = hid = zero = 0
        for k in range(nl):
            b20 = mem[B + POOL + k * S_POOL + 0x20]
            if b20 == 0:
                zero += 1
            elif b20 & m:
                vis += 1
            else:
                hid += 1
        print("%s B=%#x mask=%#04x xcur=%d law=%s nlane=%d VIS=%d HID=%d zero=%d"
              % (f, B, m, c, "OK" if law else "MISMATCH", nl, vis, hid, zero))
    print("saves=%d law_ok=%d mask_vals=%s" % (nsav, nlaw, dict(mask_vals)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
