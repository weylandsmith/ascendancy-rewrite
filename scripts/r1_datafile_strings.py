#!/usr/bin/env python3
"""r1_datafile_strings.py — which data files does the exe actually reference?

OQ-004's first measurable half: the payload contains literal data-file names.
A name that NO aligned u32 in live guest RAM points at is a dead/debug string;
a name with referrers points at the code that opens it. Pointer law (CLOSED,
docs/re/r1-savestate.md) converts a referrer's guest-physical address into the
Ghidra address of the reference: d = (member_offset - H) - P0, then
get_function_by_address(d) yields the loader.

Method (no hard-coded addresses; per-run base re-derived from anchors):
  1. every '<name>.txt' literal in work/ascend_payload.bin -> payload offset
  2. for each, scan the guest Memory member for u32 == P0 + offset
  3. report referrer count + the Ghidra addresses (deduped, sorted)

Usage: r1_datafile_strings.py --run-dir DIR [--ext txt] [--min-hits 1]
Exit 0 = census produced (>=1 referenced name). 1 = nothing referenced.
2 = harness error (no capture / base not found).
"""
import argparse, os, re, struct, struct as st, sys, zipfile
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAY = os.path.join(ROOT, "work", "ascend_payload.bin")
NAME_RE = re.compile(rb"[A-Za-z0-9_\-]{3,24}\.(txt|bin|dat|shp|voc|raw)")


def load_mem(run_dir):
    src = run_dir
    for sub in ("save", "ck"):
        if os.path.isdir(os.path.join(run_dir, sub)):
            src = os.path.join(run_dir, sub)
            break
    if not os.path.isdir(src):
        return None, None, None
    pay = open(PAY, "rb").read()
    anch = build_anchors(pay)
    for f in sorted(x for x in os.listdir(src) if x.endswith(".sav")):
        try:
            m = zipfile.ZipFile(os.path.join(src, f)).read("Memory")
        except Exception:
            continue
        v, _ = find_base(m, anch)
        if not v:
            continue
        B = v.most_common(1)[0][0]
        H = B - 0x1BF450          # member-header convention (re-derive per build)
        return f, m, B - H        # P0
    return None, None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--ext", default="txt")
    ap.add_argument("--all-slots", action="store_true",
                    help="union referrers over every slot, not just the first readable one")
    a = ap.parse_args()

    pay = open(PAY, "rb").read()
    names = OrderedDict()
    for mm in NAME_RE.finditer(pay):
        if mm.group(1).decode() != a.ext:
            continue
        names.setdefault(mm.group(0).decode(), []).append(mm.start())

    src = a.run_dir
    for sub in ("save", "ck"):
        if os.path.isdir(os.path.join(a.run_dir, sub)):
            src = os.path.join(a.run_dir, sub)
            break
    slots = sorted(x for x in os.listdir(src) if x.endswith(".sav"))
    if not slots:
        print("harness-error: no .sav slots under", src)
        return 2

    union = {}
    used = []
    for f in slots:
        try:
            m = zipfile.ZipFile(os.path.join(src, f)).read("Memory")
        except Exception:
            continue
        v, _ = find_base(m, build_anchors(pay))
        if not v:
            continue
        B = v.most_common(1)[0][0]
        H = B - 0x1BF450
        P0 = B - H
        used.append(f)
        for name, offs in names.items():
            acc = union.setdefault(name, set())
            for fo in offs:
                pat = struct.pack("<I", P0 + fo)
                s = 0
                while True:
                    o = m.find(pat, s)
                    if o < 0:
                        break
                    acc.add(o - H - P0)  # guest-phys = o - H; d = phys - P0
                    s = o + 1
        if not a.all_slots:
            break

    print(f"slot(s) used: {used}")
    print(f"{'name':16s} {'payload offsets':28s} referrers  ghidra refs")
    ref_count = 0
    for name, offs in names.items():
        refs = sorted(union.get(name, ()))
        tag = " ".join(hex(o) for o in offs)[:28]
        mark = f"{len(refs):3d}" if refs else "  0"
        if refs:
            ref_count += 1
        print(f"{name:16s} {tag:28s} {mark}     "
              f"{', '.join(hex(r) for r in refs[:6])}{' ...' if len(refs) > 6 else ''}")
    print(f"names with >=1 referrer: {ref_count}/{len(names)}")
    return 0 if ref_count else 1


if __name__ == "__main__":
    sys.exit(main())
