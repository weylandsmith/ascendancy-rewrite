#!/usr/bin/env bash
# t391 PRESENTATION SWEEP witness: one window (t385b law), screenshot per
# screen. Title -> LOAD -> Esc -> RESUME -> rail tour (STATUS/FLEET/RESEARCH/
# RACES/Intelligence) with `import -window root` after each transition.
# The app prints "ui screen A -> B (RAIL)" lines; the census script maps
# shots to screens by those lines, not by timing assumptions.
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/t391_shots}
DISP=${DISP:-:96}
rm -rf "$OUT"; mkdir -p "$OUT"
mkdir -p /tmp/t391_saves
python3 - <<'EOF'
import struct
open("/tmp/t391_saves/07.sav","wb").write(struct.pack('<I',300)+b'x'*256)
EOF
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP "$BIN" --ui --campaign 1 --seed 5 --saves /tmp/t391_saves >"$OUT/app.log" 2>&1 &
APP=$!
sleep 3
shot() { DISPLAY=$DISP import -window root "$OUT/$1.png" 2>>"$OUT/app.log"; }
X() { DISPLAY=$DISP ./tools/xsend "Ascendancy" "$@"; sleep 1; }

X 318 375            # LOAD button -> load screen
shot load
X key Escape         # -> Title
shot title
X 318 335            # RESUME -> campaign map
shot map
X 553 145            # rail STATUS -> Planets screen
shot status
X key Escape         # -> map
X 553 184            # rail FLEET
shot fleet
X key Escape
X 553 223            # rail RESEARCH
shot research
X key Escape
X 553 301            # rail RACES -> species menu
shot species
X 553 318            # Intelligence row (species-menu-only per STATE law)
shot intel
X key Escape         # species -> map
X key Escape         # map -> quit (t388 escape law)
wait $APP; RC=$?
kill $XV 2>/dev/null
echo "RC=$RC SHOTS=$(ls "$OUT"/*.png | wc -l)"
grep -E "ui screen|ui ok|load" "$OUT/app.log" | head -20
