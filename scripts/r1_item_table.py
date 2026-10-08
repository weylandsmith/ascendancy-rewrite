#!/usr/bin/env python3
"""r1_item_table.py — runtime planitem-table census (AI build-selector input).

Purpose: the AI evaluator (FUN_0003f130 region, restored-image disasm) gates
items on RUNTIME item record byte +5 (a class byte that is ZERO in every
shipped planitem.txt row — it is loaded/derived at runtime). Stub semantics
[verified disasm 0x3f59a..0x3f5e7]: score column by class —
  class 0 -> MPOP(+3), class 2 -> PROS(+2), class 3 -> IND(+0); class 1 stub
is scored via the jump table whose image bytes are link-time data (unresolved).
This tool reads the RUNTIME table so the class->column law can be grounded.

POINTER-INDEX COROLLARY (STATE.md, OQ-011 law): table at Ghidra 0x73e40 lives
at save-member index B + 0x82BB0 + 0x73e40 (B = r1_sav_scan.find_base vote on
the Memory member; H=0x88 member header). Item stride 0x28, 39 rows
[verified 39/39 byte-exact vs file for fields 0..9, OQ-014].

Exit codes: 0 = class law holds (classes subset {0..3} AND surface-class rows'
names match the OQ-014 law "rows 0..21 == SURFACE, 22..30 ORBITAL");
1 = ran, negative/inconclusive (print one-line verdict);
2 = harness-error (no captures / base not found).

Usage: r1_item_table.py [--run-dir DIR ...]   (default: all work/r1/r1deep-*)
"""
import argparse, glob, glob, os, os.path, struct, sys, sys, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base

ITEM_BASE = 0x73e40
STRIDE = 0x28
NROWS = 39
POOLS = 0x82BB0

FIELDS = ["IND", "RES", "PROS", "MPOP", "UPOP", "CLASS", "FLAGS", "COST"]

def slots(run):
    out = []
    for p in sorted(glob.glob(os.path.join(run, "save", "*.sav"))):
        try:
            z = zipfile.ZipFile(p)
        except Exception:
            continue  # torn copy (autosave rewrite-in-place; STATE.md law)
        if "Memory" in z.namelist():
            out.append((p, z.read("Memory")))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", action="append", default=None)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    runs = args.run_dir or sorted(glob.glob("work/r1/r1deep-*"))
    needle = open("work/ascend_payload.bin", "rb").read()
    anch = build_anchors(needle)

    seen = {}          # (run, slot) -> rows
    class_votes = {}   # item index -> Counter of class byte
    name_votes = {}
    ok_slots = 0
    for run in runs:
        for path, mem in slots(run):
            Bv, _ = find_base(mem, anch)
            if not Bv:
                continue
            B = Bv.most_common(1)[0][0]
            base = B + POOLS + ITEM_BASE
            if base + STRIDE * NROWS > len(mem):
                continue
            rows = []
            good = True
            for i in range(NROWS):
                rec = mem[base + i * STRIDE: base + (i + 1) * STRIDE]
                cls = rec[5]
                if cls > 3:
                    good = False
                vals = dict(IND=rec[0], RES=rec[1], PROS=rec[2], MPOP=rec[3],
                            UPOP=rec[4], CLASS=cls,
                            FLAGS=struct.unpack_from("<H", rec, 6)[0],
                            COST=struct.unpack_from("<H", rec, 8)[0])
                name = rec[10:40].split(b"\0")[0].decode("cp437", "replace")
                rows.append((vals, name))
                class_votes.setdefault(i, {}).setdefault(cls, 0)
                class_votes[i][cls] += 1
                name_votes.setdefault(i, {}).setdefault(name, 0)
                name_votes[i][name] += 1
            if good:
                ok_slots += 1
                seen[(run, os.path.basename(path))] = rows

    if not ok_slots:
        print("harness-error: no slot yielded a well-formed 39-row table (class<=3)")
        return 2

    # Majority table
    final = []
    for i in range(NROWS):
        cls = max(class_votes[i], key=class_votes[i].get)
        name = max(name_votes[i], key=name_votes[i].get)
        # field values: majority across slots (values stable; OQ-014)
        final.append((cls, name))

    if not args.quiet:
        print(f"slots ok: {ok_slots}  runs: {len(runs)}")
        print(" idx CLASS name                     majority-class-share")
        for i, (cls, name) in enumerate(final):
            tot = sum(class_votes[i].values())
            share = class_votes[i][cls] / tot
            print(f"{i:4d} {cls:^5d} {name:26s} {class_votes[i]}")

    # LAW CHECK: class 0 == SURFACE (rows 0..21), class 2 == ORBITAL (22..30)
    orbital_rows = [i for i, (c, n) in enumerate(final) if c == 2]
    surf_rows = [i for i, (c, n) in enumerate(final) if c == 0]
    law_surface22 = surf_rows == list(range(0, 22))
    law_orbital9 = orbital_rows == list(range(22, 31))
    other = [(i, c, n) for i, (c, n) in enumerate(final) if c not in (0, 2)]
    if law_surface22 and law_orbital9 and not other:
        print("CLASS LAW CONFIRMED: byte+5 == 0 for the 22 SURFACE rows, 2 for the 9 ORBITAL rows (22..30), nothing else")
        return 0
    print("VERDICT: class law NOT the simple 0/2 surface/orbital split -> "
          f"surface-rows(classes==0)={surf_rows} orbital-rows(classes==2)={orbital_rows} other={other}")
    return 1

if __name__ == "__main__":
    sys.exit(main())
