#!/usr/bin/env bash
# tPF-4 SHIP-ROW ART witness (port side). Law docs/re/_wip_tPF4.md P4/P6:
# the PLANLIST row for item 23 (Ship) blits smship{kShipShapeFile[specnum]}.shp
# record 0 at scale 0.5 instead of the planitem icon. Instrument: change-only
# log line "ui planlist ship row file N scale 0.5" + pixel census of the row
# strip vs a control strip one row-height above (no art there at rest).
# Xvfb hygiene per tPL-V1f laws: locks cleared, kill BY PID, never touch :9.
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/tpf4_shots}
DISP=${DISP:-:97}
rm -rf "$OUT"; mkdir -p "$OUT"
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99 2>/dev/null
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
export DISPLAY=$DISP
"$BIN" --ui --campaign 1 --seed 5 --species 0 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 3
shot() {
  local g; g=$(./tools/winpos "Ascendancy") || { echo "winpos FAIL $1" >>"$OUT/app.log"; return 1; }
  local X=${g%% *} rest=${g#* }; local Y=${rest%% *} rest2=${rest#* }; local W=${rest2%% *} rest3=${rest2#* }; local H=${rest3%% *}
  [ "$W" = 640 ] && [ "$H" = 480 ] || { echo "shot FAIL $1 geometry $g" >>"$OUT/app.log"; return 1; }
  timeout 15 import -window root -crop "${W}x${H}+${X}+${Y}" +repage "$OUT/$1.png" 2>>"$OUT/app.log"
}
X() { ./tools/xsend "Ascendancy" "$@"; sleep 0.35; }
X 318 335            # RESUME -> campaign map
X 553 145            # STATUS rail -> planets list
sleep 1
X 300 100            # ROW 0 -> planet view
n=0; while [ $n -lt 6 ] && ! grep -q "ui status select" "$OUT/app.log"; do sleep 0.5; n=$((n+1)); done
grep -q "ui status select" "$OUT/app.log" || { echo "VERDICT FAIL: planet view never opened"; kill $APP $XV 2>/dev/null; exit 1; }
# Open a BUILD popup on an adjacent tile: probe the CB-adjacent cell the
# tPF2b recipe derives; the FIRST ids=54 tile is fine — click Build bar.
CENTERS=$(python3 - <<'PY'
import re,re as _
log=open('/tmp/tpf4_shots/app.log').read()
m=re.search(r'home-cb cell (\d+) size (\d)', log)
B=[0,0,0,0,4,4,5,0,0,0,0,0,0,0,0,
   0,0,0,4,3,4,5,6,0,0,0,0,0,0,0,
   0,0,0,3,2,3,3,4,5,7,0,0,0,0,0,
   0,1,1,2,2,3,4,5,7,0,0,0,0,0,0,
   1,0,0,0,1,1,2,3,4,5,7,0,0,0,0]
C=[0,0,0,0,2,3,2,0,0,0,0,0,0,0,0,
   0,0,0,1,3,3,3,1,0,0,0,0,0,0,0,
   0,0,0,1,4,4,5,4,4,1,0,0,0,0,0,
   0,0,2,5,6,6,7,6,6,5,2,0,0,0,0,
   3,6,7,8,8,9,8,8,7,6,3,0,0,0,0]
s=int(m.group(2)); cum=0
for row in range(15):
    for col in range(B[s*15+row], B[s*15+row]+C[s*15+row]):
        print(410+col*34-row*34, 127+col*17+row*17)
PY
)
BUILD_XY=""
while read -r tx ty; do
  [ -n "$BUILD_XY" ] && break
  X $tx $ty
  grep 'ui planet tile' "$OUT/app.log" | tail -1 | grep -q "ids=54" && BUILD_XY="$tx $ty"
done <<< "$CENTERS"
[ -n "$BUILD_XY" ] || { echo "VERDICT FAIL: no buildable tile"; kill $APP $XV 2>/dev/null; exit 1; }
set -- $BUILD_XY
X $1 $2; sleep 0.3
X 227 353            # BUILD button -> PLANLIST opens
sleep 0.5
# The Ship row log fires whenever row 23 is IN the visible window: step the
# scroll arrow one row at a time, snapshot when it fires, keep going to the
# bottom for the census shot.
for i in $(seq 1 40); do
  X 500 404
  if grep -q "planlist ship row file" "$OUT/app.log" && [ ! -f "$OUT/list-ship.png" ]; then
    sleep 0.4; shot list-ship
  fi
done
sleep 0.5
shot list-bottom
grep "planlist ship" "$OUT/app.log" | tail -2
kill $APP $XV 2>/dev/null
if grep -q "planlist ship row file" "$OUT/app.log"; then
  echo "VERDICT LOG PASS"; exit 0
else
  echo "VERDICT LOG FAIL (ship row never rendered in the visible window)"; exit 1
fi
