#!/usr/bin/env bash
# tPF-3b port witness: TILE OVERLAY + STRUCTURE-ART ANCHOR on OUR port.
# Nav verbatim from tPF2_witness.sh (RESUME 318,335 -> STATUS 553,145 -> row 0
# 300,100, need "ui status select"). Then one planet-view shot + measure.
# Xvfb hygiene (tPL-V1f/g laws): export DISPLAY inside, clear stale locks,
# kill BY PID ONLY, never touch :9.
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/tpf3b_shots}
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
need() {
  local n=0
  while [ $n -lt 6 ]; do
    grep -q "$1" "$OUT/app.log" 2>/dev/null && return 0
    sleep 0.5; n=$((n+1))
  done
  echo "WITNESS FAIL: no '$1' ($2)" >> "$OUT/app.log"; return 1
}
kill -0 $XV 2>/dev/null || { echo "WITNESS FAIL: Xvfb dead at start" >>"$OUT/app.log"; exit 1; }
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
need "ui status select" "row click did not open planet view" || { kill $APP $XV 2>/dev/null; echo VERDICT FAIL; exit 1; }
sleep 1
shot 03_planet
kill $APP 2>/dev/null; wait $APP 2>/dev/null
kill $XV 2>/dev/null
~/tools/revenv/bin/python scripts/tPF3b_overlay_measure.py "$OUT/03_planet.png" "$OUT/app.log" 2>&1 | tail -12
echo WITNESS_RC=$?
