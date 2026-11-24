#!/usr/bin/env bash
# tPL-B2 port witness: the msg-50 productivity-box popups on OUR port.
# Boot seed 5 -> RESUME -> STATUS -> row 0 (planet view); shots: rest, then
# a CLICK on each top-row panel (PLRES/PLIND/PLPRO/PLPOP) with a shot after
# each. The app.log lines "ui planet popup <panel> (N lines)" are the
# arm-side witness; the PNGs are the render-side witness (census:
# tplb2_census.py checks the PROSPERITY popup text region changed vs rest).
# Xvfb hygiene (tPL-V1f/tPL-V1g laws): export DISPLAY inside, clear stale
# locks, kill BY PID ONLY (never bulk pkill), never touch :9.
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/tplb2_shots}
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
X 60 56              # PLRES click (msg 50 key 0)
sleep 0.5
shot popup-plres
X 292 56             # PLPRO click (msg 50 key 2 — the user witness box)
sleep 0.5
shot popup-plpro
X 404 56             # PLPOP click (msg 50 key 4 — full-info)
sleep 0.5
shot popup-plpop
X 176 56             # PLIND click (msg 50 key 1)
sleep 0.5
shot popup-plind
X 300 250            # field click = dismiss
sleep 0.5
shot dismissed
kill $APP 2>/dev/null; kill $XV 2>/dev/null   # PID-only kill law (tPL-V1g)
echo DONE
