#!/usr/bin/env bash
# t428 strip witness: boot -> RESUME -> STATUS rail -> row click (state 17)
# -> shot; census the five-panel strip on OUR render
# (scripts/t428_witness_census.py). Prints VERDICT PASS/FAIL.
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/t428_shots}
DISP=${DISP:-:98}
rm -rf "$OUT"; mkdir -p "$OUT"
pgrep -f "Xvfb $DISP" >/dev/null || { Xvfb $DISP -screen 0 1024x768x24 >/dev/null 2>&1 & }
sleep 2
DISPLAY=$DISP SDL_AUDIODRIVER=dummy "$BIN" --data /tmp/uishow --ui --campaign 1 \
  --seed 5 --species 0 >"$OUT/app.log" 2>&1 &
APP=$!
trap 'kill $APP 2>/dev/null || true' EXIT
sleep 4
X() { DISPLAY=$DISP ./tools/xsend Ascendancy "$@"; sleep 0.5; }
X 318 335            # RESUME -> campaign map
X 553 145            # STATUS rail -> planets list
sleep 1
X 300 100            # row 0 -> planet view (state 17)
sleep 1
DISPLAY=$DISP import -window root "$OUT/full.png" 2>>"$OUT/app.log"
WP=$(DISPLAY=$DISP ./tools/winpos Ascendancy)
set -- $WP; WX=$1; WY=$2
~/tools/revenv/bin/python - "$WX" "$WY" <<'PY'
import sys
from PIL import Image
x, y = int(sys.argv[1]), int(sys.argv[2])
Image.open("/tmp/t428_shots/full.png").convert("RGB").crop(
    (x, y, x + 640, y + 480)).save("/tmp/t428_shots/crop.png")
print("crop at", x, y)
PY
~/tools/revenv/bin/python scripts/t428_witness_census.py "$OUT/crop.png"
