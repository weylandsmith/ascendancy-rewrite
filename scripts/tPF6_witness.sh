#!/usr/bin/env bash
# tPF-6 witness: D28 item 11 (orbital click -> popup/build menu) + item 12
# (hover CPU). OUR port, seed 5, scratch Xvfb :99 (kill BY PID, never :9).
#
# Arm 1 (click): click orbital slot 0 centre (48,154) [origin (13,119) pitch
#   70, hit law x[14,152] y[120,468]]; expect log 'ui planet tile <surf>
#   selected (Orbital Square...' with ids=; then click the Build button
#   (left half of band y337..367, x>=160) -> PLANLIST armed; pick a row ->
#   order or reject line. Slot 4 (col0 row4 centre (48,434)) as second cell.
# Arm 2 (CPU): sample /proc/PID/stat utime+stime over 5s windows:
#   idle (pointer parked at 600,250 outside the field), orbital-hover (rapid
#   warps inside x14..152 y120..468), lattice-hover (rapid warps x300..450
#   y200..350). The mechanism claim under test: full repaint per motion
#   event, no coalescing -> hover CPU >> idle CPU.
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/tpf6_shots}
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
kill -0 $XV 2>/dev/null || { echo "WITNESS FAIL: Xvfb dead"; kill $APP 2>/dev/null; exit 1; }
need() {
  local n=0
  while [ $n -lt 8 ]; do
    grep -q "$1" "$OUT/app.log" 2>/dev/null && return 0
    sleep 0.5; n=$((n+1))
  done
  echo "WITNESS FAIL: no '$1' ($2)" >> "$OUT/app.log"; return 1
}
X() { ./tools/xsend "Ascendancy" "$@"; sleep 0.4; }
shot() {  # tPL-V1f law: root grab cropped to the window geom, assert 640x480
  local g; g=$(./tools/winpos "Ascendancy") || { echo "winpos FAIL $1" >>"$OUT/app.log"; return 1; }
  local X=${g%% *} rest=${g#* }; local Y=${rest%% *} rest2=${rest#* }; local W=${rest2%% *}
  [ "$W" = 640 ] || { echo "shot FAIL $1 geometry $g" >>"$OUT/app.log"; return 1; }
  timeout 15 import -window root -crop "${W}x480+${X}+${Y}" +repage "$OUT/$1.png" 2>>"$OUT/app.log"
}
cpu() { # cpu <label> <seconds> <hover-mode: idle|orbital|lattice>
  local label=$1 secs=$2 mode=$3
  local t0=$(awk '{print $14+$15}' /proc/$APP/stat)
  local w0=$(awk '{print $22}' /proc/$APP/stat)   # starttime (ticks)
  local end=$((SECONDS+secs))
  while [ $SECONDS -lt $end ]; do
    case $mode in
      orbital) ./tools/xsend "Ascendancy" warp 40 130 >/dev/null 2>&1
               ./tools/xsend "Ascendancy" warp 140 300 >/dev/null 2>&1
               ./tools/xsend "Ascendancy" warp 60 460 >/dev/null 2>&1 ;;
      lattice) ./tools/xsend "Ascendancy" warp 300 210 >/dev/null 2>&1
               ./tools/xsend "Ascendancy" warp 450 340 >/dev/null 2>&1
               ./tools/xsend "Ascendancy" warp 360 270 >/dev/null 2>&1 ;;
      idle)    sleep 0.5 ;;
    esac
    sleep 0.05
  done
  local t1=$(awk '{print $14+$15}' /proc/$APP/stat)
  local hz=$(getconf CLK_TCK)
  python3 -c "print('CPU $label: %.1f%% CPU over ${secs}s (ticks %d/%d hz=$hz)' % (100.0*$((t1-t0))/$hz/${secs}, $((t1-t0)), $hz))" >> "$OUT/cpu.txt"
}
# --- navigate: RESUME -> STATUS -> row 0 -> planet view
X 318 335
X 553 145
X 300 100
need "ui status select" "row click did not open planet view" || { kill $APP $XV 2>/dev/null; echo VERDICT FAIL; exit 1; }
sleep 1

# --- ARM 2 first (before state mutates): CPU windows
: > "$OUT/cpu.txt"
cpu idle 5 idle
cpu orbital-hover 5 orbital
cpu lattice-hover 5 lattice
cat "$OUT/cpu.txt"

# --- ARM 1: orbital slot 0 click
X warp 48 154
sleep 0.6
./tools/xsend "Ascendancy" click 48 154; sleep 0.8
grep -q "ui planet tile" "$OUT/app.log" || echo "ARM1 NOTE: no tile line for slot0 click" >> "$OUT/app.log"
grep -m2 "ui planet tile" "$OUT/app.log" | tail -1
shot slot0_popup
# Build button: band y337..367, first rect x160.. left half
grep -q "ids=54" "$OUT/app.log" && ./tools/xsend "Ascendancy" click 200 352 && sleep 0.8
need "ui planet popup build" "Build button did not open PLANLIST" || true
# pick row 0 of PLANLIST (list rect 120,120.. rows pitch 72 from y122)
./tools/xsend "Ascendancy" click 250 158; sleep 0.8
grep "ui planet project\|ui planet pick" "$OUT/app.log" | tail -2
shot after_order

# --- DIFFERENTIAL LEGS ---------------------------------------------------
# D1: PLBUILD open (NO armed cell) -> full REQUIRES list (n=8 on seed 5):
#     the filter must NOT leak into the plain path.
./tools/xsend "Ascendancy" click 547 57; sleep 0.8     # PLBUILD panel centre
grep "ui planlist opts" "$OUT/app.log" | tail -1
./tools/xsend "Ascendancy" click 547 57; sleep 0.8     # close again
# D2: ARMED SURFACE cell: click surface tiles until one arms Build
#     (ids=54,51 — tPF-2b centres (410,297)/(444,280) worked for size 2),
#     open the list from ITS Build button, and assert NO orbital items
#     (22/23/26) appear. Probe centres, checking the log after each.
for PT in "410 297" "444 280" "380 330" "470 310"; do
  ./tools/xsend "Ascendancy" click $PT; sleep 0.7
  LAST=$(grep "ui planet tile" "$OUT/app.log" | tail -1)
  case "$LAST" in *"ids=54,51"*) break;; esac
done
case "$LAST" in
  *"ids=54,51"*)
    ./tools/xsend "Ascendancy" click 200 352; sleep 0.8
    SURF_OPTS=$(grep "ui planlist opts" "$OUT/app.log" | tail -1 | sed 's/.*\[//')
    echo "D2 surface-armed: [$SURF_OPTS]"
    case "$SURF_OPTS" in
      *22,*|*23,*|*26,*) echo "D2 FAIL: orbital items in surface-armed list" ;;
      *) echo "D2 PASS: surface-armed list holds no orbital items" ;;
    esac >> "$OUT/app.log"
    ./tools/xsend "Ascendancy" click 200 352 2>/dev/null; sleep 0.4  # cancel/ok
    ;;
  *) echo "D2 SKIPPED: no build-eligible surface tile found ($LAST)" >> "$OUT/app.log" ;;
esac
grep -c "ui planlist opts" "$OUT/app.log"
echo "DIFF-NOTES: opts-line count above; D1 last opts before D2 should be n=8 (unarmed)"

kill $APP $XV 2>/dev/null
echo "---- app log tail ----"
tail -25 "$OUT/app.log"
echo VERDICT-DATA-COLLECTED
