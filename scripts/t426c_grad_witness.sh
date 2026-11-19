#!/bin/bash
# t426c GRADIENT witness: shoot the map screen and census the top-band
# gradient law on OUR render (scripts/t426c_witness_census.py). Law
# docs/re/_wip_t426.md F6. Prints VERDICT PASS/FAIL.
set -e
cd /home/hrethric/projects/ascendancy
pgrep -x Xvfb >/dev/null || { (Xvfb :9 -screen 0 1024x768x24 >/dev/null 2>&1 &); sleep 2; }
pkill -x ascendancy 2>/dev/null || true
sleep 1
DISPLAY=:9 SDL_AUDIODRIVER=dummy ./rewrite/build/ascendancy \
  --data /tmp/uishow --ui --campaign 1 --seed 5 --species 0 >/tmp/t426c_witness.log 2>&1 &
UI=$!
trap 'kill $UI 2>/dev/null || true' EXIT
sleep 4
DISPLAY=:9 ./tools/xsend Ascendancy click 318 335 >/dev/null   # RESUME -> map
sleep 2
WP=$(DISPLAY=:9 ./tools/winpos Ascendancy)
set -- $WP; X=$1; Y=$2
DISPLAY=:9 timeout 15 import -window root /tmp/t426c_full.png
~/tools/revenv/bin/python - "$X" "$Y" <<'PY'
import sys
from PIL import Image
x, y = int(sys.argv[1]), int(sys.argv[2])
Image.open("/tmp/t426c_full.png").convert("RGB").crop(
    (x, y, x + 640, y + 480)).save("/tmp/t426c_map_crop.png")
print("crop cropped at", x, y)
PY
~/tools/revenv/bin/python scripts/t426c_witness_census.py /tmp/t426c_map_crop.png
