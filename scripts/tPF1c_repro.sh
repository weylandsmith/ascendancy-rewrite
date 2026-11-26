#!/usr/bin/env bash
# tPF-1c REPRO (steering 2026-11-26): the user's VERBATIM launch is
#   ./build/ascendancy --data <root> --ui
# (NO --campaign; turns stays 0, main.cpp:75-80). Console showed ONLY
# "ui ok: turn 20" => clean exit via the camp.over() leg (ui.cpp:1593).
# This script matches the USER's config, not fe0fb45's REPRO B:
#   seed 1 (NO --seed => default 1, main.cpp:50; fe0fb45 used seed 5),
#   Begin-built via the wheel DEFAULTS (density rank 0 -> 50 stars,
#   species word 5 -> owners 5, title.cpp:184 + menulaw window-init law),
#   a FACTORY ORDER PENDING before day-advancing (tPF-2b click law),
#   then NEXT TURN x45 past day 25. Liveness by pgrep -f (block-buffer law).
# If the app exits: dump the tail (VICTORY event line + ui ok turn) and the
# quit-path instrument lines. Exit codes: 0 = survived 45 presses (ALIVE),
# 1 = exited before press 45 (REPRODUCED), 2 = harness/nav failure.
set -u
cd "$(dirname "$0")/.."
BIN=${BIN:-./rewrite/build/ascendancy}
OUT=${OUT:-/tmp/tpf1c_repro}
DISP=${DISP:-:97}
PASSES=${PRESSES:-45}
rm -rf "$OUT"; mkdir -p "$OUT"
rm -f /tmp/.X97-lock /tmp/.X11-unix/X97 2>/dev/null
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
trap 'kill $XV 2>/dev/null; pkill -f "rewrite/build/ascendancy --data" 2>/dev/null; true' EXIT
sleep 1
export DISPLAY=$DISP
# USER'S EXACT FLAGS: --data <repo root> --ui  (no --campaign, no --seed)
"$BIN" --data "${DATA:-$PWD}" --ui >"$OUT/app.log" 2>&1 &
APP=$!
sleep 4
kill -0 $XV 2>/dev/null || { echo "HARNESS FAIL: Xvfb dead"; kill $APP 2>/dev/null; exit 2; }
kill -0 $APP 2>/dev/null || { echo "HARNESS FAIL: app died at boot"; cat "$OUT/app.log"; exit 2; }
X() { ./tools/xsend "Ascendancy" click "$@" 2>>"$OUT/xsend.log"; sleep 1; }
alive() { pgrep -f "build/ascendancy --data" >/dev/null 2>&1; }

# --- Begin path (tNGB4 law): neutral click, FRESHGAME, BEGIN, intro dismiss
X 320 60
X 318 295
X 566 422
sleep 2
X 320 450
sleep 1
grep -q "newgame live" "$OUT/app.log" || { echo "NAV FAIL: no newgame live line"; tail -5 "$OUT/app.log"; kill $APP 2>/dev/null; exit 2; }
grep -m1 "newgame live" "$OUT/app.log"

# --- FACTORY ORDER PENDING (tPF-2b law; SKIP_ORDER=1 for pre-tPF-2d era
# trees whose popup flow has no ids law — the camp.over() claim under test
# does not depend on the order landing).
if [ "${SKIP_ORDER:-0}" != 1 ]; then
X 553 145
X 300 100
grep -q "ui status select" "$OUT/app.log" || { echo "NAV FAIL: no status select"; kill $APP 2>/dev/null; exit 2; }
CB_LINE=$(grep 'ui planet home-cb' "$OUT/app.log" | tail -1)
PSIZE=$(echo "$CB_LINE" | sed -n 's/.*size \([0-9]\).*/\1/p')
[ -n "$PSIZE" ] || { echo "NAV FAIL: no size in home-cb line"; kill $APP 2>/dev/null; exit 2; }
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
    *"n=0 "*)   # armed cell has zero legal items: Escape pops to STATUS,
                # re-select row 0 re-enters the planet view with the list /
                # popup / pick state RESET (ui.cpp fresh-entry leg)
      ./tools/xsend "Ascendancy" key Escape 2>>"$OUT/xsend.log"; sleep 0.5
      X 300 100
      continue;;
  esac
  X 300 130          # PLANLIST row 0 (pitch 72, rect 120,120..520,420)
  sleep 0.5
  if grep -qE "ordered( armed cell| \()" "$OUT/app.log"; then BUILD_XY="$c1 $c2"; break; fi
done <<< "$CENTERS"
[ -n "$BUILD_XY" ] || { echo "NAV FAIL: no cell produced an order"; kill $APP 2>/dev/null; exit 2; }
grep -E "ordered( armed cell| \()" "$OUT/app.log" | tail -1
alive || { echo "ORDER PHASE DIED — see $OUT/app.log"; tail -10 "$OUT/app.log"; exit 1; }
# back to the map from the planet view before the advance loop
./tools/xsend "Ascendancy" key Escape 2>>"$OUT/xsend.log"; sleep 0.6
grep -q "ui screen Planets -> map" "$OUT/app.log" || { echo "NAV FAIL: not on map after order-phase escape"; tail -4 "$OUT/app.log"; kill $APP 2>/dev/null; exit 2; }
fi

# --- back to the MAP: planet view -> Planets -> map (stack escape x2), then
# day-advance past day 25. Each press MUST log a next-turn click.
if [ "${SKIP_ORDER:-0}" = 1 ]; then
  # no order phase ran: we are still on the map (Begin dismissed to map)
  :
fi
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
  echo "VERDICT: ALIVE after $PASSES presses (no camp.over() exit)"
  grep -c "ui click next-turn" "$OUT/app.log"
  kill $APP 2>/dev/null
  RC=0
else
  echo "VERDICT: REPRODUCED — process exited at press $DIED_AT"
  # Drain flush window: exit path prints 'ui ok: turn N' after the loop.
  for w in $(seq 3); do kill -0 $XV 2>/dev/null && sleep 1; done
  echo "--- VICTORY/exit lines ---"
  grep -nE "VICTORY|ui ok|ui cont|quit" "$OUT/app.log" | tail -12
  echo "--- tail 20 ---"
  tail -20 "$OUT/app.log"
  RC=1
fi
kill $XV 2>/dev/null
wait 2>/dev/null
echo "DONE rc=$RC out=$OUT"
exit $RC
