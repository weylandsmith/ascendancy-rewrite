#!/usr/bin/env bash
# tPF-1d cap witness: --campaign 2 Begin flow, 2 presses => the run must
# print 'ui quit cause=harness-turn-cap turn=2' BEFORE 'ui ok: turn 2'.
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=/tmp/tpf1d_cap
rm -rf "$OUT"; mkdir -p "$OUT"
rm -f /tmp/.X97-lock /tmp/.X11-unix/X97 2>/dev/null
Xvfb :97 -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
trap 'kill $XV 2>/dev/null; pkill -f "rewrite/build/ascendancy --data" 2>/dev/null; true' EXIT
sleep 1
export DISPLAY=:97
"$BIN" --data "$PWD" --ui --campaign 2 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 4
kill -0 $APP 2>/dev/null || { echo "HARNESS FAIL: app died at boot"; cat "$OUT/app.log"; exit 2; }
X() { ./tools/xsend "Ascendancy" click "$@" 2>>"$OUT/xsend.log"; sleep 1; }
X 320 60; X 318 295; X 566 422; sleep 2; X 320 450; sleep 1
grep -q "newgame live" "$OUT/app.log" || { echo "NAV FAIL"; tail -5 "$OUT/app.log"; exit 2; }
X 511 67
grep -c "ui click next-turn" "$OUT/app.log"
X 511 67
sleep 2
grep -nE "ui quit cause|ui ok|HARNESS-CAP" "$OUT/app.log"
