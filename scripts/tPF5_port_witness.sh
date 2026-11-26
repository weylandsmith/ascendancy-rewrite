#!/usr/bin/env bash
# tPF-5 witness: the industry-tile ANCHOR on OUR port (D28 item 10).
# Boot seed 5 -> planet view -> shot rest; app.log must carry
#   "ui strip planind.shp rec K bbox(0,T) rect(123,7) blit(123,7+T)"
# with T from the measured ladder. Census: scripts/tPF5_witness_census.py.
# Xvfb hygiene (tPL-V1f/g laws): export DISPLAY inside, clear stale locks,
# kill BY PID ONLY, never touch :9. Build BOTH run_tests AND ascendancy first
# (tPF-3e WITNESS TRAP).
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/tpf5_shots}
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
X warp 400 470
sleep 0.4
shot rest
kill $APP 2>/dev/null; kill $XV 2>/dev/null   # PID-only kill law
echo DONE
