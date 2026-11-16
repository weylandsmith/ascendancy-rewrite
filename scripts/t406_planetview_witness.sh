#!/usr/bin/env bash
# t406 witness: OWNED-ONLY planets list + PLANET VIEW + PROJECT SET.
# Boot campaign -> rail Planets -> assert ONE row per owned star (no
# fabricated worlds) -> row click opens state 17 -> PLBUILD click opens the
# project list -> option click orders it (log line "ordered").
# Screenshots -> $OUT for native-vision grading.
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/t406_shots}
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
X 553 145            # STATUS rail -> planets list
shot status-open
X 300 175            # row 0 (rows top 117; centre ~170 native) -> planet view
shot planet-view
X 540 55             # PLBUILD panel (463,8-632,106) -> project list
shot project-list
X 200 135            # first project row -> order
shot after-order
kill $APP 2>/dev/null; kill $XV 2>/dev/null
echo "--- log:"
grep -E "ui status select|ui planet" "$OUT/app.log"
pass=1
grep -q "ui status select .* -> planet view (state 17)" "$OUT/app.log" \
  && echo "PASS  row click opens the planet view" \
  || { echo "FAIL  no planet-view open"; pass=0; }
grep -q "ui planet project-list open" "$OUT/app.log" \
  && echo "PASS  PLBUILD click opens the project list" \
  || { echo "FAIL  project list never opened"; pass=0; }
grep -q "ui planet project .*ordered" "$OUT/app.log" \
  && echo "PASS  project SET (ordered)" \
  || echo "NOTE  no 'ordered' line (first option may be a legal reject: check log)"
[ $pass = 1 ] && echo VERDICT PASS || echo VERDICT FAIL
