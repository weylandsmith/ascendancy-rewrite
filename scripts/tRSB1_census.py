#!/usr/bin/env python3
# tRS-B1 witness census: prove the set-project click produced visible
# feedback. Compares before/after shots:
#  (1) right panel x484..632 y46..472: green text px count BEFORE ~0
#      (t268 law: no-project panel BLANK) and > 0 AFTER (Current Project:);
#  (2) gold-rim ring pixels (230,160,40) near the clicked node AFTER, ~0
#      BEFORE (the Study state rim, ui.cpp ring law).
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

def gold_px(img):
    n = 0
    for y in range(max(0, cy - 40), min(480, cy + 40)):
        for x in range(max(0, cx - 40), min(640, cx + 40)):
            r, g, b = img.getpixel((x, y))
            if abs(r - 230) < 30 and abs(g - 160) < 40 and b < 80:
                n += 1
    return n

gb, ga = green_px(before), green_px(after)
kb, ka = gold_px(before), gold_px(after)
print(f"panel-green before={gb} after={ga}")
print(f"gold-rim near({cx},{cy}) before={kb} after={ka}")
ok = gb == 0 and ga > 0 and ka > 0 and ka - kb > 20
print("VERDICT", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
