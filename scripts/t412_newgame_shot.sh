#!/usr/bin/env bash
# t412 witness: New Game screen (post-t411 blend fix) -> BEGIN -> race intro.
set -u
cd /home/hrethric/projects/ascendancy
BIN=./rewrite/build/ascendancy
OUT=/tmp/t412_shots
DISP=${DISP:-:97}
rm -rf "$OUT"; mkdir -p "$OUT"
pkill -x ascendancy 2>/dev/null || true
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP SDL_AUDIODRIVER=dummy "$BIN" --data /tmp/uishow --ui --campaign 1 --seed 5 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 4
# neutral click first (t385b first-click-dropped law)
DISPLAY=$DISP ./tools/xsend "Ascendancy" click 320 60 2>>"$OUT/app.log"
sleep 1
# FRESHGAME centre (159,280)-(477,310) per boot.md L22
DISPLAY=$DISP ./tools/xsend "Ascendancy" click 318 295 2>>"$OUT/app.log"
sleep 1
DISPLAY=$DISP import -window root "$OUT/t412-newgame.png" 2>>"$OUT/app.log"
# BEGIN NEW GAME centre (494,373)-(639,472) per menulaw.h kBeginNewGameBtn
DISPLAY=$DISP ./tools/xsend "Ascendancy" click 566 422 2>>"$OUT/app.log"
sleep 2
DISPLAY=$DISP import -window root "$OUT/t412-raceintro.png" 2>>"$OUT/app.log"
# dismiss the intro -> Campaign (map)
DISPLAY=$DISP ./tools/xsend "Ascendancy" click 320 450 2>>"$OUT/app.log"
sleep 3
DISPLAY=$DISP import -window root "$OUT/t412-after-intro.png" 2>>"$OUT/app.log"
kill $APP 2>/dev/null; kill $XV 2>/dev/null
grep -E "ui window|FRESHGAME|ui raceconfig|ui raceintro|refused" "$OUT/app.log"
echo SHOT "$OUT/t412-newgame.png" "$OUT/t412-raceintro.png"
