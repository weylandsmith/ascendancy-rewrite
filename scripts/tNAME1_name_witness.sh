#!/usr/bin/env bash
# tNAME-1 WITNESS (D33-L3): two fresh Begin runs name DIFFERENT home stars,
# and an explicit --seed reproduces. Vendor law: fresh-run srand from the
# clock (FUN_00020fd4 0x213fc) feeds worldgen's one LCG stream; --seed is
# the record-seed override leg (0x21489 cmp -1). Pre-fix EVERY run printed
# the same seed 1 and the same home star (the user's "always Phoebe").
# PASS = A and B alive AND their 'newgame home' star bases DIFFER AND their
# seeds differ; C and C2 (both --seed 7) alive AND IDENTICAL home lines;
# every run keeps the tSPEC-1 home TYPE line (cells/row present).
# Exit: 0 PASS, 1 DEFECT, 2 harness/nav.
set -u
cd "$(dirname "$0")/.."
BIN=${BIN:-./rewrite/build/ascendancy}
OUT=${OUT:-/tmp/tname1_witness}
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

one_run() { # $1 = tag, $2 = extra args (quoted)
  local tag="$1"
  local extra="$2"
  local log="$OUT/$tag.log"
  # shellcheck disable=SC2086
  "$BIN" --data "$PWD" --ui $extra >"$log" 2>&1 &
  local APP=$!
  sleep 4
  kill -0 $APP 2>/dev/null || { echo "HARNESS FAIL ($tag): app died at boot"; cat "$log"; exit 2; }
  X 320 60          # dismiss title prompt
  X 318 295         # FRESHGAME -> New Game wheel
  grep -q "newgame summary\|raceconfig" "$log" || { echo "NAV FAIL ($tag): no newgame screen"; tail -5 "$log"; kill $APP 2>/dev/null; exit 2; }
  X 566 422         # BEGIN
  sleep 2
  X 320 450         # intro dismiss -> map (tXT1 order: dismiss BEFORE grep)
  sleep 1
  grep -q "newgame live" "$log" || { echo "NAV FAIL ($tag): no newgame live line"; tail -5 "$log"; kill $APP 2>/dev/null; exit 2; }
  grep -m1 "newgame live" "$log" > "$OUT/$tag.live"
  grep -m1 "newgame home" "$log" > "$OUT/$tag.home" || { echo "DEFECT ($tag): no home line"; kill $APP 2>/dev/null; exit 1; }
  pgrep -f "build/ascendancy --data" >/dev/null 2>&1 || { echo "DEFECT ($tag): app dead after intro"; exit 1; }
  kill $APP 2>/dev/null; wait $APP 2>/dev/null; true
  echo "$tag: $(cat "$OUT/$tag.live") | $(cat "$OUT/$tag.home")"
}

one_run A ""
one_run B ""
# Pool-collision guard: two random seeds can draw the SAME home base (1/100
# per pair). Re-run B once before calling it a defect (tPF honesty: the
# retry is logged, not hidden).
NA=$(cat "$OUT/A.home"); NA=${NA#newgame home }; NA=${NA%% *}
NB=$(cat "$OUT/B.home"); NB=${NB#newgame home }; NB=${NB%% *}
if [ "$NA" = "$NB" ]; then
  echo "NOTE: A and B collided on base '$NA' (1/100 draw); re-running B"
  one_run B2 ""
  mv "$OUT/B2.home" "$OUT/B.home"; mv "$OUT/B2.live" "$OUT/B.live"
fi
one_run C "--seed 7"
one_run C2 "--seed 7"

rc=0
LA=$(cat "$OUT/A.live"); LB=$(cat "$OUT/B.live")
HA=$(cat "$OUT/A.home"); HB=$(cat "$OUT/B.home")
HC=$(cat "$OUT/C.home"); HC2=$(cat "$OUT/C2.home")
LC=$(cat "$OUT/C.live")

# A vs B: fresh clock seeds -> different seed AND different home star base.
SA=${LA##*seed }; SB=${LB##*seed }
[ "$SA" != "$SB" ] || { echo "FAIL: A and B share seed $SA (clock draw missing?)"; rc=1; }
NA=${HA#newgame home }; NA=${NA%% *}
NB=${HB#newgame home }; NB=${NB%% *}
[ "$NA" != "$NB" ] || { echo "FAIL: A and B home star identical ($NA) — per-game variation missing"; rc=1; }
# C vs C2: explicit --seed 7 -> authority + determinism (identical homes).
case "$LC" in *"seed 8"*) ;; *) echo "FAIL: --seed 7 handoff seed != 8 (apply->seed not taken): $LC"; rc=1;; esac
[ "$HC" = "$HC2" ] || { echo "FAIL: --seed 7 runs differ ('$HC' vs '$HC2') — determinism broken"; rc=1; }
# tSPEC-1 marker intact: home line carries cells + row on every run.
for f in A B C C2; do
  grep -Eq "cells [0-9]+ row [0-9]+" "$OUT/$f.home" || { echo "FAIL ($f): home line lost cells/row"; rc=1; }
done
[ "$rc" = 0 ] && echo "TNAME1 WITNESS: PASS (fresh games vary, --seed reproduces, type law intact)"
exit $rc
