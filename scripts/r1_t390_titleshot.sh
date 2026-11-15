#!/bin/bash
# t390 diagnostic: launch --ui on Xvfb :9, screenshot, kill.
cd /home/hrethric/projects/ascendancy
pgrep -x Xvfb >/dev/null || { (Xvfb :9 -screen 0 1024x768x24 >/dev/null 2>&1 &); sleep 2; }
ls -la extracted/ascend01/data/0*pening* 2>/dev/null | head -4
DISPLAY=:9 ./rewrite/build/ascendancy --data /tmp/uishow --ui --seed 1 > /tmp/titleui.log 2>&1 &
UIPID=$!
sleep 4
DISPLAY=:9 import -window root /tmp/title_shot.png 2>&1 && echo SHOT_OK
kill $UIPID 2>/dev/null
sleep 1
head -5 /tmp/titleui.log
