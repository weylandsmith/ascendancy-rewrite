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
# tPF-2b attempt-2: the app died "X connection broken" seconds into attempt-1
# right after the row click — the shape of the SCRIPT's process group being
# killed mid-run (session ended), not of a click bug. Guard: verify each
# navigation step landed before the next, and re-assert aliveness per probe.
need() {  # need <pattern> <desc>  — retry the last click path is NOT possible
            # generically; just fail loud so a dead X is not mistaken for a
            # click miss.
  local n=0
  while [ $n -lt 6 ]; do
    grep -q "$1" "$OUT/app.log" 2>/dev/null && return 0
    sleep 0.5; n=$((n+1))
  done
  echo "WITNESS FAIL: no '$1' ($2)" >> "$OUT/app.log"; return 1
}
kill -0 $XV 2>/dev/null || { echo "WITNESS FAIL: Xvfb dead at start" >>"$OUT/app.log"; exit 1; }
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
need "ui status select" "row click did not open planet view" || { kill $APP $XV 2>/dev/null; echo VERDICT FAIL; exit 1; }

# --- find a BUILD cell and an OK cell by probing lattice tile centres ----
# tPF-2b ROOT CAUSE (attempt-1 failure): the old probe walked (col-row)
# offsets around tileCenter(0,0)=(410,127). For size class 2 the vendor grid
# (planitem.txt B/C tokens; C[size2] rows 4..10 = 1 4 4 5 4 4 1) puts ALL
# valid cells in rows 4..10 — centres span y 212..382. Every old probe was
# ABOVE the lattice: tileHitFor returned -1 for all 15, zero 'ui planet
# tile' lines. Fix: parse the app's own "home-cb ... size S surf M" line and
# enumerate the REAL cell centres from the B/C tables, in cell order.
CB_LINE=$(grep 'ui planet home-cb' "$OUT/app.log" | tail -1)
PSIZE=$(echo "$CB_LINE" | sed -n 's/.*size \([0-9]\).*/\1/p')
[ -n "$PSIZE" ] || { echo "WITNESS FAIL: no size in home-cb line" >>"$OUT/app.log"; kill $APP $XV 2>/dev/null; exit 1; }
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
BUILD_XY=""; OK_XY=""
while read -r tx ty; do
  [ -n "$BUILD_XY" ] && [ -n "$OK_XY" ] && break
  X $tx $ty
  line=$(grep 'ui planet tile' "$OUT/app.log" | tail -1)
  # tPF-2d: the log carries the vendor id array (docs/re/_wip_tPF2d.md);
  # BUILD popup = ids contain 54, OK popup = ids=51 alone (the n==1
  # getter(30) label path).
  case "$line" in
    *"ids=54"*) [ -z "$BUILD_XY" ] && BUILD_XY="$tx $ty";;
    *"ids=51)"*) [ -z "$OK_XY" ] && OK_XY="$tx $ty";;
  esac
done <<< "$CENTERS"
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
  # tPF-2b: hover row 1 (warp-only, no click) so the TEAL band is in the
  # shot (refcap build-list shows the band on the cursor row).
  DISPLAY=$DISP ./tools/xsend Ascendancy warp 300 230 >/dev/null 2>&1
  sleep 0.4
  shot list-hover
  # tPF-2b SCROLL ARROW: down once (rows 1..4), shot, back up (rows 0..3).
  X 500 404
  shot list-scrolled
  X 500 141
  X 300 130          # PLANLIST row 0 (rect 120,120..520,420, row pitch 72)
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
