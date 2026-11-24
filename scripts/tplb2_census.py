#!/usr/bin/env python3
"""tPL-B2 popup census (run over scripts/tplb2_port_witness.sh output).

Verdict law:
  1. each popup shot changes a LARGE fraction (>= 50%) of its OWN builder
     rect (wrec+10 origin, 0x145x0xcf — indpopups.h)  -> the popup painted;
  2. the no-overlap control (PLPRO shot vs rest inside the PLRES rect;
     the two builder rects are disjoint) changes ~0 px -> no leak;
  3. the dismissed shot is pixel-IDENTICAL to rest -> dismiss law holds.
Run: python3 scripts/tplb2_census.py [dir=/tmp/tplb2_shots]
"""
import sys
from PIL import Image

OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/tplb2_shots"
RECTS = {  # indicatorPopupRect(kPlanetPanels[i].rect) — indpopups.h law
    "plres": (17, 17, 246, 228),
    "plind": (133, 17, 332, 228),
    "plpro": (249, 17, 448, 228),
    "plpop": (365, 17, 564, 228),
}

def changed(a, b, box):
    ca, cb = a.crop(box), b.crop(box)
    pa, cb2 = list(ca.getdata()), list(cb.getdata())
    return sum(1 for x, y in zip(pa, cb2) if x != y), len(pa)

def main():
    rest = Image.open(f"{OUT}/rest.png").convert("RGB")
    fails = 0
    for k, r in RECTS.items():
        img = Image.open(f"{OUT}/popup-{k}.png").convert("RGB")
        d, tot = changed(rest, img, r)
        ok = d * 2 >= tot
        fails += 0 if ok else 1
        print(f"{k}: own-rect changed {d}/{tot} ({100*d/tot:.1f}%) {'OK' if ok else 'FAIL'}")
    img = Image.open(f"{OUT}/popup-plpro.png").convert("RGB")
    d, tot = changed(rest, img, RECTS["plres"])
    ok = d == 0
    fails += 0 if ok else 1
    print(f"control (plpro shot, PLRES rect): changed {d}/{tot} {'OK' if ok else 'FAIL'}")
    img = Image.open(f"{OUT}/dismissed.png").convert("RGB")
    d, tot = changed(rest, img, (0, 0, 640, 480))
    ok = d == 0
    fails += 0 if ok else 1
    print(f"dismissed vs rest: changed {d}/{tot} {'OK' if ok else 'FAIL'}")
    print("VERDICT", "PASS" if fails == 0 else f"FAIL ({fails})")
    return 0 if fails == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
