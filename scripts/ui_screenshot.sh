#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

# dev helper: screenshot the P5a UI mid-run (not part of the gate).
set -u
which import >/dev/null || { echo "ImageMagick import missing"; exit 2; }
Xvfb :77 -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=:77 "$@" >/tmp/ui_live.log 2>&1 &
APP=$!
sleep 4
DISPLAY=:77 import -window root /tmp/ui_shot1.png
sleep 6
DISPLAY=:77 import -window root /tmp/ui_shot2.png
kill $APP 2>/dev/null
kill $XV 2>/dev/null
wait 2>/dev/null
ls -la /tmp/ui_shot1.png /tmp/ui_shot2.png
cat /tmp/ui_live.log
