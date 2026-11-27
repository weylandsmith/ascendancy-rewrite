#!/usr/bin/env bash
# tPF-1d CHAMACHI-EXACT SOAK (D31 steering 2026-11-27). The user's day-20
# exit is an UNREPRODUCED defect (Escape-at-bottom closure REFUTED: "the
# mouse never moved from the next day button"). This soak matches the USER's
# launch — `--data ROOT --ui`, NO --campaign (turns=0), seed default 1,
# Begin-built via wheel defaults 50/5/1 — with the ONE addition the port
# needs to make the scenario Chamachi-home: `--species 19` (Chamachies;
# tPL-D1 law guarantees the home planet is the Chamachi size-idx-3 class,
# so no seed reroll is needed — Chamachi-home holds BY CONSTRUCTION).
#
# D31 exit-code discipline: the run is only honest if every leg asserts its
# own log line (tPF-9 soak law). If the app exits, the tPF-1d instrument
# prints 'ui quit cause=<CAUSE> turn=N' BEFORE 'ui ok' — that cause names
# the path and the soak prints it. If 45 presses pass with the app alive
# AND zero 'ui quit cause' lines, the soak SURVIVED: say so, do not invent
# a user-behavior explanation.
#
# Exit codes: 0 = ALIVE after PRESSES with zero quit lines; 1 = exited
# early (REPRODUCED; the cause line is dumped); 2 = harness/nav failure.
set -u
cd "$(dirname "$0")/.."
BIN=${BIN:-./rewrite/build/ascendancy}
OUT=${OUT:-/tmp/tpf1d_soak}
DISP=${DISP:-:97}
PASSES=${PRESSES:-45}
rm -rf "$OUT"; mkdir -p "$OUT"
rm -f /tmp/.X97-lock /tmp/.X11-unix/X97 2>/dev/null
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
trap 'kill $XV 2>/dev/null; pkill -f "rewrite/build/ascendancy --data" 2>/dev/null; true' EXIT
sleep 1
export DISPLAY=$DISP
"$BIN" --data "${DATA:-$PWD}" --ui --species 19 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 4
kill -0 $XV 2>/dev/null || { echo "HARNESS FAIL: Xvfb dead"; kill $APP 2>/dev/null; exit 2; }
kill -0 $APP 2>/dev/null || { echo "HARNESS FAIL: app died at boot"; cat "$OUT/app.log"; exit 2; }
X() { ./tools/xsend "Ascendancy" click "$@" 2>>"$OUT/xsend.log"; sleep 1; }
alive() { pgrep -f "build/ascendancy --data" >/dev/null 2>&1; }

# --- Begin path (tNGB4 law, same nav as tPF1c_repro.sh): neutral click,
# FRESHGAME, BEGIN, intro dismiss.
X 320 60
X 318 295
X 566 422
sleep 2
X 320 450
sleep 1
grep -q "newgame live" "$OUT/app.log" || { echo "NAV FAIL: no newgame live line"; tail -5 "$OUT/app.log"; kill $APP 2>/dev/null; exit 2; }
grep -m1 "newgame live" "$OUT/app.log"
# Chamachi-home witness: owner 0 owns a planet; the species build line plus
# the tPL-D1 law (home size idx 3 for specnum 19) is the citation — the
# tile line below re-confirms a 45-cell-class home is reachable.

