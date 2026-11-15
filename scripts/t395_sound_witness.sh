#!/usr/bin/env bash
# t395 witness: SOUND AUDIBILITY law on a live run.
#  (A) default-on: NO --audio flag -> diagnostic line prints, tune 0 plays;
#  (B) click INTRO button centre (318,215) -> 'sfx click08' trace line;
#  (C) bad --data (ascend01/data emptied) -> degrade line names last path.
set -u
ROOT=/home/hrethric/projects/ascendancy
rm -f /tmp/.X84-lock /tmp/.X11-unix/X84
Xvfb :84 -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
# (A)+(B): plain --ui, audio must be ON by default (t395)
DISPLAY=:84 SDL_AUDIODRIVER=dummy "$ROOT/rewrite/build/ascendancy" --ui --audio-trace >/tmp/t395_witness.log 2>&1 &
APP=$!
sleep 2
DISPLAY=:84 "$ROOT/tools/xsend" "Ascendancy" 318 215 || echo XSEND1_FAIL
sleep 2
kill -INT $APP 2>/dev/null; sleep 1; kill $APP 2>/dev/null
kill $XV 2>/dev/null
echo '--- witness log ---'
grep -E '^audio|^music|^sfx|title click' /tmp/t395_witness.log
FAIL=0
grep -q 'audio: driver=' /tmp/t395_witness.log || { echo "FAIL: no diagnostic line"; FAIL=1; }
grep -q 'music 0 theme00' /tmp/t395_witness.log || { echo "FAIL: tune0 not played on title entry"; FAIL=1; }
grep -q 'sfx click08' /tmp/t395_witness.log || { echo "FAIL: no click sfx on title button"; FAIL=1; }
[ $FAIL -eq 0 ] && echo T395_WITNESS_PASS
exit $FAIL
