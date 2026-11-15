#!/usr/bin/env bash
# t394 witness: galaxy-map sidebar chrome. Boot -> campaign map -> shot;
# click seam targets (map-ctl cluster, race slot, NEXTTURNCONT) and verify
# the printed seam lines; click NEXT TURN (advance works); final shot.
# Screenshots -> $OUT for USER grading. Census: scripts/t394_map_mass.py.
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/t394_shots}
DISP=${DISP:-:96}
rm -rf "$OUT"; mkdir -p "$OUT"
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP "$BIN" --ui --campaign 1 --seed 5 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 3
shot() { DISPLAY=$DISP import -window root "$OUT/$1.png" 2>>"$OUT/app.log"; }
X() { DISPLAY=$DISP ./tools/xsend "Ascendancy" "$@"; sleep 1; }
X 318 335            # RESUME -> campaign map
shot map
X 533 371            # ROTUP cluster centre (518,364-548,379)
X 611 418            # TOGCOLONIES centre
X 487 457            # RACE1CONTROL slot centre
X 594 67             # NEXTTURNCONT centre (557,52-632,82)
X 511 67             # NEXTTURN centre (474,52-548,82) -> advance turn 1
sleep 1
shot map-turn1
kill $APP 2>/dev/null; kill $XV 2>/dev/null
grep -E "ui window|map-ctl seam|race-controls seam|next-turn" "$OUT/app.log"
echo DONE
