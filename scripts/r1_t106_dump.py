#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r1_t106_dump.py — raw header+grid dump for named planets, dev vs siblings.

P2 [measured]: the +0x55 deviation is frozen for the whole run and clusters by
star system. This dumps the planet-record header bytes (+0x00..+0x23), the
surface slot words, r55/nb/d for one run so deviating planets can be diffed
against their same-system siblings that satisfy the seed law — looking for a
structural marker (a byte the preset/special-mode path would leave behind:
size/cells/row fields, flag byte +0x66, generation constants +0x68/+0x69).

Usage: r1_t106_dump.py --run work/r1/r1deep-20261005-233706 --system Aglarond
"""
import argparse, os, struct as st, sys, zipfile, glob, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r1_income_law as IL
from r1_sav_scan import build_anchors, find_base

NAME_AT = 0x24


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--system", default=None)
    ap.add_argument("--save", default=None)
    args = ap.parse_args()
    anch = build_anchors(open(IL.PAY, "rb").read())
    svs = sorted(glob.glob(os.path.join(args.run, "save", "*.sav")),
                 key=os.path.getmtime)
    m = zipfile.ZipFile(args.save or svs[0]).read("Memory")
    v, _ = find_base(m, anch)
    print(f"run={os.path.basename(args.run)} save="
          f"{os.path.basename(args.save or svs[0])} H={v.most_common(1)[0][0]:#x}")
    recs = IL.find_records(m)
    print(f"records={len(recs)}")
    for base, cells, cap, arr in recs:
        name = m[base + NAME_AT:base + NAME_AT + 30].split(b"\x00")[0] \
               .decode("cp437", "replace").strip()
        if args.system and not name.startswith(args.system):
            continue
        w = [m[arr + i * 4] for i in range(cap)]
        nb = sum(1 for c in w[:cells] if (c & 0xF) != 0)
        r55 = st.unpack_from("<H", m, base + 0x55)[0]
        d = r55 - (nb // 3 + 5)
        hdr = m[base:base + 0x24]
        print(f"{name:16s} d={d:+3d} r55={r55:3d} nb={nb:3d}/{cells:3d} "
              f"cap={cap:3d} size={st.unpack_from('<H', m, base+0x14)[0]} "
              f"row={st.unpack_from('<H', m, base+0x16)[0]} "
              f"f66={m[base+0x66]} pop={st.unpack_from('<H', m, base+0x42)[0]} "
              f"own={m[base+0x57]:#04x}")
        print(f"   hdr00: {hdr.hex()}")
        print(f"   slots: {''.join(f'{c:02x} ' for c in w)}")


if __name__ == "__main__":
    main()
