#!/usr/bin/env bash
# t423 witness: New Game screen with atmosphere cycled to Hostile (k12).
set -u
cd /home/hrethric/projects/ascendancy
BIN=./rewrite/build/ascendancy
OUT=/tmp/t423_shots
DISP=${DISP:-:97}
rm -rf "$OUT"; mkdir -p "$OUT"
pkill -x ascendancy 2>/dev/null || true
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP SDL_AUDIODRIVER=dummy "$BIN" --data /tmp/uishow --ui --campaign 1 --seed 5 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 4
DISPLAY=$DISP ./tools/xsend "Ascendancy" click 320 60 2>>"$OUT/app.log"
sleep 1
DISPLAY=$DISP ./tools/xsend "Ascendancy" click 318 295 2>>"$OUT/app.log"
sleep 1
# Atmosphere panel centre (255,381)-(370,472) per windows.txt F0: start
# Neutral(1), ONE click -> Hostile(2).
DISPLAY=$DISP ./tools/xsend "Ascendancy" click 312 426 2>>"$OUT/app.log"
sleep 1
DISPLAY=$DISP import -window root "$OUT/t423-hostile.png" 2>>"$OUT/app.log"
kill $APP 2>/dev/null; kill $XV 2>/dev/null
grep -E "atmosphere|refused" "$OUT/app.log" | tail -3
echo SHOT "$OUT/t423-hostile.png"
