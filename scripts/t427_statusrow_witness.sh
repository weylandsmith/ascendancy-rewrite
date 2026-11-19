#!/usr/bin/env bash
# t427 witness: PLANETS LIST ROW COMPOSITION law (D17). Boot -> campaign map
# -> STATUS rail -> shot (unselected rows); click row 0 -> Escape -> shot
# (selected row 0, line1 WHITE). Census -> t427_witness_census.py (run with
# ~/tools/revenv/bin/python — numpy lives there, NOT the repo venv).
# Law: docs/re/_wip_t427.md F1-F6. Prints VERDICT PASS/FAIL.
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/t427_shots}
DISP=${DISP:-:97}
rm -rf "$OUT"; mkdir -p "$OUT"
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 & XV=$!
sleep 2
DISPLAY=$DISP "$BIN" --ui --campaign 1 --seed 5 --species 0 >"$OUT/app.log" 2>&1 &
APP=$!
trap 'kill $APP 2>/dev/null; kill $XV 2>/dev/null' EXIT
sleep 3
shot() { DISPLAY=$DISP import -window root "$OUT/$1.png" 2>>"$OUT/app.log"; }
X() { DISPLAY=$DISP ./tools/xsend "Ascendancy" "$@"; sleep 0.4; }
K() { DISPLAY=$DISP ./tools/xsend "Ascendancy" key "$1"; sleep 0.4; }
X 318 335            # RESUME -> campaign map
X 553 145            # STATUS rail button centre -> planets list
sleep 1
shot status-open     # rows 0..2 UNSELECTED (statusSel == -1)
X 300 100            # ROW 0 band (57..197) -> opens planet view, sets statusSel=0
K Escape             # t410 chain pop -> status with statusSel persisting
sleep 1
shot status-sel      # row 0 line1 WHITE, rows 1/2 GREEN
kill $APP 2>/dev/null; kill ${XV:-0} 2>/dev/null
grep -E "ui rail STATUS|ui status" "$OUT/app.log"
~/tools/revenv/bin/python scripts/t427_witness_census.py \
    "$OUT/status-open.png" "$OUT/status-sel.png"
