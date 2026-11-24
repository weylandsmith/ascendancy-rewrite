#!/usr/bin/env bash
# tRS-B1 probe: does a research-screen node click SET the project in the
# PORT (D26 "I can't set any projects")? Scratch Xvfb :99, kill BY PID only.
# Flow: RESUME -> RESEARCH rail (553,223) -> click derived node centre ->
# log must show "ui research study <name>".
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/trs_probe}
DISP=${DISP:-:99}
rm -rf "$OUT"; mkdir -p "$OUT"
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP "$BIN" --ui --campaign 1 --seed 5 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 3
X() { DISPLAY=$DISP ./tools/xsend "Ascendancy" "$@"; sleep 1; }
X 318 335            # RESUME -> campaign map
X 553 223            # RESEARCH rail -> state 20
sleep 1
DISPLAY=$DISP import -window root -crop 640x480+0+0 +repage "$OUT/research.png" 2>>"$OUT/app.log"
# click the layout's first Available node: python derives the centre from the
# same law the app paints (kResFieldX0/Y0 + depth/slot); fallback = scan the
# png for a ring pixel cluster. For the probe just click a spread of points
# inside the field and log which (if any) fires a study line.
for pt in "40 76" "136 76" "60 120" "100 100" "136 154" "232 76" "46 200" "150 240" "300 150" "250 300"; do
  X $pt
done
sleep 1
kill $APP 2>/dev/null; kill $XV 2>/dev/null
echo "--- study/readout lines:"
grep -E "ui research (study|readout|pan)" "$OUT/app.log" | head -20
grep -q "ui research study" "$OUT/app.log" && echo "PROBE: click CAN set the project" || echo "PROBE: NO click set the project"
