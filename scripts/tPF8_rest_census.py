#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""tPF-8 rest-state pixel census (law docs/re/_wip_tPF8.md P1-P3).

At game start the vendor paints EXACTLY the three root disks (rows 0/2/6)
and NOTHING else (edge law 0x48275 gates both endpoints on 0x46d3c; all
non-root rows are illegal under the zero-mask start law). Legs:
  (a) every non-background connected component inside the RESWIN clip is a
      ring-sized disk (bbox 40..75 per side) — no stray circles;
  (b) exactly THREE such components;
  (c) the component centres sit near the app's own logged root centres.
Background = the port's flat field fill (mode colour of the strip).
Exit 0 = PASS, 1 = FAIL, 2 = harness.
"""
import sys
from collections import Counter, deque
from PIL import Image

IMG, LOGX, LOGY = sys.argv[1], None, None
if len(sys.argv) > 3:
    LOGX, LOGY = int(sys.argv[2]), int(sys.argv[3])

im = Image.open(IMG).convert("RGB")
# Tree-field crop: inside the RESWIN (tPRU law (8,46)-(476,472)) minus the
# always-present chrome the tree law says nothing about: row y=46 is the
# header/field boundary line (full-width at rest in every build) and
# y>=456 is the bottom panel text row (t252 panel). The three root disks
# live at y 210..373 (k=0 arithmetic), far from both edges.
X0, Y0, X1, Y1 = 8, 47, 476, 455
px = im.load()
strip = [px[x, 470] for x in range(X0, X1)]
bg = Counter(strip).most_common(1)[0][0]

def far(a, b):  # luminance+chroma distance, colour-blind-safe magnitude
    return abs(a[0]-b[0]) + abs(a[1]-b[1]) + abs(a[2]-b[2])

seen = [[False]*(X1-X0) for _ in range(Y1-Y0)]
comps = []
for yy in range(Y1-Y0):
    for xx in range(X1-X0):
        if seen[yy][xx] or far(px[X0+xx, Y0+yy], bg) <= 24:
            continue
        q = deque([(xx, yy)]); seen[yy][xx] = True
        n = 0; xmn = xmx = xx; ymn = ymx = yy
        while q:
            x, y = q.popleft(); n += 1
            xmn, xmx = min(xmn, x), max(xmx, x)
            ymn, ymx = min(ymn, y), max(ymx, y)
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nx, ny = x+dx, y+dy
                if 0 <= nx < X1-X0 and 0 <= ny < Y1-Y0 and not seen[ny][nx] \
                        and far(px[X0+nx, Y0+ny], bg) > 24:
                    seen[ny][nx] = True; q.append((nx, ny))
        comps.append((n, xmn+X0, xmx+X0, ymn+Y0, ymx+Y0))

rings = [c for c in comps if 40 <= c[2]-c[1] <= 75 and 40 <= c[4]-c[3] <= 75]
strays = [c for c in comps if c not in rings and c[0] >= 12]
print(f"bg={bg} comps={len(comps)} ring-sized={len(rings)} strays>=12px={len(strays)}")
for c in sorted(comps, key=lambda c: -c[0])[:8]:
    print(f"  n={c[0]} x[{c[1]}..{c[2]}] y[{c[3]}..{c[4]}]"
          f" centre=({(c[1]+c[2])//2},{(c[3]+c[4])//2})")

ok = len(rings) == 3 and not strays
if ok and LOGX is not None:
    cx = sum((c[1]+c[2])//2 for c in rings)/3
    cy = sum((c[3]+c[4])//2 for c in rings)/3
    # the logged centre is ONE of the three roots; require it within +-35 of
    # at least one component centre
    ok = any(abs(LOGX-(c[1]+c[2])//2) <= 35 and abs(LOGY-(c[3]+c[4])//2) <= 35
             for c in rings)
print("VERDICT", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
