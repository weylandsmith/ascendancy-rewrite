#!/usr/bin/env bash
# tPF-1c side-test: does an Escape at the map (stack bottom) quit the GAME
# with the user's symptom line ("ui ok: turn N")? If yes, the day-20 report
# is consistent with 20 manual NEXT TURNs + one stray Escape, NOT a
# camp.over() victory. Runs the user-era binary (656ce2e) and the HEAD
# binary under scratch Xvfb :97; kills by PID.
set -u
cd /home/hrethric/projects/ascendancy
BIN=$1
DATA=$2
PRESSES=${PRESSES:-20}
rm -f /tmp/.X97-lock /tmp/.X11-unix/X97 2>/dev/null
Xvfb :97 -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
trap 'kill $XV 2>/dev/null; true' EXIT
sleep 1
export DISPLAY=:97
"$BIN" --data "$DATA" --ui >/tmp/tpf1c_esc_${TAG:-run}.log 2>&1 &
APP=$!
sleep 4
X() { ./tools/xsend "Ascendancy" click "$@" 2>/dev/null; sleep 0.7; }
X 320 60
X 318 295
X 566 422
sleep 2
X 320 450
sleep 0.5
for i in $(seq "$PRESSES"); do X 511 67; done
./tools/xsend "Ascendancy" key Escape 2>/dev/null
sleep 1.5
LOG=/tmp/tpf1c_esc_${TAG:-run}.log
if kill -0 $APP 2>/dev/null; then
  echo "ESCAPE-TEST: ALIVE after map-Escape (presses=$(grep -c 'ui click next-turn' "$LOG"))"
  kill $APP 2>/dev/null
else
  echo "ESCAPE-TEST: EXITED on map-Escape (presses=$(grep -c 'ui click next-turn' "$LOG"))"
fi
tail -2 "$LOG"
