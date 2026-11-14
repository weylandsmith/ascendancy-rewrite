#!/usr/bin/env bash
# t387 dev check (bounded): gate 4c-c segment standalone — LOAD open with
# real slot dir, Esc cancel, RESUME, NEXT TURN, clean exit.
set -u
cd "$(dirname "$0")/.."
rm -rf /tmp/gate_saves_t387 && mkdir -p /tmp/gate_saves_t387
printf '\x2a\x04\x00\x00' > /tmp/gate_saves_t387/01.sav  # day 1066
Xvfb :81 -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=:81 ./rewrite/build/ascendancy --ui --campaign 1 \
  --seed 5 --saves /tmp/gate_saves_t387 >/tmp/gate_ui_load.log 2>&1 &
APP=$!
sleep 2
DISPLAY=:81 ./tools/xsend "Ascendancy" 318 375 || echo FAIL-load
sleep 1
DISPLAY=:81 ./tools/xsend "Ascendancy" key Escape || echo FAIL-esc
sleep 1
DISPLAY=:81 ./tools/xsend "Ascendancy" 318 335 || echo FAIL-resume
sleep 1
DISPLAY=:81 ./tools/xsend "Ascendancy" 510 66 || echo FAIL-nextturn
timeout 30 wait $APP; RC=$?
kill $XV 2>/dev/null
echo "RC=$RC"
cat /tmp/gate_ui_load.log
