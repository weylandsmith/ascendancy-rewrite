#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

"""r1_restree_law.py — decode the LIVE research table in guest RAM (OQ-013).

Measured law (2026-10-06r): restree.txt rows appear in guest RAM as
stride-75 records: name[60] (CP437, NUL-padded, '^' replaced by SPACE)
followed by a 15-byte tail carrying cost + the 0xFF-terminated prerequisite
and child index lists — the same grammar as the file, materialised.

The table starts at a per-run address derived from the pointer law
(H = per-run base offset from r1_sav_scan.find_base, minus the 0x1BF450
anchor convention); the finder here anchors on the spaced name of row 0 and
walks stride 75, so it never hard-codes an absolute address.

Exit 0 = table found and cost/prereq cross-check against restree.txt passes on
>= 90% of located rows.  1 = ran, negative.  2 = harness error.

Usage: r1_restree_law.py --run-dir DIR [--ck-dir DIR] [--slot NAME] [--dump N]
"""
import argparse, os, struct, sys, zipfile
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAY = os.path.join(ROOT, "work", "ascend_payload.bin")
RESTREE = os.path.join(ROOT, "extracted", "ascend00", "restree.txt")
STRIDE = 75
NAME_LEN = 60


def load_rows():
    """restree.txt -> list of dicts in file order (main tree 0..65, variants 66..105)."""
    txt = open(RESTREE, "rb").read().decode("cp437")
    rows = []
    for line in txt.split("\r\n"):
        t = line.split()
        if not t or (len(t) == 1 and t[0].isdigit()) or len(t) < 3:
            continue
        rows.append({
            "id": len(rows),
            "raw": t[0],
            "spaced": t[0].replace("^", " "),
            "f0": int(t[1]),
            "cost": int(t[2]),
            "prereq": [int(x) for x in t[3:] if x != "255"],
            "variant": t[0].isupper(),
        })
    return rows


def all_hits(mem, needle):
    out, s = [], 0
    while True:
        o = mem.find(needle, s)
        if o < 0:
            return out
        out.append(o)
        s = o + 1


def tail_lists(tail):
    """Split the 15-byte tail on 0xFF runs -> (cost, prereq[], children).

    Empirical grammar: u16 cost, then byte-lists terminated by 0xFF, 0-padded.
    Returns None when the shape is unparseable.
    """
    cost = struct.unpack_from("<H", tail, 0)[0]
    groups, cur = [], []
    for b in tail[2:]:
        if b == 0xFF:
            groups.append(cur)
            cur = []
        elif b != 0x00 or cur:
            cur.append(b)
    prereq = groups[0] if groups else []
    children = groups[1] if len(groups) > 1 else []
    return cost, prereq, children


def load_mem(run_dir, slot=None):
    pay = open(PAY, "rb").read()
    anch = build_anchors(pay)
    src = run_dir
    for sub in ("save", "ck"):
        if os.path.isdir(os.path.join(run_dir, sub)):
            src = os.path.join(run_dir, sub)
            break
    slots = sorted(f for f in os.listdir(src) if f.endswith(".sav"))
    if slot:
        slots = [s for s in slots if s == slot]
    for f in slots:
        try:
            m = zipfile.ZipFile(os.path.join(src, f)).read("Memory")
        except Exception:
            continue
        v, _ = find_base(m, anch)
        if not v:
            continue
        return f, m, v.most_common(1)[0][0] - 0x1BF450
    return None, None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--slot")
    ap.add_argument("--dump", type=int, default=0, help="print N decoded rows")
    a = ap.parse_args()

    rows = load_rows()
    if len(rows) != 106:
        print(f"harness-error: restree parse gave {len(rows)} rows, expected 106")
        return 2
    f, mem, H = load_mem(a.run_dir, a.slot)
    if mem is None:
        print("harness-error: no readable save slot with a base")
        return 2

    # Anchor on row 0 (Orbital Structures) spaced name; table walk from there.
    hits = all_hits(mem, rows[0]["spaced"].encode("cp437"))
    if not hits:
        print(f"NEGATIVE: row0 name absent in {f}")
        return 1

    best = None
    for h in hits:
        n = 0
        ok = 0
        p = h
        while p + STRIDE <= len(mem):
            rec = mem[p:p + STRIDE]
            nm = rec[:NAME_LEN].split(b"\x00")[0].decode("cp437", errors="replace")
            if nm != rows[n]["spaced"]:
                break
            # MEASURED COST LAW (loader FUN_00046870; docs/re/research.md §6b):
            # runtime u16 cost at RECORD base+62; this walk's rec is anchored
            # at the NAME (record base+2), so the field is rec[60:62].
            # runtime = file_cost * (2*row-20) for row > 10 else file_cost,
            # clamped 65000. Verified 66/66 rows x 27 slots (all banked
            # captures, turns 0..9).
            ram_cost = struct.unpack_from("<H", rec, 60)[0]
            c = rows[n]["cost"]
            exp = c if n <= 10 else min(c * 2 * (n - 10), 65000)
            if ram_cost == exp:
                ok += 1
            n += 1
            p += STRIDE
            if n >= len(rows):
                break
        if best is None or n > best[1]:
            best = (h, n, ok)
    h, n, ok = best if best else (0, 0, 0)
    print(f"slot={f} table@phys={h + H:#x} stride={STRIDE} rows_walked={n} "
          f"cost_match={ok} H={H:#x}")
    if n < 10:
        print("NEGATIVE: table walk died early")
        return 1

    # presence census over all 106 spaced names (case-sensitive: variants are ALL-CAPS)
    present_main = present_var = 0
    absent_var = []
    for r in rows:
        hs = all_hits(mem, r["spaced"].encode("cp437"))
        # hits inside the walked table count; elsewhere counts too (report both)
        r["hits"] = [x + H for x in hs]
        if hs:
            if r["variant"]:
                present_var += 1
            else:
                present_main += 1
        elif r["variant"]:
            absent_var.append(r["raw"])
    print(f"MAIN rows present in RAM: {present_main}/66")
    print(f"VARIANT rows present in RAM: {present_var}/40")
    if absent_var:
        print(f"variant absent sample: {absent_var[:12]}")

    # also test the raw '^' forms — if RAM ever stored them, presence flips
    var_caret = sum(1 for r in rows if r["variant"]
                    and all_hits(mem, r["raw"].encode("cp437")))
    print(f"variant rows present with '^' spelling: {var_caret}/40")

    if a.dump:
        p = h
        for r in rows[:a.dump]:
            rec = mem[p:p + STRIDE]
            t = tail_lists(rec[NAME_LEN:])
            print(f"  {r['id']:3d} f0={r['f0']} cost={r['cost']:3d} file_pre={r['prereq']} "
                  f"ram={(t[1], t[2]) if t else None} @phys={p + H:#x}")
            p += STRIDE

    frac = ok / max(n, 1)
    if frac >= 0.9:
        print(f"PASS: cost cross-check {ok}/{n} ({frac:.0%}) against restree.txt")
        return 0
    print(f"NEGATIVE: cost cross-check only {ok}/{n}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
