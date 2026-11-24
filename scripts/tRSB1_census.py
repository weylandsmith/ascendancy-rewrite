#!/usr/bin/env python3
# tRS-B1 witness census (tRS-V1c UPDATE): prove the set-project click
# produced visible feedback ON THE VENDOR-LAW RENDER. The pre-V1c gold-rim
# probe (230,160,40) is DEAD — the port now blits resring.shp frames (P10),
# it no longer paints vector rings in that RGB.
#  (1) right panel x484..632 y46..472: green text px count BEFORE == 0
#      (t268 law: no-project panel BLANK) and > 0 AFTER (Current Project:);
#  (2) LOCAL leg: pixels inside a 40px box about the clicked centre must
#      CHANGE after the click (frame 1 -> selection frame 2 + Study frame 0
#      + the 0xf3 edge repaint — the vendor selection chain paints AT the
#      disk).
# PASS = both legs. Exit 0/1.
import sys
from PIL import Image

before = Image.open(sys.argv[1]).convert("RGB")
after = Image.open(sys.argv[2]).convert("RGB")
cx, cy = int(sys.argv[3]), int(sys.argv[4])

def green_px(img):
    n = 0
    for y in range(46, 473):
        for x in range(484, 633):
            r, g, b = img.getpixel((x, y))
            if g > 150 and r < 100 and b < 150:
                n += 1
    return n

def changed_near(img_a, img_b, half=40):
    n = 0
    for y in range(max(0, cy - half), min(480, cy + half)):
        for x in range(max(0, cx - half), min(640, cx + half)):
            if img_a.getpixel((x, y)) != img_b.getpixel((x, y)):
                n += 1
    return n

gb, ga = green_px(before), green_px(after)
kc = changed_near(before, after)
print(f"panel-green before={gb} after={ga}")
print(f"changed-px within 40 of ({cx},{cy}) = {kc}")
ok = gb == 0 and ga > 0 and kc > 40
print("VERDICT", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
