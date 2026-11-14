#!/usr/bin/env bash
# t388b witness: intro cue table fires on a live run (not a unit fixture).
# Click Play Introduction (vendor rect 159,200-477,230 centre 318,215),
# let the movie pass frame 20 (71 ms/frame -> ~1.5 s), press a key to abort
# (ui.cpp intro loop abort law), then Esc quits from the title.
set -u
ROOT=/home/hrethric/projects/ascendancy
rm -f /tmp/.X81-lock /tmp/.X11-unix/X81
Xvfb :81 -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=:81 SDL_AUDIODRIVER=dummy "$ROOT/rewrite/build/ascendancy" --ui --audio --audio-trace >/tmp/t388b_intro.log 2>&1 &
APP=$!
sleep 2
DISPLAY=:81 "$ROOT/tools/xsend" "Ascendancy" 318 215 || echo XSEND1_FAIL
sleep 3
# abort the movie with a key, then let SIGINT tear down
DISPLAY=:81 "$ROOT/tools/xsend" "Ascendancy" key space 2>/dev/null || true
sleep 1
kill -INT $APP 2>/dev/null
sleep 1
kill $APP 2>/dev/null
kill $XV 2>/dev/null
grep -E 'audio|music|sfx|intro|title' /tmp/t388b_intro.log
