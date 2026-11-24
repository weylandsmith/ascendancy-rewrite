#!/usr/bin/env bash
# tPL-V2 port witness: the orbital slot grid on OUR port. Boot seed 5 ->
# RESUME -> STATUS -> row 0 (planet view); shots: (a) rest (ten empty slots,
# NO resting frames), (b) hover slot 0 (thin grey 69x69 box at (13,119)),
# (c) hover slot 6 (box at (83,189)). Hover = xsend warp (XWarpPointer ->
# SDL_GetMouseState, the t419 corner-popup law). Census -> tplv2_census.py.
# Xvfb hygiene (tPL-V1f/tPL-V1g laws): export DISPLAY inside, clear stale
# locks, kill BY PID ONLY (never bulk pkill), never touch :9.
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/tplv2_shots}
DISP=${DISP:-:99}
rm -rf "$OUT"; mkdir -p "$OUT"
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99 2>/dev/null
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
export DISPLAY=$DISP
"$BIN" --ui --campaign 1 --seed 5 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 3
shot() {
  local g; g=$(./tools/winpos "Ascendancy") || { echo "winpos FAIL $1" >>"$OUT/app.log"; return 1; }
  local X=${g%% *} rest=${g#* }; local Y=${rest%% *} rest2=${rest#* }; local W=${rest2%% *} rest3=${rest2#* }; local H=${rest3%% *}
  [ "$W" = 640 ] && [ "$H" = 480 ] || { echo "shot FAIL $1 geometry $g" >>"$OUT/app.log"; return 1; }
  timeout 15 import -window root -crop "${W}x${H}+${X}+${Y}" +repage "$OUT/$1.png" 2>>"$OUT/app.log"
}
X() { ./tools/xsend "Ascendancy" "$@"; sleep 0.4; }
X 318 335            # RESUME -> campaign map
X 553 145            # STATUS rail -> planets list
sleep 1
X 300 100            # ROW 0 band -> planet view
sleep 1
# park the pointer OUTSIDE the orbital rect (x>152) but inside the window
X warp 400 470
sleep 0.4
shot rest              # ten slots, NO frames (empty at rest)
X warp 40 150
sleep 0.4
shot hover-slot0
X warp 110 220
sleep 0.4
shot hover-slot6
X warp 400 470
sleep 0.4
shot rest-again
kill $APP 2>/dev/null; kill $XV 2>/dev/null   # PID-only kill law (tPL-V1g)
echo DONE
