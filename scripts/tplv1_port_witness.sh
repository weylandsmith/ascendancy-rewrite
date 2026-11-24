#!/usr/bin/env bash
# tPL-V1 witness: the corrected tile lattice (adjacent rows) + class edge
# colours on OUR port. Boot seed 5 -> STATUS -> row 0 (planet view) -> shot;
# tile click -> shot. Census -> tplv1_port_census.py (run with
# ~/tools/revenv/bin/python — numpy lives there, NOT the repo venv).
# The t418b witness's click point (365,325) encoded the OLD transposed law's
# bbox centre and is NOT reused; under the corrected law the seed-5 size-0
# lattice bbox centre is tile (5,5) at (410,297).
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/tplv1_shots}
DISP=${DISP:-:99}
rm -rf "$OUT"; mkdir -p "$OUT"
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP "$BIN" --ui --campaign 1 --seed 5 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 3
# grab the APP WINDOW (not root): a stray Xvfb on the display would make a
# root grab larger than 640x480 with the window offset inside it (tPL-V1
# lesson). ImageMagick resolves -window by NAME.
shot() { DISPLAY=$DISP import -window "Ascendancy" "$OUT/$1.png" 2>>"$OUT/app.log"; }
X() { DISPLAY=$DISP ./tools/xsend "Ascendancy" "$@"; sleep 0.4; }  # t408 grep-race law
X 318 335            # RESUME -> campaign map
X 553 145            # STATUS rail -> planets list
sleep 1
X 300 100            # ROW 0 band -> planet view
sleep 1
shot planet-open     # adjacent-row lattice + class-coloured edges
X 410 297            # tile (5,5) centre under the CORRECTED law
sleep 0.4
shot planet-tile     # white selection outline on that diamond
X 444 280            # tile (4,5) centre (adjacent up-right) — the click
                     # chain across the SHARED edge
sleep 0.4
shot planet-adjacent
kill $APP 2>/dev/null; kill $XV 2>/dev/null
grep -E "ui status select|ui planet tile|ui planet project" "$OUT/app.log"
echo DONE
