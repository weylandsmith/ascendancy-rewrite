#!/usr/bin/env bash
# t388 live witness: rail clicks route through the screen law under Xvfb.
# Scratch display :81 only. Prints the app log at the end.
set -u
cd "$(dirname "$0")/.."
rm -f /tmp/.X81-lock /tmp/.X11-unix/X81
Xvfb :81 -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=:81 ./rewrite/build/ascendancy --ui --resume --campaign 1 --seed 5 \
  >/tmp/t388_ui.log 2>&1 &
APP=$!
sleep 2
X() { DISPLAY=:81 ./tools/xsend "Ascendancy rewrite (P5a)" "$@"; sleep 1; }
X 553 145      # STATUS button centre (474,130-632,160) -> Planets screen
X key Escape   # -> map
X 553 310      # overlap-zone click on the MAP -> RACES (species menu)
X 553 310      # inside the species menu -> Intelligence (STATE "1 7")
X key Escape   # -> map
X 510 66       # NEXTTURN -> turn advances
sleep 1
kill $APP 2>/dev/null
kill $XV 2>/dev/null
echo "=== app log ==="
cat /tmp/t388_ui.log