# --- FACTORY ORDER PENDING (tPF-2b click law, verbatim from tPF1c_repro).
X 553 145
X 300 100
grep -q "ui status select" "$OUT/app.log" || { echo "NAV FAIL: no status select"; kill $APP 2>/dev/null; exit 2; }
CB_LINE=$(grep 'ui planet home-cb' "$OUT/app.log" | tail -1)
PSIZE=$(echo "$CB_LINE" | sed -n 's/.*size \([0-9]\).*/\1/p')
[ -n "$PSIZE" ] || { echo "NAV FAIL: no size in home-cb line"; kill $APP 2>/dev/null; exit 2; }
echo "home planet size class idx $PSIZE (tPL-D1: Chamachi home is ALWAYS 3)"
CENTERS=$(python3 - "$PSIZE" <<'PY'
import sys
B=[0,0,0,0,4,4,5,0,0,0,0,0,0,0,0,
   0,0,0,4,3,4,5,6,0,0,0,0,0,0,0,
   0,0,0,3,2,3,3,4,5,7,0,0,0,0,0,
   0,1,1,2,2,3,4,5,7,0,0,0,0,0,0,
   1,0,0,0,1,1,2,3,4,5,7,0,0,0,0]
C=[0,0,0,0,2,3,2,0,0,0,0,0,0,0,0,
   0,0,0,1,3,3,3,1,0,0,0,0,0,0,0,
   0,0,0,1,4,4,5,4,4,1,0,0,0,0,0,
   0,0,2,5,6,6,7,6,6,5,2,0,0,0,0,
   3,6,7,8,8,9,8,8,7,6,3,0,0,0,0]
s=int(sys.argv[1]); cum=0
for row in range(15):
    for col in range(B[s*15+row], B[s*15+row]+C[s*15+row]):
        print(410+col*34-row*34, 127+col*17+row*17)
PY
)
BUILD_XY=""
while read -r c1 c2; do
  [ -n "$BUILD_XY" ] && break
  X $c1 $c2
  case "$(grep 'ui planet tile' "$OUT/app.log" | tail -1)" in
    *"ids=54"*) ;;   # BUILD popup open
    *) continue;;
  esac
  X 227 353          # Build button -> PLANLIST armed
  sleep 0.5
  case "$(grep 'ui planlist opts' "$OUT/app.log" | tail -1)" in
    *"n=0 "*)   # armed cell zero legal items: Escape -> STATUS, re-select
                # row 0 re-enters fresh (ui.cpp fresh-entry leg)
      ./tools/xsend "Ascendancy" key Escape 2>>"$OUT/xsend.log"; sleep 0.5
      X 300 100
      continue;;
  esac
  X 300 130          # PLANLIST row 0
  sleep 0.5
  if grep -qE "ordered( armed cell| \()" "$OUT/app.log"; then BUILD_XY="$c1 $c2"; break; fi
done <<< "$CENTERS"
[ -n "$BUILD_XY" ] || { echo "NAV FAIL: no cell produced an order"; kill $APP 2>/dev/null; exit 2; }
grep -E "ordered( armed cell| \()" "$OUT/app.log" | tail -1
alive || { echo "ORDER PHASE DIED — see $OUT/app.log"; tail -10 "$OUT/app.log"; grep -nE "ui quit cause" "$OUT/app.log"; exit 1; }
# back to the map from the planet view before the advance loop. The stack is
# Planet Display -> Planets -> map (t410 one-level unwind), so escape may
# need TWO presses; loop until the screen line says map (max 3, each press
# asserted by the screen-line count growing).
for e in 1 2 3; do
  before_s=$(grep -c "ui screen" "$OUT/app.log")
  ./tools/xsend "Ascendancy" key Escape 2>>"$OUT/xsend.log"; sleep 0.6
  after_s=$(grep -c "ui screen" "$OUT/app.log")
  [ "$after_s" -gt "$before_s" ] || { echo "HARNESS FAIL: escape $e logged no screen line"; kill $APP 2>/dev/null; exit 2; }
  case "$(grep "ui screen" "$OUT/app.log" | tail -1)" in
    *"-> map"*) break;;
  esac
done
grep -q "ui screen Planets -> map" "$OUT/app.log" || { echo "NAV FAIL: not on map after order-phase escape"; tail -4 "$OUT/app.log"; kill $APP 2>/dev/null; exit 2; }

# --- day-advance loop, per-press assertion (tPF-9 soak law).
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
  QUITLINES=$(grep -c "ui quit cause" "$OUT/app.log")
  if [ "$QUITLINES" != "0" ]; then
    echo "VERDICT: ALIVE but quit line present — instrument anomaly:"
    grep -nE "ui quit cause" "$OUT/app.log"
    kill $APP 2>/dev/null; exit 1
  fi
  echo "VERDICT: SOAK SURVIVED — $PASSES presses, app alive, ZERO quit lines"
  kill $APP 2>/dev/null
  RC=0
else
  echo "VERDICT: REPRODUCED — process exited at press $DIED_AT"
  for w in $(seq 3); do kill -0 $XV 2>/dev/null && sleep 1; done
  echo "--- instrument + exit lines ---"
  grep -nE "ui quit cause|VICTORY|ui ok|ui cont" "$OUT/app.log" | tail -12
  echo "--- tail 20 ---"
  tail -20 "$OUT/app.log"
  RC=1
fi
kill $XV 2>/dev/null
wait 2>/dev/null
echo "DONE rc=$RC out=$OUT"
exit $RC
