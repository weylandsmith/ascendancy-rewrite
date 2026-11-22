#!/usr/bin/env bash
# tNG-B B2 WITNESS: the species wheel re-rolls the ROSTER while the star
# SET IS PRESERVED (vendor 0x52e58..0x52ecc calls FUN_00022ce4 race
# assignment, NOT the density arm's full regen 0x226e4). Law
# docs/re/_wip_tNGB.md 'B2 SPECIES ARM FULL DECODE'.
# Captures: default screen (vendor-default Five == k7) + four clicks.
set -u
cd /home/hrethric/projects/ascendancy
BIN=./rewrite/build/ascendancy
OUT=/tmp/tNGB_species
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
DISPLAY=$DISP import -window root "$OUT/spec0.png" 2>>"$OUT/app.log"
# Species panel centre ~ (188,435) (kNewgameControls[1].rect 131..246 x 381..472)
for k in 1 2 3 4; do
  DISPLAY=$DISP ./tools/xsend "Ascendancy" click 188 435 2>>"$OUT/app.log"
  sleep 1
  DISPLAY=$DISP import -window root "$OUT/spec$k.png" 2>>"$OUT/app.log"
done
kill $APP 2>/dev/null
grep -E "raceconfig roster|raceconfig click SPECIES" "$OUT/app.log"
echo SHOTS "$OUT"/spec*.png
