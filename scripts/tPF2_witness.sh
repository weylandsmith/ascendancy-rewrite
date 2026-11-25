#!/usr/bin/env bash
# tPF-2 port witness: the SQUARE-INFO POPUP chain on OUR port (D28 P3/P5).
# Boot seed 5 -> RESUME -> STATUS -> row 0 (planet view); then:
#  1. click tiles until the log shows a BUILD-eligible cell (adjacent) and
#     an OK-only cell (non-adjacent) — "ui planet tile N selected (...)"
#  2. on the BUILD popup click the bar's left half -> PLANLIST opens with
#     the cell armed -> click row 0 -> log "ordered armed cell N"
#  3. on the OK popup click OK -> popup dismissed
# Xvfb hygiene (tPL-V1f/g laws): export DISPLAY inside, clear stale locks,
# kill BY PID ONLY, never touch :9.
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/tpf2_shots}
DISP=${DISP:-:99}
rm -rf "$OUT"; mkdir -p "$OUT"
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99 2>/dev/null
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
export DISPLAY=$DISP
"$BIN" --ui --campaign 1 --seed 5 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 3
shot() {
  local g; g=$(./tools/winpos "Ascendancy") || { echo "winpos FAIL $1" >>"$OUT/app.log"; return 1; }
  local X=${g%% *} rest=${g#* }; local Y=${rest%% *} rest2=${rest#* }; local W=${rest2%% *} rest3=${rest2#* }; local H=${rest3%% *}
  [ "$W" = 640 ] && [ "$H" = 480 ] || { echo "shot FAIL $1 geometry $g" >>"$OUT/app.log"; return 1; }
  timeout 15 import -window root -crop "${W}x${H}+${X}+${Y}" +repage "$OUT/$1.png" 2>>"$OUT/app.log"
}
X() { ./tools/xsend "Ascendancy" "$@"; sleep 0.4; }
X 318 335            # RESUME -> campaign map
X 553 145            # STATUS rail -> planets list
sleep 1
X 300 100            # ROW 0 band -> planet view
sleep 1

# --- find a BUILD cell and an OK cell by probing lattice tile centres ----
# tileCenter (tPL-V1 law): (410 + 34*(col-row), 127 + 17*(col+row)).
BUILD_XY=""; OK_XY=""
for d in "0 0" "1 0" "-1 0" "0 1" "0 -1" "2 0" "-2 0" "0 2" "0 -2" "3 0" "-3 0" "4 0" "-4 0" "5 0" "-5 0"; do
  row=${d% *}; col=${d#* }
  tx=$((410 + 34*(col-row))); ty=$((127 + 17*(col+row)))
  [ $tx -lt 0 ] && continue; [ $tx -gt 639 ] && continue
  [ $ty -lt 120 ] && continue; [ $ty -gt 375 ] && continue
  before=$(grep -c 'ui planet tile' "$OUT/app.log" 2>/dev/null || echo 0)
  X $tx $ty
  sleep 0.3
  line=$(grep 'ui planet tile' "$OUT/app.log" | tail -1)
  case "$line" in
    *"BUILD)"*) [ -z "$BUILD_XY" ] && BUILD_XY="$tx $ty";;
    *" OK)"*)   [ -z "$OK_XY" ] && OK_XY="$tx $ty";;
  esac
  [ -n "$BUILD_XY" ] && [ -n "$OK_XY" ] && break
done
echo "WITNESS BUILD_XY='$BUILD_XY' OK_XY='$OK_XY'" >> "$OUT/app.log"

# --- path A: BUILD popup -> Build -> list pick -> armed-cell order -------
if [ -n "$BUILD_XY" ]; then
  set -- $BUILD_XY
  X $1 $2            # re-open the BUILD popup (previous click may dismiss)
  sleep 0.3
  shot popup-build
  # bar y = 339..367; Build label x ~ 227 (left quarter of 162..477)
  X 227 353
  sleep 0.5
  shot list-open
  X 300 130          # PLANLIST row 0 (rect 120,120..520,420, row pitch 24)
  sleep 0.5
  shot after-pick
fi

# --- path B: OK popup -> dismiss ------------------------------------------
if [ -n "$OK_XY" ]; then
  set -- $OK_XY
  X $1 $2
  sleep 0.3
  shot popup-ok
  X 312 353          # OK (centre of the bar)
  sleep 0.4
  shot after-ok
fi

grep -E 'ui planet (tile|popup|project)' "$OUT/app.log" | tail -30
kill $APP 2>/dev/null; kill $XV 2>/dev/null   # PID-only kill law
echo DONE
