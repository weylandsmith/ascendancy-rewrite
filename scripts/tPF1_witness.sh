#!/usr/bin/env bash
# tPF-1 WITNESS (D28 P7 time controls; law help.txt help 1next2 + windows.txt
# ln556; working log docs/re/_wip_tPF1.md). Stages on scratch seed 5:
#   stage1  manual NEXT TURN x3 -> turn 3 (cont OFF; no "ui cont advance")
#   stage2  click NEXTTURNCONT (557,52-632,82) -> pump runs ("ui cont
#           advance tN" lines appear WITHOUT any click); app must STAY ALIVE
#   stage3  manual NEXT TURN press -> "ui cont advance cancelled", pump stops
# Companion for the exit-flag repro (b): scripts/tPF1_repro_exit.sh.
# Scratch Xvfb :99, kill BY PID (host law).
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/tpf1_shots}
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
fail() { echo "FAIL  $1"; kill $APP 2>/dev/null; kill $XV 2>/dev/null; echo VERDICT FAIL; exit 1; }
X 318 335            # RESUME -> campaign map
for i in 1 2 3; do X 511 67; done          # manual NEXT TURN x3
grep -q "ui ok: turn\|ui click next-turn" "$OUT/app.log" || fail "no manual advance logged"
N_MANUAL=$(grep -c "ui click next-turn$" "$OUT/app.log")
[ "$N_MANUAL" = "3" ] || fail "expected 3 manual clicks, got $N_MANUAL"
grep -q "ui cont advance t" "$OUT/app.log" && fail "pump ran before NEXTTURNCONT press"
X 594 67             # NEXTTURNCONT (centre of 557,52-632,82)
sleep 3              # ~12 pump ticks at 250 ms if latched
kill -0 $APP 2>/dev/null || fail "app died during continuous advance"
N_CONT=$(grep -c "ui cont advance t" "$OUT/app.log")
[ "$N_CONT" -ge 3 ] || fail "continuous pump produced only $N_CONT ticks"
echo "pump ticks after NEXTTURNCONT: $N_CONT"
grep "ui cont advance stop" "$OUT/app.log" || true
X 511 67             # manual press must CANCEL the pump
grep -q "ui cont advance cancelled" "$OUT/app.log" || fail "manual press did not cancel"
N_AFTER=$(grep -c "ui cont advance t" "$OUT/app.log")
sleep 2
N_FINAL=$(grep -c "ui cont advance t" "$OUT/app.log")
[ "$N_FINAL" = "$N_AFTER" ] || fail "pump still ticking after cancel ($N_AFTER -> $N_FINAL)"
kill -0 $APP 2>/dev/null || fail "app died after cancel"
kill $APP 2>/dev/null; kill $XV 2>/dev/null
wait 2>/dev/null
echo VERDICT PASS
