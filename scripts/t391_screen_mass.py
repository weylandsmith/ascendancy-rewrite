#!/usr/bin/env python3
# t391 mechanical presentation census (run under a PIL-bearing python).
# Per screenshot: window-crop non-bg mass + distinct-colour count, and for
# the STATUS shot a backdrop check: the 10status k0 plane mapped through the
# SAME luminance-ramp blit path can't be compared pixel-exact here, so the
# mechanical test is mass-based: a vector-only screen has mass in the
# hundreds (frame lines + glyphs); an art-backed screen has mass in the
# 100k+ range (t390 art-zone law: 124,800). Print verdict per screen against
# the S4 table in docs/re/_wip_t391.md.
import sys, os
from collections import Counter
from PIL import Image

OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/t391_shots"
EXPECT = {  # name: expected class. 'art' = mass > 50000 (backdrop blitted);
    # 'vector' = mass < 5000 (frame lines + glyphs only, NO art);
    # 'content' = 5000..50000: vector chrome PLUS vector CONTENT (the map
    # itself: stars/lanes/rail) — legitimately not art-backed per S4.
    "title": "art", "load": "art", "map": "content", "status": "art",
    "fleet": "vector", "research": "vector", "species": "content",
    "intel": "vector",
}
BG = {(10, 12, 26), (0, 0, 0)}
fails = 0
for name, want in EXPECT.items():
    p = os.path.join(OUT, name + ".png")
    if not os.path.isfile(p):
        print(f"{name:<9} MISSING"); fails += 1; continue
    im = Image.open(p).convert("RGB")
    W, H = im.size
    ox, oy = (W - 640) // 2, (H - 480) // 2
    px = im.load()
    c = Counter(px[ox + x, oy + y] for y in range(480) for x in range(640))
    # Per-shot background = dominant colour (each screen clears to its own
    # kBg; the title band differs too). Mass = everything that is NOT the
    # dominant colour (t390 law shape).
    bgc, bgn = c.most_common(1)[0]
    mass = sum(n for col, n in c.items() if col != bgc)
    got = "art" if mass > 50000 else ("vector" if mass < 5000 else "content")
    ok = got == want
    fails += 0 if ok else 1
    print(f"{name:<9} {got:<6} want={want:<6} mass={mass:<7} bg={bgc} "
          f"distinct={len(c):<5} {'OK' if ok else 'MISMATCH'}")
print("VERDICT", "PASS" if fails == 0 else f"FAIL({fails})")
sys.exit(0 if fails == 0 else 1)
