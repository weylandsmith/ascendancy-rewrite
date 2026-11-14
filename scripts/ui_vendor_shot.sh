#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

# One-shot dev check (NOT a gate stage): boot the campaign UI with the vendor
# .fnt faces under Xvfb, autoplay some turns, capture the screen for a vision
# read. Kills only its own Xvfb pid. Bounded by timeout on the app.
set -u
cd "$(dirname "$0")/.."
OUT=${1:-/tmp/ui_vendor_fonts.png}
DISPLAY_NUM=${2:-79}
Xvfb ":$DISPLAY_NUM" -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=":$DISPLAY_NUM" timeout 30 ./rewrite/build/ascendancy --ui --resume \
  --campaign 40 --autoplay --seed 2024 >/tmp/ui_vendor_run.log 2>&1 &
APP=$!
sleep 6
DISPLAY=":$DISPLAY_NUM" import -window root "$OUT" 2>/dev/null
kill "$APP" 2>/dev/null
kill "$XV" 2>/dev/null
echo "shot: $OUT"
cat /tmp/ui_vendor_run.log
