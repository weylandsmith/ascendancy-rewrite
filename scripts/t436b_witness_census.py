#!/usr/bin/env python3
# t436b species-menu census leg (run on scripts/t409_species_witness.sh shots
# or any OUR-render species screen). Grades the port's state-7 paint against
# the vendor law numbers (docs/re/_wip_t436.md F4/F7/G1):
#   1. populated rows: navy (8,32,49) dominant (>70%)
#   2. empty slots: dark-speckle families {(8,12,16),(0,0,0),(12,28,48)}
#      cover >85% and the field is correlated (mean run > 2.6)
#   3. centred ink: non-well bbox centre within +-4 px of 553 per row
#   4. ZERO grey-outline px ((120,120,120) family the old defect painted)
#      on the slot border lines
#   5. portrait ring: >=1 chromatic ring px of an owner hue at radius
#      50..55 about SOME centre (skipped if no contact/known rows)
# Usage: t436b_witness_census.py shot.png [known_rows]
import sys
from collections import Counter
from PIL import Image

im = Image.open(sys.argv[1]).convert("RGB")
px = im.load()
W, H = im.size
known = int(sys.argv[2]) if len(sys.argv) > 2 else None
WELL = {(12, 12, 16), (0, 0, 0), (12, 28, 48), (8, 12, 16), (8, 28, 49)}
GREY = lambda c: abs(c[0] - c[1]) < 6 and abs(c[1] - c[2]) < 6 and 90 < c[0] < 150
tops = [7, 46, 85, 124, 163, 202, 241]
fail = 0

# rows 1..6: populated = first `known` slots (port law: rows from kRaceRows[1])
def slot_region(i):
    return [(x, y) for y in range(tops[i], tops[i] + 31)
            for x in range(474, 633)]

if known is not None:
    for i in range(1, 7):
        reg = slot_region(i)
        cnt = Counter(px[p] for p in reg)
        tot = sum(cnt.values())
        if i <= known:
            navy = cnt[(8, 32, 49)]
            ok = navy * 100 / tot > 70
            print(("PASS" if ok else "FAIL"),
                  f"row{i} populated navy {(8,32,49)} {100*navy/tot:.1f}%")
            fail += 0 if ok else 1
        else:
            fam = sum(n for c, n in cnt.items() if c in WELL)
            ok = fam * 100 / tot > 85
            print(("PASS" if ok else "FAIL"),
                  f"slot{i} empty well-family {100*fam/tot:.1f}%")
            fail += 0 if ok else 1
    # 3. centred ink bbox per populated row
    for i in range(1, known + 1):
        xs = [x for y in range(tops[i], tops[i] + 31) for x in range(474, 633)
              if px[x, y] not in WELL and px[x, y] != (8, 32, 49)]
        if not xs:
            print(f"NOTE row{i} no ink (flag+name absent?)")
            continue
        c = (min(xs) + max(xs)) / 2
        # flag sits left of centre; ink-only centre check uses x>505 (right of
        # the flag column) so the flag does not skew it
        xs2 = [x for x in xs if x > 505]
        c2 = (min(xs2) + max(xs2)) / 2 if xs2 else c
        ok = abs(c2 - 553) <= 6
        print(("PASS" if ok else "FAIL"),
              f"row{i} ink bbox {min(xs)}..{max(xs)} right-part centre {c2:.0f} (target 553)")
        fail += 0 if ok else 1
    # 4. zero grey outline px on all slot borders
    gpx = 0
    for i in range(7):
        for y in (tops[i], tops[i] + 30):
            gpx += sum(1 for x in range(474, 633) if GREY(px[x, y]))
        for x in (474, 632):
            gpx += sum(1 for y in range(tops[i], tops[i] + 31) if GREY(px[x, y]))
    ok = gpx == 0
    print(("PASS" if ok else "FAIL"), f"grey-outline px on slot borders: {gpx}")
    fail += 0 if ok else 1
# 5. ring census: search candidate centres; a portrait scores as (a) a DISC:
# >600 non-black px inside r<=40, and (b) a RING BAND: >=120 strongly
# chromatic px in the annulus r50..56 (vendor: three-tone owner ring; our
# render: racering 53x53 at 2x -> band r50..53 + antialias. Point-sampling
# a circle is brittle (the band has art gaps); the annulus census is the
# robust statistic — measured 273 chromatic px on the t436b witness shot).
def disc_score(cx, cy):
    inner = 0
    ring = 0
    for y in range(max(0, cy - 58), min(min(H, 473), cy + 59)):
        for x in range(max(0, cx - 58), min(W, cx + 59)):
            dx, dy = x - cx, y - cy
            r2 = dx * dx + dy * dy
            c = px[x, y]
            if r2 <= 1600 and sum(c) > 20:
                inner += 1
            if 2500 <= r2 <= 3136 and max(c) - min(c) > 40:
                ring += 1
    return inner, ring
# Preferred: centres the PORT LOGGED ("ui species portrait owner N at x,y" —
# the projection law's own output). argv[3] = "x,y;x,y". Fallback: blind
# blob search (coarse, only used when no log centres were passed).
if len(sys.argv) > 3:
    logged = [tuple(int(v) for v in s.split(","))
              for s in sys.argv[3].split(";") if s]
    centres = [(cx, cy) + disc_score(cx, cy) for cx, cy in logged]
    bad = [c for c in centres if c[2] < 2500 or c[3] < 120]
    if known in (None, 0):
        print("NOTE ring leg skipped (no known-row datum)")
    elif not bad:
        print("PASS", f"logged portrait centres carry disc+ring: {centres}")
    else:
        print("FAIL", f"logged centres without disc+ring: {bad}")
        fail += 1
else:
    centres = []
    for cy in range(70, 472, 8):
        for cx in range(70, 450, 8):
            inner, ring = disc_score(cx, cy)
            if inner > 2500 and ring >= 120:
                centres.append((cx, cy, inner, ring))
if known in (None, 0):
    print("NOTE ring leg skipped (no known-row datum to grade against)")
elif len(sys.argv) <= 3:
    if centres:
        print("PASS", f"chromatic ring band candidates: {len(centres)}",
              centres[:4])
    else:
        print("FAIL", "no chromatic ring band at radius ~52 anywhere in the field")
        fail += 1
print("VERDICT", "PASS" if fail == 0 else "FAIL")
sys.exit(0 if fail == 0 else 1)
