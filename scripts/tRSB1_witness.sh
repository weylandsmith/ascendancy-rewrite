#!/usr/bin/env bash
# tRS-B1 WITNESS: the D26 set-project walkthrough (law docs/re/_wip_tRSB1.md
# P1-P3; port arm researchview.cpp setStudy + ui.cpp kScreenResearch).
# Flow: RESUME -> RESEARCH rail -> BEFORE shot -> click a known-Available
# node -> AFTER shot -> log leg + pixel census leg. Scratch Xvfb, kill BY PID.
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/trsb1_shots}
DISP=${DISP:-:99}
PY=${PY:-$HOME/tools/revenv/bin/python}
NODE_X=${NODE_X:-136}
NODE_Y=${NODE_Y:-154}
rm -rf "$OUT"; mkdir -p "$OUT"
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP SDL_AUDIODRIVER=dummy "$BIN" --ui --campaign 1 --seed 5 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 3
X() { DISPLAY=$DISP ./tools/xsend "Ascendancy" "$@"; sleep 1; }
shot() { sleep 0.3; DISPLAY=$DISP import -window root -crop 640x480+0+0 +repage "$OUT/$1.png" 2>>"$OUT/app.log"; }
X 318 335            # RESUME -> campaign map
X 553 223            # RESEARCH rail (windows.txt 474,208-632,238) -> state 20
sleep 1
shot before
X "$NODE_X" "$NODE_Y"    # click an Available node -> SET the project
sleep 1
shot after
kill $APP 2>/dev/null; kill $XV 2>/dev/null
pass=1
grep -E "ui research (study|readout)" "$OUT/app.log"
grep -q "ui research study" "$OUT/app.log" \
  && echo "PASS  log: a node click SET the study project" \
  || { echo "FAIL  no study line"; pass=0; }
"$PY" scripts/tRSB1_census.py "$OUT/before.png" "$OUT/after.png" "$NODE_X" "$NODE_Y" \
  || { echo "census FAIL"; pass=0; }
[ $pass = 1 ] && echo VERDICT PASS || echo VERDICT FAIL
exit $((1-pass))
