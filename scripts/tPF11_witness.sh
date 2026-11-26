#!/usr/bin/env bash
# tPF-11 RESEARCH-CHROME WITNESS (D28 item 22). Legs:
#   (1) open a fresh campaign, click RESEARCH rail (553,223 — tPF-10 law);
#   (2) shoot the research screen; census it against the MEASURED chrome
#       law (scripts/tPF11_witness_census.py): perimeter bands, header
#       speckle, ramp 38..45, black y46/x7, panel band + well, NO tan box,
#       NO gray inventions;
#   (3) Escape back to the map and shoot it — the MAP chrome must be
#       UNCHANGED (frameTex law; the split is two-way).
# Scratch Xvfb :99, kill BY PID. Build run_tests AND ascendancy first
# (tPF-3e trap).
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/tpf11_shots}
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
X 553 223            # RESEARCH rail -> state 20
sleep 1
shot research_chrome
X key Escape
X 553 223            # re-enter (chrome must survive re-entry)
sleep 1
shot research_reentry
X key Escape         # back to map
sleep 1
shot map_after
kill $APP 2>/dev/null; kill $XV 2>/dev/null
wait $APP 2>/dev/null; wait $XV 2>/dev/null

"$PY" scripts/tPF11_witness_census.py "$OUT/research_chrome.png" | tee "$OUT/census1.out"
"$PY" scripts/tPF11_witness_census.py "$OUT/research_reentry.png" | tee "$OUT/census2.out"
grep -q "VERDICT PASS" "$OUT/census1.out" && grep -q "VERDICT PASS" "$OUT/census2.out" \
  && echo "VERDICT PASS" || { echo "VERDICT FAIL"; exit 1; }
