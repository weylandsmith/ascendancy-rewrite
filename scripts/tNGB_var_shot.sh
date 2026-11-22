#!/usr/bin/env bash
# tNG-B: same-state run-to-run noise probe (row-7 knife-edge autopsy).
set -u
cd /home/hrethric/projects/ascendancy
BIN=./rewrite/build/ascendancy
OUT=/tmp/tNGB_var
DISP=${DISP:-:97}
rm -rf "$OUT"; mkdir -p "$OUT"
pkill -x ascendancy 2>/dev/null || true
if ! pgrep -f "Xvfb $DISP" >/dev/null; then
  Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
  sleep 1
fi
DISPLAY=$DISP SDL_AUDIODRIVER=dummy "$BIN" --data /tmp/uishow --ui --campaign 1 --seed 5 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 4
DISPLAY=$DISP ./tools/xsend "Ascendancy" click 320 60 2>>"$OUT/app.log"
sleep 1
DISPLAY=$DISP ./tools/xsend "Ascendancy" click 318 295 2>>"$OUT/app.log"
sleep 1
DISPLAY=$DISP import -window root "$OUT/a.png" 2>>"$OUT/app.log"
sleep 1
DISPLAY=$DISP import -window root "$OUT/b.png" 2>>"$OUT/app.log"
sleep 1
DISPLAY=$DISP import -window root "$OUT/c.png" 2>>"$OUT/app.log"
kill $APP 2>/dev/null
echo DONE "$OUT"
