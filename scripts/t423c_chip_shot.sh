#!/usr/bin/env bash
# t423c witness: New Game screen, click player-colour chip idx 3 (pink),
# expect the DESC ring to switch to racering k3 + the reassign log line.
set -u
cd /home/hrethric/projects/ascendancy
BIN=./rewrite/build/ascendancy
OUT=/tmp/t423c_shots
DISP=${DISP:-:97}
rm -rf "$OUT"; mkdir -p "$OUT"
pkill -x ascendancy 2>/dev/null || true
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP SDL_AUDIODRIVER=dummy "$BIN" --data /tmp/uishow --ui --campaign 1 --seed 5 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 4
DISPLAY=$DISP ./tools/xsend "Ascendancy" click 320 60 2>>"$OUT/app.log"
sleep 1
DISPLAY=$DISP ./tools/xsend "Ascendancy" click 318 295 2>>"$OUT/app.log"
sleep 1
DISPLAY=$DISP import -window root "$OUT/before.png" 2>>"$OUT/app.log"
# chip idx 3 hit-zone centre: x = 0x17b + 3*16 + 8 = 435, y = 446 (zone 420..472)
DISPLAY=$DISP ./tools/xsend "Ascendancy" click 435 446 2>>"$OUT/app.log"
sleep 1
DISPLAY=$DISP import -window root "$OUT/after.png" 2>>"$OUT/app.log"
kill $APP 2>/dev/null; kill $XV 2>/dev/null
grep -E "player colour idx" "$OUT/app.log"
echo SHOT "$OUT/before.png" "$OUT/after.png"
