#!/usr/bin/env bash
# tNG-S S27 port witness: our New Game field must ANIMATE (pump 2deg/s).
# Grabs the newgame screen twice ~4 s apart; offline diff proves motion.
set -u
cd /home/hrethric/projects/ascendancy
BIN=./rewrite/build/ascendancy
OUT=/tmp/tngs4_ours
DISP=${DISP:-:97}
rm -rf "$OUT"; mkdir -p "$OUT"
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
DISPLAY=$DISP import -window root "$OUT/ng_t0.png" 2>>"$OUT/app.log"
sleep 4
DISPLAY=$DISP import -window root "$OUT/ng_t4.png" 2>>"$OUT/app.log"
kill $APP 2>/dev/null || true
kill $XV 2>/dev/null || true
echo DONE
