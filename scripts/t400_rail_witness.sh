#!/usr/bin/env bash
# t400 witness: rail icon placement (RIGHT of label), species flags, frame
# texture, title HOVER fill. Screenshots -> $OUT (USER grading) and the
# mechanical census decides (scripts/t400_witness_census.py).
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/t400_shots}
DISP=${DISP:-:98}
rm -rf "$OUT"; mkdir -p "$OUT"
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP "$BIN" --ui --campaign 1 --seed 5 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 3
shot() { DISPLAY=$DISP import -window root "$OUT/$1.png" 2>>"$OUT/app.log"; }
X() { DISPLAY=$DISP ./tools/xsend "Ascendancy" "$@"; sleep 1; }
# HOVER witness: xsend moves the pointer (it warps before the click); hover
# WITHOUT clicking is what we need — xsend only clicks, so use xdotool-style
# motion via xsend's motion? xsend clicks only; instead hover via a motion:
# the port reads SDL_GetMouseState, which tracks the X pointer. Use
# xdotool if present, else xsend's pre-click warp leaves the pointer ON the
# button after the click — so instead: click LOAD (opens load screen), Esc
# back to title with the pointer LEFT at 318,375 (inside LOAD) -> the title
# frame now renders LOAD hovered.
X 318 375            # LOAD -> load screen (pointer now 318,375)
X key Escape         # back to Title, pointer still on LOAD's rect
shot title-hover     # LOAD band must read fill (0,28,36)
X 318 295            # FRESH GAME -> New Game screen
X 566 422            # Begin New Game (494,373)-(639,472) -> campaign map
shot map
kill $APP 2>/dev/null; kill $XV 2>/dev/null
grep -E "ui palette|raceflag" "$OUT/app.log"
echo DONE
