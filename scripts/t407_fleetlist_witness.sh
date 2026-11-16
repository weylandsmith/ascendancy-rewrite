#!/usr/bin/env bash
# t407 witness: SHIPS LIST (state 18) renders the campaign's ship census.
# THE TIMING LAW (measured this session, probe over the real buildCampaign
# path): on --seed 5 the player's planitem queue reaches Shipyard at t198 and
# the FIRST ship is in transit exactly between turn 278 and 279 (it colonises
# at t280; the model holds ships ONLY in transit — named seam). So the
# witness clicks NEXTTURN 277 times, then probes (open Ships, click row 0,
# Esc) once per turn — deterministic, no injected state.
# Boot WITHOUT --campaign N (that caps UI turns; first NEXTTURN would quit).
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/t407_shots}
DISP=${DISP:-:97}
rm -rf "$OUT"; mkdir -p "$OUT"
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP SDL_AUDIODRIVER=dummy "$BIN" --ui --seed 5 --audio-trace >"$OUT/app.log" 2>&1 &
APP=$!
sleep 3
shot() { DISPLAY=$DISP import -window root "$OUT/$1.png" 2>>"$OUT/app.log"; }
X() { DISPLAY=$DISP ./tools/xsend "Ascendancy" "$@"; sleep 0.05; }
K() { DISPLAY=$DISP ./tools/xsend "Ascendancy" key "$1"; sleep 0.4; }
X 318 335            # RESUME -> campaign map
sleep 1
for i in $(seq 1 277); do X 511 67; done   # NEXTTURN x277 (map only)
found=0
for i in $(seq 1 8); do
    X 553 184          # rail Ships -> state 18
    X 300 105          # row 0 centre (rows top 52, pitch 106)
    if grep -q "ui fleet select" "$OUT/app.log"; then found=1; shot fleet-rows; break; fi
    K Escape           # back to map
    X 511 67           # one more turn
done
echo "--- found=$found"
[ $found = 1 ] || shot fleet-norows
# Interaction sequence (screen open; row 0 selected if found):
X click3 300 105     # RIGHT-click deselect (selfplay law)
X 620 453            # scroll-down arrow box (measured)
X 620 63             # scroll-up arrow box
X 620 250            # trough click: inert (no log expected)
shot fleet-final
K Escape
kill $APP 2>/dev/null; kill $XV 2>/dev/null
echo "--- log lines:"
grep -E "ui screen .*-> Ships|ui fleet" "$OUT/app.log" | head -20
pass=1
grep -q "ui fleet select row" "$OUT/app.log" \
  && echo "PASS  row click selects (census non-empty, hit-map live)" \
  || { echo "FAIL  no row select (census never non-empty or hit-map dead)"; pass=0; }
grep -q "ui fleet deselect" "$OUT/app.log" \
  && echo "PASS  right-click deselect (selfplay law)" \
  || echo "NOTE  no deselect line (check select above)"
grep -q "ui fleet scroll" "$OUT/app.log" \
  && echo "PASS  arrow boxes scroll" \
  || echo "NOTE  no scroll line (a <=4-ship list cannot scroll — honest)"
if grep -q "laser01" "$OUT/app.log"; then echo "FAIL  laser01 regression (t404 law)"; pass=0
else echo "PASS  zero laser01"; fi
[ $pass = 1 ] && echo VERDICT PASS || echo VERDICT FAIL
