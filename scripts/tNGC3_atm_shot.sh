#!/usr/bin/env bash
# tNG-C3: capture the atmosphere wheel at all three states (k10/k11/k12)
# from OUR build, plus density/species panels, for the G1 sliver hunt.
set -u
cd /home/hrethric/projects/ascendancy
BIN=./rewrite/build/ascendancy
OUT=/tmp/tNGC3_atm
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
DISPLAY=$DISP ./tools/xsend "Ascendancy" click 320 60 2>>"$OUT/app.log"   # neutral
sleep 1
DISPLAY=$DISP ./tools/xsend "Ascendancy" click 318 295 2>>"$OUT/app.log"  # FRESHGAME -> raceconfig
sleep 1
DISPLAY=$DISP import -window root "$OUT/atm0.png" 2>>"$OUT/app.log"
# Atmosphere panel centre ~ (312, 426); click wheel area to cycle (t289 drive law: click inside panel)
for k in 1 2; do
  DISPLAY=$DISP ./tools/xsend "Ascendancy" click 312 435 2>>"$OUT/app.log"
  sleep 1
  DISPLAY=$DISP import -window root "$OUT/atm$k.png" 2>>"$OUT/app.log"
done
# Species cycle x2 and density cycle x2 for extraneous-art check
for k in 1 2; do
  DISPLAY=$DISP ./tools/xsend "Ascendancy" click 188 435 2>>"$OUT/app.log"
  sleep 1
  DISPLAY=$DISP import -window root "$OUT/sp$k.png" 2>>"$OUT/app.log"
done
for k in 1 2; do
  DISPLAY=$DISP ./tools/xsend "Ascendancy" click 64 435 2>>"$OUT/app.log"
  sleep 1
  DISPLAY=$DISP import -window root "$OUT/dn$k.png" 2>>"$OUT/app.log"
done
# Begin panel starfield
DISPLAY=$DISP import -window root "$OUT/before_begin.png" 2>>"$OUT/app.log"
kill $APP 2>/dev/null
grep -E "raceconfig|refused|dimscheck" "$OUT/app.log" | head -30
ls "$OUT"
