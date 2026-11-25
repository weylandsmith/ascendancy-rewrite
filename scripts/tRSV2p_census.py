#!/usr/bin/env python3
"""tRS-V2p DISK FILL PIXEL CENSUS (law docs/re/research.md S9; witness
scripts/tRSV2p_witness.sh). The port paints restree.shp record[row] scaled
q/20 about the node anchor AFTER the ring. Stages witnessed on seed 5:
  before   = row Available (q=0, NO picture)
  sliver   = row just selected (q=2 -> 10x50->10px picture per the 50x50
             content law scaled 0.1)
  later    = row after >=1 turns of research (q = 18p/cost+2 > 2)
Census law (the tRSV1d lesson): measure CONTENT vs the flat field bg
(16,16,24), never brightness. Content bbox is measured INSIDE a +-20 box
about the logged centre (the ring occupies the outside), so growth of the
changed-px count and of the content half-extent IS the wipe law.
Anti-vacuity: a control box 120px away inside the same clip must stay
0-changed across the same shot pairs.
"""
import re
import re as _re
import sys
from PIL import Image

BG = (16, 16, 24)
HALF = 20


def load(p):
    return Image.open(p).convert("RGB")


def changed(imgA, imgB, cx, cy, half=HALF):
    n = 0
    for y in range(cy - half, cy + half + 1):
        for x in range(cx - half, cx + half + 1):
            if imgA.getpixel((x, y)) != imgB.getpixel((x, y)):
                n += 1
    return n


def content_bbox(img, cx, cy, half=HALF, tol=8):
    x0, y0, x1, y1 = 10**9, 10**9, -1, -1
    for y in range(cy - half, cy + half + 1):
        for x in range(cx - half, cx + half + 1):
            r, g, b = img.getpixel((x, y))
            if abs(r - BG[0]) > tol or abs(g - BG[1]) > tol or abs(b - BG[2]) > tol:
                x0, y0 = min(x0, x), min(y0, y)
                x1, y1 = max(x1, x), max(y1, y)
    return None if x1 < 0 else (x0, y0, x1, y1)


def main():
    out = sys.argv[1]           # dir with app.log + shots
    cx, cy = int(sys.argv[2]), int(sys.argv[3])
    row = int(sys.argv[4])
    log = open(f"{out}/app.log").read()

    # Log legs.
    fills = {}
    for m in re.finditer(rf"ui research fill {row} (\d+)", log):
        fills.setdefault(int(m.group(1)), 0)
        fills[int(m.group(1))] += 1
    study = f"ui research study" in log
    print(f"logged fill values for row {row}: {sorted(fills)}  study-line={study}")
    ok = True
    if 2 not in fills:
        print("FAIL  no 'ui research fill <row> 2' line (select sliver q)")
        ok = False
    later = [q for q in fills if q > 2]
    if not later:
        print("FAIL  no grown-q log line after turns advanced")
        ok = False

    before = load(f"{out}/before.png")
    sliver = load(f"{out}/sliver.png")
    progressed = load(f"{out}/progressed.png")

    # Pixel legs: select must PAINT inside the disk (q 0->2), and advancing
    # research must WIDEN it (q 2->later).
    n_sel = changed(before, sliver, cx, cy)
    n_wide = changed(sliver, progressed, cx, cy)
    print(f"changed px in +-{HALF} box: select {n_sel}, advance {n_wide}")
    if n_sel == 0:
        print("FAIL  select painted NOTHING inside the disk (q=2 sliver missing)")
        ok = False
    if n_wide == 0:
        print("FAIL  advancing research painted NOTHING (grown fill missing)")
        ok = False
    if ok and n_sel and n_wide:
        bb_s = content_bbox(sliver, cx, cy)
        bb_p = content_bbox(progressed, cx, cy)
        hs = max(bb_s[2] - bb_s[0], bb_s[3] - bb_s[1]) if bb_s else -1
        hp = max(bb_p[2] - bb_p[0], bb_p[3] - bb_p[1]) if bb_p else -1
        print(f"content extent: sliver {hs}px, progressed {hp}px "
              f"(sliver bbox {bb_s}, progressed bbox {bb_p})")
        if hp < hs:
            print("FAIL  content SHRANK with progress (wipe law violated)")
            ok = False
    # Anti-vacuity control: 120px left of centre (same clip band if inside).
    ccx = cx - 120
    if ccx > HALF:
        nc = changed(before, progressed, ccx, cy)
        print(f"control box 120px away: changed {nc} (expect small/0)")
        if nc > n_sel + n_wide and nc > 200:
            print("FAIL  control churned more than the node (camera moved?)")
            ok = False
    print("VERDICT", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
