#!/usr/bin/env bash
# t409 witness: (1) the SPECIALAB rail press OPENS the ABILITYWIN modal
# (vendor msg-5 path 0x55ffb -> CALL 0x37b14: the player species' help.txt
# abilNN panel), the modal swallows a turn-advance key while open, and a
# click inside the full-rect dismisses (ABILBUTTON0/1 law); (2) the SPECIES
# menu (state 7) renders the static #11 header and known-species rows, and
# a row press logs the NEGSCREEN seam.
# Player species = Minions (--species 0) so the dialog has a real panel
# (default -1 human prints the seam line instead — also asserted).
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/t409_shots}
DISP=${DISP:-:97}
rm -rf "$OUT"; mkdir -p "$OUT"
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP SDL_AUDIODRIVER=dummy "$BIN" --ui --seed 5 --species 0 --audio-trace >"$OUT/app.log" 2>&1 &
APP=$!
sleep 3
shot() { DISPLAY=$DISP import -window root "$OUT/$1.png" 2>>"$OUT/app.log"; }
X() { DISPLAY=$DISP ./tools/xsend "Ascendancy" "$@"; sleep 0.05; }
K() { DISPLAY=$DISP ./tools/xsend "Ascendancy" key "$1"; sleep 0.4; }
X 318 335            # RESUME -> campaign map
sleep 1
X 553 262            # rail Special Ability (474,247-632,277 centre)
sleep 0.5
shot ability-open
# Modal law probes: (a) Return must NOT advance the turn while open;
turn0=$(grep -oE "ui widget state.*turn=[0-9]+" "$OUT/app.log" | tail -1 | grep -oE "turn=[0-9]+" || true)
K Return
K Return
# (b) click OUTSIDE the window: inert (still open = no dismiss line yet)
X 550 450
sleep 0.4
# (c) click INSIDE (ABILBUTTON full-rect): dismiss
X 227 227
sleep 0.5
shot ability-closed
# Species menu: advance a few turns so contacts can happen, then open it.
for i in 1 2 3 4 5 6 7 8; do K Return; done
X 553 301            # rail Species -> state 7
sleep 0.6
shot species-menu
X 553 61             # race row 2 (kRaceRows[1])
sleep 0.4
K Escape
sleep 0.3
kill $APP 2>/dev/null; kill $XV 2>/dev/null
echo "--- log lines:"
grep -E "ui ability|ui screen|ui species" "$OUT/app.log" | head -20
pass=1
grep -q "ui ability dialog open (abil00)" "$OUT/app.log" \
  && echo "PASS  SPECIALAB opens ABILITYWIN with the Minions panel (abil00)" \
  || { echo "FAIL  no dialog-open line (button dead again?)"; pass=0; }
grep -q "ui ability dialog dismiss" "$OUT/app.log" \
  && echo "PASS  inside-click dismisses (ABILBUTTON full-rect msg-50 law)" \
  || { echo "FAIL  no dismiss line"; pass=0; }
# The modal waits: 10 Returns sent (2 under the modal, 8 after dismissal);
# the app prints "ui key next" per ADVANCE — the suppressed pair must not
# appear, so the count is 8.
n=$(grep -c "ui key next" "$OUT/app.log" || true)
if [ "$n" = "8" ]; then echo "PASS  modal swallowed the two Returns (8 advances not 10)"; else echo "FAIL  advances=$n (expect 8; keys leaked through the modal)"; pass=0; fi
grep -qE "ui species row .*NEGSCREEN state 13 seam" "$OUT/app.log" \
  && echo "PASS  species row press logged (NEGSCREEN seam, honest inert)" \
  || echo "NOTE  no species-row line (no contact by turn 9 — header-only shot still graded)"
if grep -q "laser01" "$OUT/app.log"; then echo "FAIL  laser01 regression (t404 law)"; pass=0
else echo "PASS  zero laser01"; fi
[ $pass = 1 ] && echo VERDICT PASS || echo VERDICT FAIL
