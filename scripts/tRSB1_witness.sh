#!/usr/bin/env bash
# tRS-B1 WITNESS (tRS-V1c UPDATE): the D26 set-project walkthrough (law
# docs/re/_wip_tRSV1.md P12 + _wip_tRSB1.md P1-P3; port arm
# researchview.cpp setStudy + ui.cpp kScreenResearch).
# Flow: RESUME -> RESEARCH rail -> BEFORE shot -> click the Available node
# the APP ITSELF reported ("ui research center <row> <x> <y> available",
# logged once on screen entry under the vendor projection law) -> AFTER shot
# -> log leg + pixel census leg. The click point is RE-DERIVED from the log,
# never hard-coded (the tRS-V1c geometry moved every centre).
# Scratch Xvfb, kill BY PID.
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/trsb1_shots}
DISP=${DISP:-:99}
PY=${PY:-$HOME/tools/revenv/bin/python}
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
# The frontier row sits OFF-FRAME at rest (tRS-V1c geometry: y=684 at seed
# 5 — the vendor field is a WINDOW and the rest camera does not show every
# legal disk). DOLLY OUT (MOVEUP pair, kResMoveUp centre 578,449): each tick
# posZ -= 1 shrinks the tree toward (235,240); ~5 ticks pulls row 3's centre
# inside the clip rect. The app RE-LOGS the centre on every change.
# tPF-7 HOLD LAW: the dolly runs ONLY while the button is held (vendor
# release msg 0x47d3b). clickdn = press-only, clickup = release-only; the
# hold is POLLED against the app's centre re-log (adaptive across cadences —
# the pump now runs at ResCam::kPumpMs=34, not the old 1000).
BEFORE_N=$(grep -c "ui research center " "$OUT/app.log")
X clickdn 578 449
for i in 1 2 3 4 40 80; do
  sleep 0.5
  NOW_N=$(grep -c "ui research center " "$OUT/app.log")
  [ "$NOW_N" -ge $((BEFORE_N + 8)) ] && break
done
X clickup 578 449
sleep 1
shot before          # AFTER dolly settles: local leg isolates the CLICK
# RE-DERIVE the click point from the app's LATEST centre report (vendor law).
CENTER_LINE=$(grep "ui research center " "$OUT/app.log" | grep available | tail -1)
if [ -z "$CENTER_LINE" ]; then
  echo "FAIL  app logged no 'ui research center' line"; kill $APP 2>/dev/null; kill $XV 2>/dev/null
  echo VERDICT FAIL; exit 1
fi
# "ui research center <row> <x> <y> available" -> fields 4,5,6
read -r _ _ _ NODE_ROW NODE_X NODE_Y _ <<< "$CENTER_LINE"
echo "click re-derived from log: row=$NODE_ROW x=$NODE_X y=$NODE_Y"
X "$NODE_X" "$NODE_Y"    # click the Available node -> SET the project
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
