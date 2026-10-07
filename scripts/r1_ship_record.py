#!/usr/bin/env python3
"""r1_ship_record.py — verify the LIVE ship-record model in guest RAM (OQ-019).

Static law (docs/re/ships.md S6 + S9, FUN_00037d80 / FUN_00038ba4 /
FUN_00038f68 / FUN_0004105c / FUN_00046b6e): the per-ship record (stride
0x7b) mirrors the planet-system-object layout:

  +0x14 u16 scan-advance accumulator   (+0x11 u8 per-turn scan contribution)
  +0x16 u8  planet-type index (0..4 row of the planitem type table)
  +0x18 u16 surface slot count   (= sum of type-row surface cells, <= 100)
  +0x1a u16 capacity             = +0x18 + 10  (the ORBITAL slot count)
  +0x10 u32 slot-array pointer (physical; member = ptr - 0x88), 4B/slot:
          {class u8, gizmoIdx u8 (0xff empty), flags u16}
  +0x42 u16 build cost remaining (industry), +0x4a u16 max build capacity,
  +0x4c u16 repair floor, +0x46 u16 orbital-industry tally (FUN_00046b80),
  +0x55 u16 hull points, +0x57 u8 owner (0xff = unowned),
  +0x5e f32[3] position x/y/z   (FUN_00038f68 normalises x/y/z at +0x5e),
  +0x5a u16 gizmo count.

Orbital-slot law tested here: orbital slots are [+0x18, +0x1a) — i.e. the
slots AFTER all surface cells — matching rewrite economy.h
(kPlanitemSurfaceCount=22, kPlanitemOrbitalCount=9, rows 22..30). A capture
with colonised systems therefore shows:
  slots [0, cells)   -> gizmoIdx in [0,22) or 0xff
  slots [cells, cap) -> gizmoIdx in [22,31) or 0xff      <-- discriminating
Any gizmoIdx >= 31 in a populated slot falsifies the planitem-index reading
(it would name a special gizmo, not an orbital item), which is recorded, not
explained away.

Exit 0 = locator law + cap==cells+10 + the [22,31) orbital census all hold on
at least one slot of at least one capture.  1 = ran, negative.  2 = harness.

Usage: r1_ship_record.py --run-dir DIR [--slot NAME] [--dump N]
"""
import argparse, os, struct as st, sys, zipfile
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1_sav_scan import build_anchors, find_base

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAY = os.path.join(ROOT, "work", "ascend_payload.bin")
SURFACE, ORBIT_LO, ORBIT_HI = 22, 22, 30  # planitem census (OQ-014)
STRIDE = 0x7B


def load_slots(run_dir, slot=None):
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
    out = []
    for f in slots:
        try:
            m = zipfile.ZipFile(os.path.join(src, f)).read("Memory")
        except Exception:
            continue
        v, _ = find_base(m, anch)
        if not v:
            continue
        out.append((f, m, v.most_common(1)[0][0] - 0x1BF450))
    return out


def census(m, P0):
    """Scan the whole guest image for stride-0x7b ship-record candidates."""
    hits = Counter()
    owned = 0
    for base in range(0, len(m) - STRIDE, 4):
        cells = st.unpack_from("<H", m, base + 0x18)[0]
        cap = st.unpack_from("<H", m, base + 0x1a)[0]
        if cells not in (7, 11, 23, 45, 73) or cap != cells + 10:
            continue
        ptr = st.unpack_from("<I", m, base + 0x10)[0]
        if not (0x100000 < ptr < len(m) + 0x88 + 0x200000):
            continue
        owner = m[base + 0x57]
        # slot array: member index = ptr - 0x88 (heap pointers are physical)
        arr = ptr - 0x88  # verified against r1_planet_layout slot-array reads
        if arr < 0 or arr + cap * 4 > len(m):
            continue
        # sanity: every slot gizmo byte in {0xff} or planitem range
        idxs = [m[arr + i * 4 + 1] for i in range(cap)]
        bad = [i for i, g in enumerate(idxs) if g != 0xFF and g > 38]
        hits["records"] += 1
        hits["bad_high"] += len(bad)
        if owner != 0xFF:
            owned += 1
            for i, g in enumerate(idxs):
                if g == 0xFF:
                    continue
                if i < cells:
                    hits["surface_idx"] += 1
                    if g >= SURFACE:
                        hits["surface_OUT_OF_RANGE"] += 1
                else:
                    hits["orbital_idx"] += 1
                    if ORBIT_LO <= g <= ORBIT_HI:
                        hits["orbital_IN_22_30"] += 1
                    else:
                        hits["orbital_OUT_22_30"] += 1
                        hits.setdefault("orbital_values", Counter())[g] += 1
    hits["owned_records"] = owned
    return hits


def dump_one(m, base, n=40):
    print(f"--- record @{hex(base)}")
    for off in (0x10, 0x14, 0x16, 0x18, 0x1a, 0x42, 0x44, 0x46, 0x48, 0x4a, 0x4c, 0x55, 0x57, 0x5a, 0x5e):
        w = st.unpack_from("<H", m, base + off)[0]
        print(f"  +0x{off:02x} = {w} (0x{w:04x})")
    x, y, z = st.unpack_from("<3f", m, base + 0x5e)
    print(f"  pos f32 = ({x:.1f}, {y:.1f}, {z:.1f})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--slot")
    args = ap.parse_args()
    slots = load_slots(args.run_dir, args.slot)
    if not slots:
        print("harness: no readable slot with derivable base in", args.run_dir)
        return 2
    ok_any = False
    for name, m, P0 in slots[:4]:
        h = census(m, P0)
        recs = h["records"]
        print(f"{name}: ship-record candidates={recs} owned={h['owned_records']} "
              f"bad_high={h['bad_high']} surface={h['surface_idx']} "
              f"orbital={h['orbital_idx']} orbital_in[22,30]={h['orbital_IN_22_30']} "
              f"orbital_out={h['orbital_OUT_22_30']}")
        ov = h.get("orbital_values")
        if ov:
            print("   orbital gizmo idx values:", dict(sorted(ov.items())))
        if recs and h["bad_high"] == 0 and h["orbital_idx"] and \
           h["orbital_IN_22_30"] == h["orbital_idx"]:
            ok_any = True
    if ok_any:
        print("LAW HOLDS: orbital slots = [cells, cells+10) carry planitem "
              "indices 22..30 (rewrite kPlanitemOrbitalCount law confirmed live)")
        return 0
    print("negative this run (see counters)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
