#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""t401 witness census — MECHANICAL checks of OUR OWN New Game render
(R13-safe: geometry/mass counting on our render; look-grading stays USER's).
Checks (laws docs/re/t401-newgame-art.md S10):
 1. DESC panel interior is SOLID (starfield cannot show through): the black
    fill covers the panel; star-preview px (neutral grey dots) inside the
    panel rect == 0 outside drawn art... simplified decisive form: the
    panel rect contains NO pure-black holes between art rows 30..250 on the
    fill rows — count pure-black px fraction INSIDE the lore band region
    between text rows (must be >90% black fill, i.e. no stars: stars are
    (120,120,120)-ish dots on black; census star-ish px inside NEWGAMEWND).
 2. RACELIST row zones contain CHROMATIC portrait px (smrace through
    game.pal) — each of the three row bands has chroma px count > 200.
 3. DESC crest zone (441,205,14x24) contains raceflag green (0,170,81) or
    (0,85,40).
 4. DESC ring: green (0,142,69) px arc pixels near r=52 of (409,97) >= 100.
 5. Bottom-row wheels: the three panels contain DIFFERENT dominant chroma
    signatures (k2 dots / k7 icons / k10 orb at the default values
    50/7/1... default species setting is 7 -> k9; atmosphere Neutral -> k10):
    assert per-panel chroma px > 300 AND panel0 dominant != panel1 dominant.
 6. Begin box: dot-cluster px present in band (496..570) > 100 AND portrait
    chroma inside emblem rect > 100.
 7. Page texture: left margin x0..6 full-height coverage in the t400 §4
    colour set (>= 95% of margin px in set+black), right band x>=494 has
    texture px present (>= 2000 outside panels? panels cover much; count
    texture-set px in x494..501 gutter).
Exit 0 iff all PASS; prints a per-check line.
"""
import sys
from PIL import Image
from collections import Counter

SHOTS = sys.argv[1:] or ["/tmp/t401_shots/t401-newgame.png"]

TEX = {(77,113,117),(85,125,125),(97,146,146),(69,105,109),(97,97,97),
       (89,134,138),(89,89,89),(60,93,97),(73,73,85),(48,77,81),
       (105,154,154),(81,81,81),(36,56,60),(0,0,0)}
GREENS = {(0,142,69),(0,170,81),(0,85,40)}

def run():
    ok = True
    for shot in SHOTS:
        im = Image.open(shot).convert("RGB")
        if im.size != (640, 480):
            print(f"FAIL {shot}: size {im.size} != 640x480 (scaled window?)")
            ok = False
            continue
        px = im.load()
        def zone(x0,y0,x1,y1):
            return [px[x,y] for y in range(y0,y1+1) for x in range(x0,x1+1)]
        # 1) star preview must NOT be inside NEWGAMEWND: star dots are the
        # neutral grey kNeutralRgb (120,120,120)-class ON black; the panel
        # fill is pure black. Count px equal to neutral-class greys 100..140
        # inside NEWGAMEWND rows 30..250 excluding the silver rings (rings
        # are near their own circles; rows 30..250 x full width includes
        # ring px — restrict to x 336..356 + 462..486 margins INSIDE panel
        # where nothing else draws).
        margin = zone(336,30,356,250) + zone(462,30,486,250)
        starish = sum(1 for c in margin if 100 <= c[0] <= 140 and abs(c[0]-c[1])<=6 and abs(c[1]-c[2])<=6)
        p1 = starish == 0
        # panel interior pure-black coverage overall
        black = sum(1 for c in zone(334,12,488,364) if c==(0,0,0))
        p1b = black > 20000
        print(f"{'PASS' if p1 and p1b else 'FAIL'} {shot}: desc-panel solid (starish-in-margin {starish}, black {black})")
        ok &= p1 and p1b
        # 2) RACELIST row chroma
        chroma_ok = True
        for i in range(3):
            cy = 49 + i*108 + 54
            zs = zone(512, cy-40, 606, cy+40)
            ch = sum(1 for c in zs if max(c)-min(c) > 35)
            chroma_ok &= ch > 200
            if ch <= 200: print(f"  row {i} chroma {ch} <= 200")
        print(f"{'PASS' if chroma_ok else 'FAIL'} {shot}: RACELIST portraits chromatic")
        ok &= chroma_ok
        # 3) crest green
        crest = zone(441,205,454,228)
        cg = sum(1 for c in crest if c in {(0,170,81),(0,85,40)})
        p3 = cg > 20
        print(f"{'PASS' if p3 else 'FAIL'} {shot}: crest raceflag-green px {cg}")
        ok &= p3
        # 4) desc ring green
        import math
        ring = 0
        for a in range(0,3600):
            rad = a*math.pi/1800
            x = 409 + int(52*math.cos(rad)); y = 97 + int(52*math.sin(rad))
            if 0<=x<640 and 0<=y<480 and px[x,y]==(0,142,69): ring += 1
        p4 = ring >= 100
        print(f"{'PASS' if p4 else 'FAIL'} {shot}: desc ring green px {ring}")
        ok &= p4
        # 5) bottom-row wheels: each panel shows a wheel with real chroma
        # AND the three panels show DIFFERENT content (the pre-t401 defect
        # was k0 blitted into every panel; identical zone content = that bug
        # returning). Dominant colour is NOT a valid discriminator (the
        # frame family shares fill colours — measured this session).
        wheels_ok = True
        zones = []
        sigs = []
        for (x0,x1) in [(7,122),(131,246),(255,370)]:
            cx = (x0+x1)//2
            zs = zone(cx-28, 408, cx+27, 462)
            zones.append(zs)
            ch = sum(1 for c in zs if max(c)-min(c) > 35)
            sigs.append(ch)
            wheels_ok &= ch > 300
        same = sum(1 for a, b in zip(zones[0], zones[1]) if a == b)
        p5 = wheels_ok and same < len(zones[0]) * 0.5
        print(f"{'PASS' if p5 else 'FAIL'} {shot}: wheels chroma {sigs}, "
              f"panel0==panel1 px {same}/{len(zones[0])}")
        ok &= p5
        # 6) begin box dots + emblem chroma
        dots = sum(1 for c in zone(496,390,570,446)
                   if c in {(255,255,255),(225,227,229),(164,171,177),
                            (103,116,126),(97,97,97),(69,105,109)})
        emb = sum(1 for c in zone(577,394,625,442) if max(c)-min(c) > 35)
        p6 = dots > 100 and emb > 100
        print(f"{'PASS' if p6 else 'FAIL'} {shot}: begin dots {dots}, emblem chroma {emb}")
        ok &= p6
        # 7) page texture
        left = zone(0,0,6,479)
        inset = sum(1 for c in left if c in TEX)
        gutter = zone(494,0,501,479)
        gin = sum(1 for c in gutter if c in TEX)
        p7 = inset >= int(len(left)*0.95) and gin > 1000
        print(f"{'PASS' if p7 else 'FAIL'} {shot}: texture left {inset}/{len(left)}, gutter {gin}")
        ok &= p7
    print("VERDICT", "PASS" if ok else "FAIL")
    return 0 if ok else 1

sys.exit(run())
