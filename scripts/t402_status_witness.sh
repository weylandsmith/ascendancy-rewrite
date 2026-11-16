#!/usr/bin/env bash
# t402 witness: PLANETS LIST screen. Boot -> campaign map -> click STATUS rail
# button (kRail[0] {474,130,632,160}) -> shot; scroll down; click row 2; shot.
# Screenshots -> $OUT for USER grading.
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/t402_shots}
DISP=${DISP:-:96}
rm -rf "$OUT"; mkdir -p "$OUT"
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP "$BIN" --ui --campaign 1 --seed 5 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 3
shot() { DISPLAY=$DISP import -window root "$OUT/$1.png" 2>>"$OUT/app.log"; }
X() { DISPLAY=$DISP ./tools/xsend "Ascendancy" "$@"; sleep 1; }
X 318 335            # RESUME -> campaign map
X 553 145            # STATUS rail button centre -> STATUSWND planets list
shot status-open
X 599 445            # scroll-down arrow centre
shot status-scroll1
X 599 445            # scroll again
X 300 190            # row 2 hit (rows top 135.6? row0 centre ~191 native)
shot status-select
kill $APP 2>/dev/null; kill $XV 2>/dev/null
grep -E "ui rail STATUS|ui status" "$OUT/app.log"
echo DONE
