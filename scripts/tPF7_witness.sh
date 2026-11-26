#!/usr/bin/env bash
# tPF-7 HOLD-LAW WITNESS (D28 items 16/17/18; law docs/re/_wip_tPF7.md
# P1-P6; port arm researchview.h ResCam release + ui.cpp resHold leg).
# Proves THREE legs on the live port:
#  (a) HOLD: press-only press of RESROTRIGHT drives the tree (app re-logs
#      projected centres continuously), and the app FREEZES the moment
#      clickup lands (vendor release msg 0x47d3b == SDL_MOUSEBUTTONUP).
#  (b) NO-STICK: a plain click (press+release) on the same control leaves
#      the camera still afterwards (the pre-fix build rotated forever).
#  (c) CADENCE: >= 10 centre re-logs inside a 2 s hold — the old 1000 ms
#      pump could produce at most ~2; the shipped 34 ms loop produces ~29/s.
# Scratch Xvfb, kill BY PID. Click points are the windows.txt rects
# (RESROTRIGHT 540,442-554,472 -> centre 547,457), not eyeballed.
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/tpf7_shots}
DISP=${DISP:-:99}
rm -rf "$OUT"; mkdir -p "$OUT"
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP SDL_AUDIODRIVER=dummy "$BIN" --ui --campaign 1 --seed 5 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 3
X() { DISPLAY=$DISP ./tools/xsend "Ascendancy" "$@"; sleep 0.15; }
shot() { sleep 0.3; DISPLAY=$DISP import -window root -crop 640x480+0+0 +repage "$OUT/$1.png" 2>>"$OUT/app.log"; }
cnt() { grep -c "ui research center " "$OUT/app.log"; }

X 318 335            # RESUME -> campaign map
X 553 223            # RESEARCH rail -> state 20
sleep 1

# --- (c)+(a) HOLD LEG ------------------------------------------------------
B0=$(cnt)
X clickdn 547 457    # press-only on RESROTRIGHT (rot pair latches)
T0=$(date +%s%N)
sleep 2
B1=$(cnt)
X clickup 547 457    # release-only: vendor 0x47d3b clears the rot pair
sleep 0.2
shot held            # mid-state check: app alive with tree rotated
sleep 2
B2=$(cnt)
T_MS=$(( ($(date +%s%N) - T0) / 1000000 ))

# --- (b) NO-STICK LEG ------------------------------------------------------
X 547 457            # plain click (press+release) on the same control.
# NOTE: the ~65 ms press->release gap legitimately advances 1-2 pump ticks
# (the vendor behaves the same: its release is a SCHEDULED msg 0x38, not
# instantaneous). The anti-sticky property is about what happens AFTER the
# release — so the measurement window starts once the click has settled.
sleep 1
C0=$(cnt)
sleep 3
C1=$(cnt)
shot afterclick

kill $APP 2>/dev/null; kill $XV 2>/dev/null
wait $APP 2>/dev/null; wait $XV 2>/dev/null

pass=1
echo "hold window: ${T_MS} ms; centre re-logs during hold: $((B1-B0)); after release (+2s): $((B2-B1))"
echo "click leg: re-logs within 3 s after a plain click: $((C1-C0))"
grep -E "ui research latch" "$OUT/app.log" | head -8

[ $((B1 - B0)) -ge 10 ] \
  && echo "PASS (c) cadence: $((B1-B0)) centre changes in ${T_MS} ms (old 1000ms pump <= 2)" \
  || { echo "FAIL (c) cadence: only $((B1-B0)) changes"; pass=0; }
[ $((B2 - B1)) -le 1 ] \
  && echo "PASS (a) release freezes: $((B2-B1)) changes after clickup (tolerance 1: in-flight poll)" \
  || { echo "FAIL (a) still moving after release: $((B2-B1)) changes"; pass=0; }
[ $((C1 - C0)) -le 1 ] \
  && echo "PASS (b) no sticky latch after a plain click" \
  || { echo "FAIL (b) camera kept moving after click: $((C1-C0)) changes"; pass=0; }
grep -q "ui research latch 0 0" "$OUT/app.log" \
  && echo "PASS latch-zero logged (press law + release law both fired)" \
  || { echo "FAIL no latch-zero line"; pass=0; }
[ $pass = 1 ] && echo VERDICT PASS || echo VERDICT FAIL
exit $((1-pass))
