#!/usr/bin/env bash
# t385 dev check (bounded): title-screen click routing under Xvfb.
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
Xvfb :78 -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=:78 "$BIN" --ui --campaign 1 --seed 5 >/tmp/t385_title.log 2>&1 &
APP=$!
sleep 2
DISPLAY=:78 ./tools/xsend "Ascendancy" 318 100   # outside the column: no-op
sleep 1
DISPLAY=:78 ./tools/xsend "Ascendancy" 318 295   # FRESHGAME -> raceconfig
sleep 1
DISPLAY=:78 ./tools/xsend "Ascendancy" 318 335   # RESUME -> campaign
sleep 1
DISPLAY=:78 ./tools/xsend "Ascendancy" 510 66    # NEXT TURN
wait $APP; RC=$?
kill $XV 2>/dev/null
echo "RC=$RC"
cat /tmp/t385_title.log
