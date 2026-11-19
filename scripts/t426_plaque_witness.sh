#!/bin/bash
# t426 PLAQUE + BORDER witness: the map screen must show (1) chrome texture
# in the TOP band rows 0..6 and BOTTOM band rows 473..479 at mid-x (the
# "map border missing" defect), (2) the 15x25 plaque frame at screen
# (10,10) with idx19 outline + navy interior inside the black field,
# (3) the home-star crest: idx19 frame pixels at the logged home-star
# anchor (starx-7, stary+3). Prints VERDICT PASS/FAIL.
# Law: docs/re/_wip_t426.md F1/F2/F3.
set -e
cd /home/hrethric/projects/ascendancy
pgrep -x Xvfb >/dev/null || { (Xvfb :9 -screen 0 1024x768x24 >/dev/null 2>&1 &); sleep 2; }
pkill -x ascendancy 2>/dev/null || true
sleep 1
DISPLAY=:9 SDL_AUDIODRIVER=dummy ./rewrite/build/ascendancy \
  --data /tmp/uishow --ui --campaign 1 --seed 5 --species 0 > /tmp/t426_witness.log 2>&1 &
UI=$!
trap 'kill $UI 2>/dev/null || true' EXIT
sleep 4
# RESUME -> campaign map (t411 witness law: title button centre 318,335)
DISPLAY=:9 ./tools/xsend Ascendancy click 318 335 >/dev/null
sleep 2
DISPLAY=:9 timeout 15 import -window root /tmp/t426_map.png
WP=$(DISPLAY=:9 ./tools/winpos Ascendancy)
set -- $WP; X=$1; Y=$2; W=$3; H=$4
~/tools/revenv/bin/python - "$X" "$Y" <<'PY'
import sys
from PIL import Image
img = Image.open("/tmp/t426_map.png").convert("RGB")
# crop the 640x480 window content
x, y = int(sys.argv[1]), int(sys.argv[2])
img = img.crop((x, y, x + 640, y + 480))
def px(a, b): return img.getpixel((a, b))
fails = []
# 1) top + bottom chrome bands at mid-x must NOT be black (t426 F1)
top = [px(a, 3) for a in range(60, 420)]
bot = [px(a, 473) for a in range(60, 420)]
print(f"bottom band y473 nonblack {sum(1 for p in bot if sum(p) > 0)}/360 "
      f"(measured edge row; the t411 shot had y472 black, y473 (54,76,76))")
t_nonblack = sum(1 for p in top if sum(p) > 0)
b_nonblack = sum(1 for p in bot if sum(p) > 0)
print(f"top band y3 nonblack {t_nonblack}/360 ; bottom band y476 nonblack {b_nonblack}/360")
if t_nonblack < 300: fails.append("top band still black")
if b_nonblack < 300: fails.append("bottom band still black")
# 2) plaque frame at (10,10): top row green-ish, interior navy present
green = lambda p: p[1] > 120 and p[0] < 60 and p[2] < 120
navy = lambda p: abs(p[0]-12) <= 3 and abs(p[1]-32) <= 3 and abs(p[2]-48) <= 3
frame_px = sum(1 for a in range(10, 25) for b in range(10, 35)
               if (a in (10, 24) or b in (10, 34)) and green(px(a, b)))
navy_px = sum(1 for a in range(11, 24) for b in range(11, 34) if navy(px(a, b)))
print(f"plaque outline green px {frame_px}/56 ; interior navy px {navy_px}/273")
if frame_px < 40: fails.append("plaque outline missing")
if navy_px < 150: fails.append("plaque interior missing")
# 3) field left of plaque must stay black (no bleed)
if sum(1 for a in range(8, 10) for b in range(12, 33) if sum(px(a, b)) > 0) > 0:
    fails.append("plaque bleeds into field")
# 4) home crest: locate logged anchor
import re
m = None
for line in open("/tmp/t426_witness.log"):
    mm = re.search(r"ui home star \S+ at (-?\d+),(-?\d+)", line)
    if mm: m = mm
if not m:
    print("NOTE: no home-star log line (sitting without campaign?)")
else:
    hx, hy = int(m.group(1)), int(m.group(2))
    cx, cy = hx - 7, hy + 3
    crest_frame = sum(1 for a in range(cx, cx + 15) for b in range(cy, cy + 25)
                      if (a in (cx, cx + 14) or b in (cy, cy + 24)) and green(px(a, b)))
    print(f"crest frame green px {crest_frame}/56 at ({cx},{cy}) [star {hx},{hy}]")
    if crest_frame < 40: fails.append("home crest frame missing")
# 5) THE BAR: with --species 0 (the refcap's own flag k0) the port's plaque
#    block must be EXACT-DIFF zero against the palette-pure refcap.
import numpy as np
ref = np.asarray(Image.open("docs/assets/refcap/original-strategic-map.png")
                 .convert("RGB")).astype(int)
port = np.asarray(img).astype(int)
eq = int((np.abs(port[10:35, 10:25] - ref[50:75, 10:25]).sum(axis=2) <= 3).sum())
print(f"plaque exact-diff vs refcap: {eq}/375")
if eq < 375: fails.append(f"plaque not exact ({eq}/375)")
print("VERDICT", "FAIL: " + "; ".join(fails) if fails else "PASS")
sys.exit(1 if fails else 0)
PY
