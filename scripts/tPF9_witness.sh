#!/usr/bin/env bash
# tPF-9 STRAY-TEXT WITNESS (D28 item 13). Legs (docs/re/_wip_tPF9.md P1):
#   (1) planet view at IDLE: no text ink in the PLBUILD bottom strip (the
#       "click: set project" site) nor the bottom-left (the Esc-label site);
#   (2) CONTROL: open the project list -> "list open: pick one" MUST paint
#       in the UR strip (proves the census sees text where text exists);
#   (3) research screen: no ink in the bottom-left Esc-label box.
# Scratch Xvfb :99, kill BY PID (host law). Build BOTH run_tests AND
# ascendancy before running (tPF-3e trap).
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/tpf9_shots}
DISP=${DISP:-:99}
PY=${PY:-$HOME/tools/revenv/bin/python}
rm -rf "$OUT"; mkdir -p "$OUT"
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP SDL_AUDIODRIVER=dummy "$BIN" --ui --campaign 1 --seed 5 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 3
X() { DISPLAY=$DISP ./tools/xsend "Ascendancy" "$@"; sleep 1; }
shot() { sleep 0.3; DISPLAY=$DISP import -window root -crop 640x480+0+0 +repage "$OUT/$1.png" 2>>"$OUT/app.log"; }
X 318 335            # RESUME -> campaign map
X 553 145            # STATUS rail -> planets list
X 300 175            # row 0 -> planet view (state 17)
shot planet_idle
X 540 55             # PLBUILD panel -> project list opens
shot list_open
X key Escape         # close list (routing behaviour leg stays alive)
X key Escape         # back to galaxy map
X 553 223            # RESEARCH rail -> state 20
shot research
kill $APP 2>/dev/null; kill $XV 2>/dev/null
wait $APP 2>/dev/null; wait $XV 2>/dev/null
grep -E "ui planet project-list open|ui research" "$OUT/app.log" | head -3
"$PY" scripts/tPF9_witness_census.py "$OUT/planet_idle.png" "$OUT/list_open.png" "$OUT/research.png" | tee "$OUT/census.out"
grep -q "VERDICT PASS" "$OUT/census.out" && echo "VERDICT PASS" || { echo "VERDICT FAIL"; exit 1; }
