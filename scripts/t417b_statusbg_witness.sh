#!/usr/bin/env bash
# t417b witness: STATUS BACKGROUND law (D15). Boot -> campaign map -> STATUS
# rail -> shot (open); scroll + select -> shot. Census -> t417b_witness_census.py
# (run with ~/tools/revenv/bin/python — numpy lives there, NOT the repo venv).
# Screenshots -> $OUT for USER grading.
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/t417b_shots}
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
K() { DISPLAY=$DISP ./tools/xsend "Ascendancy" key "$1"; sleep 0.4; }
X 318 335            # RESUME -> campaign map
X 553 145            # STATUS rail button centre -> planets list
sleep 1
shot status-open     # no marker yet (statusSel == -1)
X 628 450            # scroll-down arrow (t405 measured box; seed-5 clamps)
shot status-scroll1
X 300 100            # ROW 0 band (57..197) -> t406 law opens planet view
K Escape             # t410 chain: planet -> status (stack pops one level)
sleep 1
shot status-reopen   # statusSel persists -> red marker row 0 x16..69 y59..82
kill $APP 2>/dev/null; kill $XV 2>/dev/null
grep -E "ui rail STATUS|ui status" "$OUT/app.log"
echo DONE
