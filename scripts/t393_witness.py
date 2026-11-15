#!/usr/bin/env python3
# t393 mechanical witness (our OWN render — self-graded VISION stays banned;
# pixel COUNTING is mechanical, per the t390/t392 precedent). Reads the
# screenshots scripts/t393_newgame_witness.sh just produced and asserts the
# screen law + panel/ink presence laws from docs/re/_wip_t393.md.
# RUN WITH: ~/tools/revenv/bin/python (PIL 12.x; the repo .venv has no PIL —
# same interpreter law as scripts/r1_t182_pngdump.py).
import sys
from collections import Counter

from PIL import Image

OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/t393_shots"
fails = []


def check(name, ok, detail=""):
    print(f"{name}: {'PASS' if ok else 'FAIL'} {detail}")
    if not ok:
        fails.append(name)


im = Image.open(f"{OUT}/t393-newgame.png").convert("RGB")
check("screenshot_is_640x480", im.size == (640, 480), str(im.size))
px = im.load()

# SCREEN LAW: the title screen's button fill (0,0,8) appears NOWHERE on the
# New Game screen (t393 switched RaceConfig from overlay to full screen).
fill = sum(1 for y in range(480) for x in range(640) if px[x, y] == (0, 0, 8))
check("screen_law_no_title_fill", fill == 0, f"fill px={fill}")

# Panel navy (12,32,48) present in every bottom-row zone.
zones = {
    "GALAXY_MORE": (7, 381, 122, 472), "PLAYERS_MORE": (131, 381, 246, 472),
    "DIFFICULTYMORE": (255, 381, 370, 472), "PlayerColor": (379, 381, 493, 419),
    "BEGIN": (494, 373, 639, 472), "RACELIST": (502, 45, 632, 372),
}
for nm, (a, b, c, d) in zones.items():
    navy = sum(1 for y in range(b + 1, d) for x in range(a + 1, c)
               if px[x, y] == (12, 32, 48))
    check(f"navy_{nm}", navy > 1000, f"px={navy}")

# Green ink (lore/name law): NEWGAMEWND lore rows + name rows.
green = lambda p: len(p) == 3 and p[1] > 100 and p[0] < 80 and p[2] < 100
lore = sum(1 for y in range(258, 331) for x in range(334, 489)
           if green(px[x, y]))
name = sum(1 for y in range(12, 32) for x in range(334, 489) if green(px[x, y]))
check("lore_green_ink", lore > 300, f"px={lore}")
check("name_green_ink", name > 20, f"px={name}")

# Starfield backdrop: lanes grey (120,120,120) present in the left zone.
lane = sum(1 for y in range(0, 320) for x in range(0, 465)
           if px[x, y] == (120, 120, 120))
check("backdrop_lanes_present", lane > 500, f"px={lane}")

# Portrait-seam discs: grey (128,128,128) inside RACELIST.
disc = sum(1 for y in range(46, 373) for x in range(503, 633)
           if px[x, y] == (128, 128, 128))
check("racelist_discs", disc > 5000, f"px={disc}")

# After Begin: the campaign bg (16,16,24) dominates (play was entered).
ab = Image.open(f"{OUT}/t393-after-begin.png").convert("RGB")
c = Counter(ab.getdata())
check("begin_enters_campaign", c.get((16, 16, 24), 0) > 100000,
      f"bg px={c.get((16, 16, 24), 0)}")

print("WITNESS_T393", "PASS" if not fails else f"FAIL {fails}")
sys.exit(1 if fails else 0)
