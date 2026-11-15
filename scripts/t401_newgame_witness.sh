#!/usr/bin/env bash
# t401 witness: New Game ART law. Boot to Title -> New Game -> screenshot
# (art census target) -> click Species + Atmosphere wheels -> second shot
# (wheel frame must CHANGE) -> Begin -> campaign starts (routing line).
# Screenshots to $OUT; census runs via the VENV python (PIL law).
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/t401_shots}
DISP=${DISP:-:97}
rm -rf "$OUT"; mkdir -p "$OUT"
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP "$BIN" --ui --campaign 1 --seed 5 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 4
# one click into the window (t385b: first synthetic click on a fresh window
# is dropped; the title->newgame transition itself reuses the window)
DISPLAY=$DISP ./tools/xsend "Ascendancy" 318 295 2>>"$OUT/app.log"
sleep 1
DISPLAY=$DISP import -window root "$OUT/t401-newgame.png" 2>>"$OUT/app.log"
# wheel clicks: Species (188,426) then Atmosphere (312,426)
DISPLAY=$DISP ./tools/xsend "Ascendancy" 188 426 2>>"$OUT/app.log"
sleep 1
DISPLAY=$DISP ./tools/xsend "Ascendancy" 312 426 2>>"$OUT/app.log"
sleep 1
DISPLAY=$DISP import -window root "$OUT/t401-newgame-set.png" 2>>"$OUT/app.log"
# Begin -> campaign
DISPLAY=$DISP ./tools/xsend "Ascendancy" 566 422 2>>"$OUT/app.log"
sleep 2
kill $APP 2>/dev/null; kill $XV 2>/dev/null
grep -E "ui window|FRESHGAME|ui raceconfig|ui ok" "$OUT/app.log"
~/tools/revenv/bin/python scripts/t401_witness_census.py "$OUT/t401-newgame.png"
echo DONE
