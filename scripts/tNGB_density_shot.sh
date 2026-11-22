#!/usr/bin/env bash
# tNG-B B1 WITNESS: the density wheel must REBUILD the preview galaxy —
# law docs/re/_wip_tNGB.md (vendor 0x52db9..0x52e57 full-regen, rand
# consumer). Assertions live in the python step below this script; here we
# capture the cosmos rect + Begin panel at every rung.
set -u
cd /home/hrethric/projects/ascendancy
BIN=./rewrite/build/ascendancy
OUT=/tmp/tNGB_density
DISP=${DISP:-:97}
rm -rf "$OUT"; mkdir -p "$OUT"
pkill -x ascendancy 2>/dev/null || true
if ! pgrep -f "Xvfb $DISP" >/dev/null; then
  Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
  sleep 1
fi
DISPLAY=$DISP SDL_AUDIODRIVER=dummy "$BIN" --data /tmp/uishow --ui --campaign 1 --seed 5 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 4
DISPLAY=$DISP ./tools/xsend "Ascendancy" click 320 60 2>>"$OUT/app.log"   # neutral
sleep 1
DISPLAY=$DISP ./tools/xsend "Ascendancy" click 318 295 2>>"$OUT/app.log"  # FRESHGAME -> raceconfig
sleep 1
DISPLAY=$DISP import -window root "$OUT/rung0.png" 2>>"$OUT/app.log"
# Density panel centre ~ (64,435) (kNewgameControls[0].rect 7..122 x 381..472)
# SIX clicks so the rung cycle WRAPS back to 75 (gen1 vs gen6 pair): a
# frozen regen seed repeats h15 on that pair (witness set-identity law).
for k in 1 2 3 4 5 6; do
  DISPLAY=$DISP ./tools/xsend "Ascendancy" click 64 435 2>>"$OUT/app.log"
  sleep 1
  DISPLAY=$DISP import -window root "$OUT/rung$k.png" 2>>"$OUT/app.log"
done
kill $APP 2>/dev/null
grep -E "galaxy regen|raceconfig click GALAXY" "$OUT/app.log"
echo SHOTS "$OUT"/rung*.png
