#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""Assert the end-*.txt victory-condition grammar (docs/re/turnloop.md §1).
Grammar per file: vendor comment, enddesc..endtext, ranks + EXACTLY 10 names
(stop the walker at the next keyword!), congrat..endtext, end. Exit 0 = all
five files conform; any deviation is a hard failure (gate 3l)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ["end-capt", "end-ctrl", "end-dest", "end-unit", "end-xtnc"]
KEYWORDS = {"enddesc", "endtext", "ranks", "congrat", "end"}


def lines_of(path):
    raw = open(path, "rb").read().split(b"\x1a")[0].decode("cp437")
    return [l.strip() for l in raw.replace("\r", "").split("\n")]


def block_names(ls, start):
    """names from start until blank-or-keyword (the trap: continuing past
    'congrat' counted 20 once; keyword stops are mandatory)."""
    out = []
    i = start + 1
    while i < len(ls) and ls[i] and ls[i] not in KEYWORDS and not ls[i].startswith("//"):
        out.append(ls[i])
        i += 1
    return out, i


def main():
    errs = []
    for f in FILES:
        p = os.path.join(ROOT, "extracted", "ascend00", f + ".txt")
        ls = lines_of(p)
        if not ls[0].startswith("// Text file for ending condition:"):
            errs.append(f + ": first line is not the vendor condition comment")
        for kw in KEYWORDS:
            if kw not in ls:
                errs.append(f + ": missing block " + kw)
        if "ranks" in ls:
            names, _ = block_names(ls, ls.index("ranks"))
            if len(names) != 10:
                errs.append(f + ": ranks block has %d names, need exactly 10" % len(names))
        if "enddesc" in ls:
            desc, _ = block_names(ls, ls.index("enddesc"))
            if not desc:
                errs.append(f + ": empty enddesc")
        # endtext closes a block: there must be TWO (enddesc + congrat)
        if ls.count("endtext") != 2:
            errs.append(f + ": %d endtext terminators, need 2" % ls.count("endtext"))
    if errs:
        for e in errs:
            print("FAIL", e)
        return 1
    print("OK 5 end files: vendor condition comments + enddesc/congrat + 10 ranks each")
    return 0


if __name__ == "__main__":
    sys.exit(main())
