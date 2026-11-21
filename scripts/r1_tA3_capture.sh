#!/usr/bin/env bash
# tA3 TEXT LAW capture: Title -> New Game (FRESHGAME 159,280-477,310) ->
# Begin New Game (hit rect 494,373-639,472) -> campaign map. One shot per
# screen at the tA1 1:1 Xvfb law (640x480 root grab, no scaling).
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/tA3_shots}
DISP=${DISP:-:99}
rm -rf "$OUT"; mkdir -p "$OUT" /tmp/tA3_saves
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP "$BIN" --ui --campaign 1 --seed 5 --saves /tmp/tA3_saves >"$OUT/app.log" 2>&1 &
APP=$!
sleep 3
shot() { DISPLAY=$DISP import -window root "$OUT/$1.png" 2>>"$OUT/app.log"; }
X() { DISPLAY=$DISP ./tools/xsend "Ascendancy" "$@"; sleep 1; }

X 318 295            # FRESHGAME -> New Game screen
sleep 1
shot newgame
X 566 422            # Begin New Game hit rect centre -> race intro
sleep 2
X 320 240            # intro advance -> campaign map
sleep 2
shot map
kill $APP 2>/dev/null; kill $XV 2>/dev/null
echo DONE
