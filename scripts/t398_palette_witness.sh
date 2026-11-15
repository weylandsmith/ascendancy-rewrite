#!/usr/bin/env bash
# t398 witness: chrome renders through game.pal. Boot --ui under Xvfb, RESUME
# to the campaign map, screenshot; the census (scripts/t398_witness_census.py)
# decides mechanically: the palette diagnostic line + rail-zone chroma.
# Screenshots -> $OUT for USER grading (D11 "greyscale" re-test).
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/t398_shots}
DISP=${DISP:-:97}
rm -rf "$OUT"; mkdir -p "$OUT"
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP "$BIN" --ui --campaign 1 --seed 5 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 3
shot() { DISPLAY=$DISP import -window root "$OUT/$1.png" 2>>"$OUT/app.log"; }
X() { DISPLAY=$DISP ./tools/xsend "Ascendancy" "$@"; sleep 1; }
shot title
X 318 375            # LOAD button -> load screen
shot load
X key Escape         # cancel load
X 318 295            # FRESH GAME -> New Game screen
shot newgame
X 566 422            # Begin New Game (494,373)-(639,472) -> campaign map
shot map
kill $APP 2>/dev/null; kill $XV 2>/dev/null
grep -E "ui palette" "$OUT/app.log"
echo DONE
