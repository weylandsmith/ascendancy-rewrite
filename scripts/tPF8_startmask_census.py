#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tPF-8 STARTING-TECH MASK CENSUS (zero capture).

Question (D28 item 21): at game start, which restree rows does the VENDOR
mark known (mask byte ds:0x7478e + 0x4b*i, bit 1<<race — same field the
0x46d3c legality predicate reads via dword[rec+0x47]>>24)? The port's
default owns rows 0/1/2 for every race (campaign.cpp kNotes-era block); the
user's vendor report says NO tech is known at start and exactly three
circles (the roots) are displayed.

Method: every banked save (playcap ring + all work/r1/r1sav-* dirs), read
turn counter u16 guest-phys 0x254e10 (t249b law) and the 66-row mask per
race; report the MINIMUM-turn saves' masks and the roots' masks everywhere.
Laws reused, NOT re-derived: base B via r1_sav_scan anchors; DB = B+0x82BB0
(pointer law OQ-011); count word ds:0x74744; restree.txt prereq rows.
Exit 0 = census complete; 2 = harness broken.
"""
import glob, os, struct, sys, zipfile, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import r1_sav_scan as SS


def restree_rows():
    rows = []
    started = False
    for ln in open(os.path.join(ROOT, "extracted/ascend00/restree.txt"),
                   errors="replace"):
        parts = ln.split()
        if not parts:
            continue
        if parts[0] == "66":
            started = True
            continue
        if not started:
            continue
        nums = []
        ok = True
        for x in parts[1:]:
            if not x.isdigit():
                ok = False
                break
            nums.append(int(x))
        if not ok or len(nums) < 2:
            continue
        pre = []
        for n in nums[2:]:
            if n == 255:
                break
            pre.append(n)
        rows.append((parts[0], pre))
    return rows[:66]


def load_saves():
    out = []
    pats = [os.path.join(ROOT, "work/r1/playcap/save/*.sav")]
    pats += [os.path.join(ROOT, "work/r1/r1sav-*/save/*.sav"),
             os.path.join(ROOT, "work/r1/r1sav-*/*.sav")]
    seen = set()
    for pat in pats:
        for p in glob.glob(pat):
            rp = os.path.realpath(p)
            if rp in seen:
                continue
            seen.add(rp)
            out.append(p)
    return out


def main():
    pay = open(os.path.join(ROOT, "work/ascend_payload.bin"), "rb").read()
    anch = SS.build_anchors(pay)
    saves = load_saves()
    if not saves:
        print("harness: no banked saves")
        return 2
    rows = restree_rows()
    roots = [i for i, (n, pre) in enumerate(rows) if not pre]
    print(f"restree rows={len(rows)} roots={roots} "
          f"names={[rows[i][0] for i in roots]}")

    recs = []
    bad = 0
    for p in saves:
        try:
            zf = zipfile.ZipFile(p)
            mem = zf.read("Memory")
        except Exception:
            bad += 1
            continue
        votes, _ = SS.find_base(mem, anch)
        if not votes:
            bad += 1
            continue
        B = votes.most_common(1)[0][0]
        DB = B + 0x82BB0
        try:
            turn = struct.unpack_from("<H", mem, DB + 0x254E10)[0]
        except Exception:
            bad += 1
            continue
        cnt = struct.unpack_from("<H", mem, DB + 0x74744)[0]
        masks = [mem[DB + 0x7478E + 0x4B * i] for i in range(66)]
        recs.append((turn, p, cnt, masks))
    print(f"saves read={len(recs)} unreadable={bad}")
    if not recs:
        return 2
    recs.sort(key=lambda t: t[0])

    print("== 8 LOWEST-TURN saves: per-race owned-row sets ==")
    for turn, p, cnt, masks in recs[:8]:
        per = {}
        for r in range(8):
            owned = [i for i in range(66) if (masks[i] >> r) & 1]
            if owned:
                per[r] = owned
        print(f"turn={turn} cnt={cnt} {os.path.relpath(p, ROOT)}")
        for r, owned in sorted(per.items()):
            print(f"   race{r} n={len(owned)} rows={owned[:12]}"
                  + ("..." if len(owned) > 12 else ""))

    print("== ROOTS mask census across ALL saves ==")
    for i in roots:
        hist = collections.Counter()
        for turn, p, cnt, masks in recs:
            hist[masks[i]] += 1
        print(f"row {i} {rows[i][0]!r}: mask bytes "
              + ", ".join(f"0x{m:02x}x{c}" for m, c in sorted(hist.items())))

    # what would the frontier be at the minimum-turn save, race of the
    # player home owner (owner 0 assumed player; honest: roster unmapped)
    turn, p, cnt, masks = recs[0]
    for r in (0,):
        owned = {i for i in range(66) if (masks[i] >> r) & 1}
        frontier = [i for i, (n, pre) in enumerate(rows)
                    if i not in owned and all(q in owned or q >= 66 for q in pre)]
        print(f"MIN save turn={turn} race{r}: owned={sorted(owned)} "
              f"frontier(first 12)={frontier[:12]} n_frontier={len(frontier)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
