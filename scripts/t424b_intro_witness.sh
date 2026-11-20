#!/usr/bin/env bash
# t424b witness: drive title -> New Game -> Begin, screenshot the RACE INTRO
# (dark-speckle background law, docs/re/_wip_t424b.md F1-F3), then grade
# mechanically (scripts/t424b_witness_census.py). Rect centres per the t393
# witness (same New Game layout).
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/t424b_shots}
DISP=${DISP:-:97}
rm -rf "$OUT"; mkdir -p "$OUT"
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP "$BIN" --ui --campaign 1 --seed 5 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 4
# 1) New Game button (FRESHGAME rect centre 318,295)
DISPLAY=$DISP ./tools/xsend "Ascendancy" 318 295 2>>"$OUT/app.log"
sleep 1
# 2) species slot 0 select (leftmost of the species row) + Begin New Game
#    (measured rect centre 566,422) -> the RACE INTRO screen
DISPLAY=$DISP ./tools/xsend "Ascendancy" 567 214 2>>"$OUT/app.log"
sleep 1
DISPLAY=$DISP ./tools/xsend "Ascendancy" 566 422 2>>"$OUT/app.log"
sleep 2
DISPLAY=$DISP import -window root "$OUT/t424b-raceintro.png" 2>>"$OUT/app.log"
kill $APP 2>/dev/null; kill $XV 2>/dev/null
grep -E "ui raceintro|ui raceconfig" "$OUT/app.log"
echo DONE
