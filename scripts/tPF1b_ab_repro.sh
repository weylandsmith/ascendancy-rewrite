#!/usr/bin/env bash
# tPF-1b REPRO A/B (steering 2026-11-26): discriminate launcher-flag vs game
# law for D28 P7 ("advancing a single day at a time, the game exits after 20
# days"). Evidence chain: "ui ok: turn 20" is ui.cpp:3686 (clean return),
# reachable via the cap ui.cpp:1553 ONLY when turns>0, which on the Begin
# path is exclusively o.campaign (main.cpp:665).
#   A: --ui --campaign 20, Begin-built, xsend NEXT TURN x20 -> expect cap
#      line + "ui ok: turn 20" + exit 0.
#   B: --ui ALONE (turns=0, cap cannot fire), Begin-built, NEXT TURN x40 ->
#      expect ALIVE at turn 40 and NO cap line.
# If A prints and B survives: tPF-1b CLOSES as launcher-flag. If B also dies
# at 20: real defect, instrument quit paths.
# Begin path click sequence verbatim from scripts/tNGB4_begin_shot.sh law
# (neutral first click, FRESHGAME 318,295, BEGIN 566,422, intro dismiss
# 320,450). Scratch Xvfb :96, kill BY PID (host law).
set -u
cd /home/hrethric/projects/ascendancy
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/tpf1b_ab}
DISP=${DISP:-:96}
rm -rf "$OUT"; mkdir -p "$OUT"
rm -f /tmp/.X96-lock /tmp/.X11-unix/X96
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
X() { DISPLAY=$DISP ./tools/xsend "Ascendancy" click "$@" 2>>"$OUT/$1.log"; sleep 1; }

begin_run() { # $1 = log name, $2.. = extra app args
  local LOG=$1; shift
  DISPLAY=$DISP SDL_AUDIODRIVER=dummy "$BIN" --ui --seed 5 "$@" >"$OUT/$LOG" 2>&1 &
  APP=$!
  sleep 4
  X 320 60      # neutral first click (first-click law)
  X 318 295     # FRESHGAME -> raceconfig
  X 566 422     # BEGIN NEW GAME (kBeginNewGameBtn 494,373-639,472)
  sleep 2
  X 320 450     # dismiss race intro -> campaign map
  sleep 1
}

echo "===== REPRO A: --ui --campaign 20 (Begin-built), NEXT TURN x20 ====="
begin_run appA.log --campaign 20
DIED_AT=""
for i in $(seq 20); do
  X 511 67      # NEXT TURN (kNextTurnBtn 474,52-548,82)
  if ! kill -0 $APP 2>/dev/null; then DIED_AT=$i; break; fi
done
for w in $(seq 10); do kill -0 $APP 2>/dev/null || break; sleep 1; done
wait $APP 2>/dev/null; RC=$?
echo "A: exit_code=$RC died_at_press=${DIED_AT:-never} presses_logged=$(grep -c 'ui click next-turn' "$OUT/appA.log")"
grep -n "turn cap\|ui ok: turn" "$OUT/appA.log"
cp "$OUT/appA.log" /tmp/tpf1b_A_app.log
if grep -q "ui ok: turn 20" "$OUT/appA.log"; then
  echo "A-VERDICT: printed 'ui ok: turn 20' (cap path), died_at_press=${DIED_AT:-loop-completed}, exit=$RC"
elif grep -q "ui ok: turn" "$OUT/appA.log"; then
  echo "A-VERDICT: printed ui ok but NOT turn 20 — inspect"
else
  echo "A-VERDICT: NO ui ok line — unexpected"
fi

echo "===== REPRO B: --ui ALONE (no --campaign), Begin-built, NEXT TURN x40 ====="
begin_run appB.log
DIED_AT_B=""
for i in $(seq 40); do
  X 511 67
  if ! kill -0 $APP 2>/dev/null; then DIED_AT_B=$i; break; fi
done
sleep 1
if kill -0 $APP 2>/dev/null; then
  echo "B-VERDICT: ALIVE after 40 presses (presses_logged=$(grep -c 'ui click next-turn' "$OUT/appB.log")) cap_lines=$(grep -c 'turn cap' "$OUT/appB.log")"
  kill $APP 2>/dev/null
else
  echo "B-VERDICT: DIED at press $DIED_AT_B (presses_logged=$(grep -c 'ui click next-turn' "$OUT/appB.log"))"
  tail -8 "$OUT/appB.log"
fi
cp "$OUT/appB.log" /tmp/tpf1b_B_app.log
kill $XV 2>/dev/null
wait 2>/dev/null
echo DONE
