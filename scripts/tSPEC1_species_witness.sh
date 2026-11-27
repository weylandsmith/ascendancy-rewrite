#!/usr/bin/env bash
# tSPEC-1 WITNESS (D33-L2): the Begin-path species pick reaches PLAY.
# Run A: FRESHGAME -> BEGIN with NO racelist click  -> vendor default row 0
#        (Minions: home 73 cells, terrain row 5 — window-init 0x52c8c).
# Run B: FRESHGAME -> scroll RACELIST to offset 18 -> click slot 1 (specnum
#        19 Chamachies) -> BEGIN -> home 45 cells, terrain row 7 (tPL-D1
#        T1[19]=3 -> 45; T2[19]=7).
# PASS = both runs alive AND the 'newgame live ... species' lines read 0 vs
# 19 AND the 'newgame home' lines differ (73/5 vs 45/7). Pre-fix BOTH runs
# printed species -1 with identical rng homes (the user's complaint).
# Exit: 0 PASS, 1 DEFECT, 2 harness/nav.
set -u
cd "$(dirname "$0")/.."
BIN=${BIN:-./rewrite/build/ascendancy}
OUT=${OUT:-/tmp/tspec1_witness}
DISP=${DISP:-:97}
rm -rf "$OUT"; mkdir -p "$OUT"
rm -f /tmp/.X97-lock /tmp/.X11-unix/X97 2>/dev/null
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
cleanup() { kill $XV 2>/dev/null; pkill -f "rewrite/build/ascendancy --data" 2>/dev/null; true; }
trap cleanup EXIT
sleep 1
export DISPLAY=$DISP
X() { ./tools/xsend "Ascendancy" click "$@" 2>>"$OUT/xsend.log"; sleep 1; }
alive() { pgrep -f "build/ascendancy --data" >/dev/null 2>&1; }

one_run() { # $1 = tag, $2 = "click" | "noclick"
  local tag=$1 mode=$2 log="$OUT/$2.log"
  "$BIN" --data "$PWD" --ui >"$log" 2>&1 &
  local APP=$!
  sleep 4
  kill -0 $APP 2>/dev/null || { echo "HARNESS FAIL ($tag): app died at boot"; exit 2; }
  X 320 60          # dismiss title prompt
  X 318 295         # FRESHGAME -> New Game wheel
  grep -q "newgame summary\|raceconfig" "$log" || { echo "NAV FAIL ($tag): no newgame screen"; tail -5 "$log"; kill $APP 2>/dev/null; exit 2; }
  if [ "$mode" = click ]; then
    # RACELIST down arrow kRaceArrowDown {616,356,631,371}: center 623,363.
    # maxOff = 21-3 = 18 -> 18 presses (per-press assert, tPF-9 law).
    for i in $(seq 1 18); do
      X 623 363
      grep -q "arrow down offset $i$" "$log" || { echo "NAV FAIL ($tag): arrow press $i unlogged"; kill $APP 2>/dev/null; exit 2; }
    done
    # Row slots (menulaw.cpp newgameRowAt): slot i spans
    # [kRaceSlotTop + i*kRaceSlotPitch, +107] = slot1 y 157..264. At scroll
    # offset 18, slot 1 = specnum 19. x inside kRaceList {502..632}, left of
    # the arrows: 560.
    X 560 200
    grep -q "select specnum 19" "$log" || { echo "NAV FAIL ($tag): slot click did not select specnum 19"; grep "select specnum" "$log" | tail -3; kill $APP 2>/dev/null; exit 2; }
  fi
  X 566 422         # BEGIN
  sleep 2
  X 320 450         # intro dismiss -> map (tXT1 order: dismiss BEFORE the
                    # grep — 'newgame live' prints only after runTitleScreen
                    # returns, i.e. after the intro)
  sleep 1
  grep -q "newgame live" "$log" || { echo "NAV FAIL ($tag): no newgame live line"; tail -5 "$log"; kill $APP 2>/dev/null; exit 2; }
  grep -m1 "newgame live" "$log"
  grep -m1 "newgame home" "$log"
  alive || { echo "DEFECT ($tag): app dead after intro"; exit 1; }
  kill $APP 2>/dev/null; wait $APP 2>/dev/null; true
}

one_run A noclick
one_run B click

LA=$(grep -m1 "newgame live" "$OUT/noclick.log")
LB=$(grep -m1 "newgame live" "$OUT/click.log")
HA=$(grep -m1 "newgame home" "$OUT/noclick.log")
HB=$(grep -m1 "newgame home" "$OUT/click.log")
echo "A: $LA | $HA"
echo "B: $LB | $HB"
rc=0
case "$LA" in *"species 0"*) ;; *) echo "FAIL: A species != 0"; rc=1;; esac
case "$LB" in *"species 19"*) ;; *) echo "FAIL: B species != 19"; rc=1;; esac
case "$HA" in *"cells 73 row 5"*) ;; *) echo "FAIL: A home not Minions table (73/5)"; rc=1;; esac
case "$HB" in *"cells 45 row 7"*) ;; *) echo "FAIL: B home not Chamachies table (45/7)"; rc=1;; esac
[ "$HA" = "$HB" ] && { echo "FAIL: home lines identical (species dropped?)"; rc=1; }
[ "$rc" = 0 ] && echo "TSPEC1 WITNESS: PASS (two Begin runs, two species, two home types)"
exit $rc
