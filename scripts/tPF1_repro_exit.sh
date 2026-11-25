#!/usr/bin/env bash
# tPF-1(b) REPRO: "advancing a single day at a time, the game exits after 20
# days" (D28 P7). Discriminator between the FLAG path (--campaign N in --ui
# mode IS the turn cap, main.cpp:665 -> ui.cpp:1215) and a REAL loop-
# terminating defect: launch EXACTLY the README interactive command
# (`--ui`, no --campaign => turns=0 => cap cannot fire) and press NEXT TURN
# 30 times. If the app dies, the exit is a real defect, not the flag.
# Scratch Xvfb :99, kill BY PID (host law).
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/tpf1_repro}
DISP=${DISP:-:99}
rm -rf "$OUT"; mkdir -p "$OUT"
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP SDL_AUDIODRIVER=dummy "$BIN" --ui --seed 5 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 3
X() { DISPLAY=$DISP ./tools/xsend "Ascendancy" "$@"; sleep 1; }
X 318 335            # RESUME -> campaign map
ALIVE_BEFORE=$(kill -0 $APP 2>/dev/null && echo yes || echo no)
DIED_AT=""
for i in $(seq 30); do
  X 511 67           # NEXT TURN (kNextTurnBtn 474,52-548,82)
  if ! kill -0 $APP 2>/dev/null; then DIED_AT=$i; break; fi
done
sleep 1
if kill -0 $APP 2>/dev/null; then
  echo "VERDICT ALIVE after 30 presses (clicks logged: $(grep -c 'ui click next-turn' "$OUT/app.log"))"
else
  echo "VERDICT DIED at press $DIED_AT (clicks logged: $(grep -c 'ui click next-turn' "$OUT/app.log"))"
fi
echo "--- tail app.log"
tail -6 "$OUT/app.log"
kill $APP 2>/dev/null; kill $XV 2>/dev/null
wait 2>/dev/null
[ -z "$DIED_AT" ]
