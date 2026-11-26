#!/usr/bin/env bash
# tPF-6 ITEM 12 MECHANISM TEST: does a MOTION FLOOD drive CPU above the
# planet-screen idle floor? Seed 5, Xvfb :99, kill BY PID.
set -u
cd /home/hrethric/projects/ascendancy
BIN=${BIN:-./rewrite/build/ascendancy}
OUT=${OUT:-/tmp/tpf6_flood}; rm -rf $OUT; mkdir -p $OUT
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99 2>/dev/null
Xvfb :99 -screen 0 640x480x24 >/dev/null 2>&1 & XV=$!
sleep 1; export DISPLAY=:99
"$BIN" --ui --campaign 1 --seed 5 >$OUT/app.log 2>&1 & APP=$!
sleep 3
X() { ./tools/xsend "Ascendancy" "$@" >/dev/null 2>&1; sleep 0.4; }
X 318 335; X 553 145; X 300 100
grep -q "ui status select" $OUT/app.log || { echo "FLOOD FAIL: nav"; kill $APP $XV; exit 1; }
sleep 1
sample() { # sample <label> <secs> <mode>
  local label=$1 secs=$2 mode=$3
  local t0=$(awk '{print $14+$15}' /proc/$APP/stat)
  local end=$((SECONDS+secs))
  while [ $SECONDS -lt $end ]; do
    case $mode in
      flood)    ./tools/xsend "Ascendancy" warp 40 130 >/dev/null 2>&1
                ./tools/xsend "Ascendancy" warp 140 300 >/dev/null 2>&1
                ./tools/xsend "Ascendancy" warp 60 460 >/dev/null 2>&1 ;;
      slow)     ./tools/xsend "Ascendancy" warp 48 154 >/dev/null 2>&1; sleep 0.9 ;;
      idle)     sleep 0.5 ;;
    esac
  done
  local t1=$(awk '{print $14+$15}' /proc/$APP/stat)
  python3 -c "print('CPU $label: %.1f%%' % (100.0*$((t1-t0))/100.0/${secs}))" | tee -a $OUT/cpu.txt
}
sample idle 5 idle
sample slow-hover 5 slow
sample flood-hover 5 flood
sample idle-after 5 idle
kill $APP $XV 2>/dev/null
echo FLOOD-DONE
