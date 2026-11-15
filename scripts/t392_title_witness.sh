#!/usr/bin/env bash
# t392 witness: boot to Title in ONE window (t385b law), screenshot, then
# Esc must exit the title loop (live input-path proof; Alt-chords need a
# real keyboard — xsend sends one keysym with no modifier state, and the
# hotkey routing itself is unit-pinned in test_titletext_t392.cpp).
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/t392_shots}
DISP=${DISP:-:97}
rm -rf "$OUT"; mkdir -p "$OUT"
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP "$BIN" --ui --campaign 1 --seed 5 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 4
DISPLAY=$DISP import -window root "$OUT/title.png" 2>>"$OUT/app.log"
DISPLAY=$DISP ./tools/xsend "Ascendancy" key Escape 2>>"$OUT/app.log"
sleep 1
if kill -0 $APP 2>/dev/null; then
  echo "FAIL: ALIVE_AFTER_ESC" >>"$OUT/app.log"
else
  echo "OK: EXITED_AFTER_ESC" >>"$OUT/app.log"
fi
kill $APP 2>/dev/null; kill $XV 2>/dev/null
echo DONE
