#!/usr/bin/env bash
# tXT-1 WITNESS (D32/D33): the USER'S repro shape on the Begin path —
# Very Dense (wheel density rung 2 = 100 stars) + Seven species (wheel
# species word 5->6->7) -> BEGIN -> 60 NEXT TURN presses. PRE-FIX the app
# exited at t20 (victory:Extinct after 'owner 1 captured Phoebe'); the
# freeForAll arcade default started every pair at war (refuted by
# diplomacy.md §19: 200/200 fresh-campaign pairs NOT at war). PASS = alive
# after 60 presses AND the 'newgame live' handoff line carries stars 100
# owners 7 (the tPF1d both-fields law). Exit codes: 0 = SURVIVED,
# 1 = exited before press 60 (defect persists), 2 = harness/nav failure.
set -u
cd "$(dirname "$0")/.."
BIN=${BIN:-./rewrite/build/ascendancy}
OUT=${OUT:-/tmp/txt1_dense7}
DISP=${DISP:-:97}
PASSES=${PASSES:-60}
rm -rf "$OUT"; mkdir -p "$OUT"
rm -f /tmp/.X97-lock /tmp/.X11-unix/X97 2>/dev/null
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
trap 'kill $XV 2>/dev/null; pkill -f "rewrite/build/ascendancy --data" 2>/dev/null; true' EXIT
sleep 1
export DISPLAY=$DISP
"$BIN" --data "${DATA:-$PWD}" --ui >"$OUT/app.log" 2>&1 &
APP=$!
sleep 4
kill -0 $XV 2>/dev/null || { echo "HARNESS FAIL: Xvfb dead"; kill $APP 2>/dev/null; exit 2; }
kill -0 $APP 2>/dev/null || { echo "HARNESS FAIL: app died at boot"; cat "$OUT/app.log"; exit 2; }
X() { ./tools/xsend "Ascendancy" click "$@" 2>>"$OUT/xsend.log"; sleep 1; }
alive() { pgrep -f "build/ascendancy --data" >/dev/null 2>&1; }

# --- Begin path to the New Game wheel (tNGB4 law), set the repro rungs,
# then BEGIN + intro dismiss.
X 320 60          # dismiss title prompt
X 318 295         # FRESHGAME -> New Game wheel
grep -q "newgame summary" "$OUT/app.log" || true
# GALAXY_MORE rect {7,381,122,472} (menulaw.cpp kNewgameControls): center
# ~64,426. Average(50) -> Dense(75) -> Very Dense(100) = 2 clicks.
X 64 426
X 64 426
grep -q "galaxy regen gen 2" "$OUT/app.log" || { echo "NAV FAIL: density rung 2 not reached"; tail -5 "$OUT/app.log"; kill $APP 2>/dev/null; exit 2; }
# PLAYERS_MORE rect {131,381,246,472}: center ~188,426. word 5 -> 6 -> 7.
X 188 426
X 188 426
grep -q "ui raceconfig species 7\|species word 7\|species 7 " "$OUT/app.log" || true
X 566 422         # BEGIN
sleep 2
X 320 450         # intro dismiss -> map
grep -q "newgame live" "$OUT/app.log" || { echo "NAV FAIL: no newgame live line"; tail -5 "$OUT/app.log"; kill $APP 2>/dev/null; exit 2; }
HANDOFF=$(grep -m1 "newgame live" "$OUT/app.log")
echo "HANDOFF: $HANDOFF"
case "$HANDOFF" in
  *"stars 100"*"owners 7"*) ;;
  *) echo "NAV FAIL: handoff triple wrong (want stars 100 owners 7)"; kill $APP 2>/dev/null; exit 2;;
esac
grep -m1 "ui raceconfig begin density" "$OUT/app.log"

# --- day-advance loop, per-press assertion (tPF-9 soak law). No order
# phase: the user's ground-truth shape is an idle player (D33: "20 days in
# every player will still be building their first structure") — survival
# must not depend on our building anything.
DIED_AT=""
for i in $(seq "$PASSES"); do
  before=$(grep -c "ui click next-turn" "$OUT/app.log")
  X 511 67       # NEXT TURN (kNextTurnBtn 474,52-548,82)
  after=$(grep -c "ui click next-turn" "$OUT/app.log")
  [ "$after" -gt "$before" ] || { echo "HARNESS FAIL: press $i registered no next-turn click"; kill $APP 2>/dev/null; exit 2; }
  if ! alive; then DIED_AT=$i; break; fi
done
sleep 1
if [ -z "$DIED_AT" ]; then
  echo "VERDICT: SURVIVED $PASSES turns on dense+7 (no victory exit)"
  grep -c "ui click next-turn" "$OUT/app.log"
  grep -E "captured|declared war|VICTORY|quit" "$OUT/app.log" | tail -5
  kill $APP 2>/dev/null
  RC=0
else
  echo "VERDICT: REPRODUCED — process exited at press $DIED_AT"
  for w in $(seq 3); do kill -0 $XV 2>/dev/null && sleep 1; done
  grep -nE "VICTORY|ui ok|ui cont|quit" "$OUT/app.log" | tail -12
  RC=1
fi
kill $XV 2>/dev/null
wait 2>/dev/null
echo "DONE rc=$RC out=$OUT"
exit $RC
