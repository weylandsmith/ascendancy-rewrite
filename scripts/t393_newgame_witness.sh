#!/usr/bin/env bash
# t393 witness: New Game full-screen switch. Title -> click New Game ->
# screenshot the NEW GAME screen (screen law: no title chrome may bleed) ->
# wheel clicks + species select + arrow -> click Begin New Game -> campaign
# must start (routing prints). Screenshots land in $OUT for USER grading.
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/t393_shots}
DISP=${DISP:-:96}
rm -rf "$OUT"; mkdir -p "$OUT"
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP "$BIN" --ui --campaign 1 --seed 5 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 4
DISPLAY=$DISP import -window root "$OUT/t393-title.png" 2>>"$OUT/app.log"
# 1) New Game button (FRESHGAME rect centre 318,295)
DISPLAY=$DISP ./tools/xsend "Ascendancy" 318 295 2>>"$OUT/app.log"
sleep 1
DISPLAY=$DISP import -window root "$OUT/t393-newgame.png" 2>>"$OUT/app.log"
# 2) wheel clicks: Star Density, Species, Atmosphere (row centres y=426)
DISPLAY=$DISP ./tools/xsend "Ascendancy" 64 426 2>>"$OUT/app.log"
DISPLAY=$DISP ./tools/xsend "Ascendancy" 188 426 2>>"$OUT/app.log"
DISPLAY=$DISP ./tools/xsend "Ascendancy" 312 426 2>>"$OUT/app.log"
# 3) species select slot 1 (centre 567,214) + down arrow (623,363)
DISPLAY=$DISP ./tools/xsend "Ascendancy" 567 214 2>>"$OUT/app.log"
DISPLAY=$DISP ./tools/xsend "Ascendancy" 623 363 2>>"$OUT/app.log"
sleep 1
DISPLAY=$DISP import -window root "$OUT/t393-newgame-set.png" 2>>"$OUT/app.log"
# 4) Begin New Game (measured rect centre 566,422) -> Campaign
DISPLAY=$DISP ./tools/xsend "Ascendancy" 566 422 2>>"$OUT/app.log"
sleep 2
DISPLAY=$DISP import -window root "$OUT/t393-after-begin.png" 2>>"$OUT/app.log"
kill $APP 2>/dev/null; kill $XV 2>/dev/null
grep -E "ui window|ui title click FRESHGAME|ui raceconfig" "$OUT/app.log"
echo DONE
