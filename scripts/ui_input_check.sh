#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

# dev check (bounded): does synthetic input reach the app? autoplay keeps
# the app exit-able even if no clicks land. Prints app log tail.
set -u
BIN=${1:-./rewrite/build/ascendancy}
Xvfb :77 -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=:77 "$BIN" --ui --autoplay --campaign 4 >/tmp/ui_in.log 2>&1 &
APP=$!
sleep 3
echo "-- xsend next-turn (510,66):"
DISPLAY=:77 ./tools/xsend "Ascendancy" 510 66; echo "rc=$?"
sleep 1
echo "-- xsend map (140,160):"
DISPLAY=:77 ./tools/xsend "Ascendancy" 140 160; echo "rc=$?"
wait $APP; rc=$?
kill "$XV" 2>/dev/null
echo "APP_EXIT=$rc"
grep -E '^ui (click|key)' /tmp/ui_in.log || echo "NO-EVENTS-SEEN"
