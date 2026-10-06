#!/usr/bin/env python3
"""r1_ckdiff.py — per-record churn diff across ADAPTIVE checkpoints.

For runs/ck dirs produced by scripts/r1_adcapture.sh: decode planet names
(per-run base law), report the turn per checkpoint, and for every consecutive
checkpoint pair list (a) colonized records that changed and the exact changed
intra-record offsets (b) count of orbit-pair movers. Colonized = NAME+0x28
block nonzero (law: per-settled-colony block, r1-savestate 2026-10-06d).

Usage: r1_ckdiff.py --run-dir DIR [--ck-dir DIR/ck] [--only NAME]
Exit 0 always (report tool).
"""
import os, re, sys, struct, zipfile, argparse, math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAY = os.path.join(ROOT, "work", "ascend_payload.bin")


def load_slots(src):
    pay = open(PAY, "rb").read()
    anch = build_anchors(pay)
    out = []
    for f in sorted(os.listdir(src)):
        if not f.endswith(".sav"):
            continue
        try:
            m = zipfile.ZipFile(os.path.join(src, f)).read("Memory")
        except Exception:
            print(f"{f}: CORRUPT (skipped)")
            continue
        v, _ = find_base(m, anch)
        if not v:
            print(f"{f}: no base (skipped)")
            continue
        H = v.most_common(1)[0][0] - 0x1BF450
        out.append((f, m, H))
    return out


NAME_RE = re.compile(rb"([A-Za-z][A-Za-z\-'. ]{2,28}[\- ])(\d{1,2}|[IVX]{1,4})\x00")
# RAM stores ordinals BOTH ways across campaigns (Arabic in some maps, Roman
# in others - measured 2026-10-06j: r1ad-144225 'Flammifer II' is Roman;
# Byzantium run Arabic matched \d). Match both; never assume one.


def planets(m, H):
    """name-offset -> planet name (grid window law: 0x255b00..0x27a000)."""
    res = {}
    for mm in NAME_RE.finditer(m[H + 0x255B00:H + 0x27A000]):
        nm = mm.group(1).decode(errors="replace").strip()
        res[mm.start() + H] = nm
    return res


def turn(m, H):
    return struct.unpack_from("<H", m, 0x254E10 + H)[0]


def colonized(m, H):
    res = {}
    for p, nm in planets(m, H).items():
        if any(m[p + 0x28 + k] for k in range(9)):
            res[p] = nm
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--ck-dir")
    ap.add_argument("--only", help="filter to one planet name substring")
    a = ap.parse_args()
    src = a.ck_dir or os.path.join(a.run_dir, "ck")
    if not os.path.isdir(src):
        src = os.path.join(a.run_dir, "save")
    slots = load_slots(src)
    print(f"checkpoints: {len(slots)}")
    turns = [turn(m, H) for _, m, H in slots]
    print("turns:", turns)
    for i in range(len(slots) - 1):
        fa, m1, H1 = slots[i]
        fb, m2, H2 = slots[i + 1]
        c1, c2 = colonized(m1, H1), colonized(m2, H2)
        changed = {}
        for p, nm in c1.items():
            if p not in c2:
                changed[nm] = "DECOLONIZED"
                continue
            offs = [o for o in range(0, 123) if m1[p + o] != m2[p + o]]
            if offs:
                changed[nm] = offs
        # orbit movers over ALL planets (not just colonized)
        pv1, pv2 = planets(m1, H1), planets(m2, H2)
        orb = 0
        for p in pv1:
            if p in pv2:
                v1 = struct.unpack_from("<f", m1, p + 0x57)[0], struct.unpack_from("<f", m1, p + 0x5F)[0]
                v2 = struct.unpack_from("<f", m2, p + 0x57)[0], struct.unpack_from("<f", m2, p + 0x5F)[0]
                if v1 != (0, 0) and v1 != v2:
                    orb += 1
        t1, t2 = turns[i], turns[i + 1]
        tag = "TURN-BOUNDARY" if t2 > t1 else "intra-turn"
        filt = {k: v for k, v in changed.items() if (not a.only or a.only.lower() in k.lower())}
        print(f"{fa}->{fb} t{t1}->{t2} [{tag}] orbit_movers={orb} colonized_changed={len(changed)}")
        for nm, offs in list(filt.items())[:20]:
            print(f"    {nm!r}: {offs if offs != 'DECOLONIZED' else offs}")


if __name__ == "__main__":
    main()
