#!/usr/bin/env bash
# t418b witness: PLANET VIEW tile grid (D15 "no planet visible"). Boot ->
# campaign map -> STATUS rail -> row click (opens state 17) -> shot; tile
# click -> shot; PLBUILD press -> shot. Census -> t418b_witness_census.py
# (run with ~/tools/revenv/bin/python — numpy lives there, NOT the repo venv).
# Screenshots -> $OUT for USER/native-vision grading (D13).
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/t418b_shots}
DISP=${DISP:-:97}
rm -rf "$OUT"; mkdir -p "$OUT"
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP "$BIN" --ui --campaign 1 --seed 5 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 3
shot() { DISPLAY=$DISP import -window root "$OUT/$1.png" 2>>"$OUT/app.log"; }
X() { DISPLAY=$DISP ./tools/xsend "Ascendancy" "$@"; sleep 0.4; }  # t408 grep-race law
X 318 335            # RESUME -> campaign map
X 553 145            # STATUS rail button centre -> planets list
sleep 1
X 300 100            # ROW 0 band (57..197) -> t406 law opens planet view
sleep 1
shot planet-open     # disc + diamond grid + any structure art
# Tile click: the F2 bbox centre is (365,325) for EVERY size class (derived
# from the lattice this session), and it is exactly the centre of tile
# (row5,col5) — a guaranteed hit. (390,320 was a lattice GAP: the diamond
# area 1156 < lattice cell 1445, so gaps exist between tiles — the vendor
# grid shows the same; the hit-map correctly refuses gap points.)
X 365 325
sleep 0.4
shot planet-tile     # white outline on the selected diamond (log: tile N selected)
X 547 57             # PLBUILD panel centre (463,8-632,106) -> project list
sleep 0.6
shot planet-list     # PLANLIST rows over the field
kill $APP 2>/dev/null; kill $XV 2>/dev/null
grep -E "ui status select|ui planet tile|ui planet project" "$OUT/app.log"
echo DONE
