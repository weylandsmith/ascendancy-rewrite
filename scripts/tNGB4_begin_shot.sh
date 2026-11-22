#!/usr/bin/env bash
# tNG-B B4 WITNESS capture: the Begin press -> SETTINGS-APPLY seam.
# Law docs/re/_wip_tNGB.md 'B4 VERDICT'. Sequence on ONE app run:
#   open New Game -> atmosphere click (gov 1->2) -> species click (owners
#   5->6) -> density click (stars 50->75) -> BEGIN -> intro dismiss.
# The app.log carries the law lines the witness python checks.
set -u
cd /home/hrethric/projects/ascendancy
BIN=./rewrite/build/ascendancy
OUT=/tmp/tNGB4_begin
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
DISPLAY=$DISP ./tools/xsend "Ascendancy" click 320 60 2>>"$OUT/app.log"   # neutral (first-click law)
sleep 1
DISPLAY=$DISP ./tools/xsend "Ascendancy" click 318 295 2>>"$OUT/app.log"  # FRESHGAME -> raceconfig
sleep 1
DISPLAY=$DISP ./tools/xsend "Ascendancy" click 312 435 2>>"$OUT/app.log"  # ATMOSPHERE wheel (kNewgameControls[2])
sleep 1
DISPLAY=$DISP ./tools/xsend "Ascendancy" click 188 435 2>>"$OUT/app.log"  # SPECIES wheel
sleep 1
DISPLAY=$DISP ./tools/xsend "Ascendancy" click 64 435 2>>"$OUT/app.log"   # DENSITY wheel
sleep 1
DISPLAY=$DISP import -window root "$OUT/before-begin.png" 2>>"$OUT/app.log"
DISPLAY=$DISP ./tools/xsend "Ascendancy" click 566 422 2>>"$OUT/app.log"  # BEGIN NEW GAME
sleep 2
DISPLAY=$DISP import -window root "$OUT/raceintro.png" 2>>"$OUT/app.log"
DISPLAY=$DISP ./tools/xsend "Ascendancy" click 320 450 2>>"$OUT/app.log"  # dismiss intro -> Campaign
sleep 3
DISPLAY=$DISP import -window root "$OUT/map.png" 2>>"$OUT/app.log"
kill $APP 2>/dev/null
grep -E "raceconfig atmos|raceconfig click|newgame apply|newgame live|raceintro|title exit" "$OUT/app.log"
echo SHOTS "$OUT"/before-begin.png "$OUT"/raceintro.png "$OUT"/map.png
