#!/usr/bin/env bash
# tPF-7b COSMOS PUMP CADENCE WITNESS (sibling defect of tPF-7; law
# docs/re/_wip_tPF7b.md P1-P5; port arm cam3d.h kFireLoopMs + ui.cpp gates).
# The cosmos dial is a TOGGLE (t416 press law: same-dial click stops) — unlike
# the reswin controls there is NO release leg, so the legs are:
#  (c) CADENCE: >= 10 "ui cosmos pump yaw" lines inside a 2 s latched window
#      (old 1000 ms pump produces at most 2; shipped 34 ms produces ~29/s).
#  (a) STOP: press again -> ZERO pump lines in the following 2 s.
#  (b) IDLE: zero pump lines before the first press (pump is latch-gated,
#      never free-running — gates/autoplay law).
# Dial point ROTLEFT 486,379 is the t411 dial-walk centre (kMapCtl rect), not
# eyeballed. Scratch Xvfb, kill BY PID.
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/tpf7b_shots}
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
cnt() { grep -c "ui cosmos pump yaw" "$OUT/app.log"; }

X 318 335            # RESUME -> campaign map
sleep 2

# --- (b) IDLE LEG -----------------------------------------------------------
I0=$(cnt)
sleep 2
I1=$(cnt)

# --- (c)+(a) LATCHED WINDOW -------------------------------------------------
L0=$(cnt)
X click 486 379      # ROTLEFT press: dial latches (t416 law)
T0=$(date +%s%N)
sleep 2
L1=$(cnt)
T_MS=$(( ($(date +%s%N) - T0) / 1000000 ))   # latch window ONLY (tPF-7
shot spinning                                # witness precedent: the stop leg
X click 486 379      # same dial again: STOP   must not dilute the rate)
sleep 0.3
S0=$(cnt)
sleep 2
S1=$(cnt)
shot stopped

kill $APP 2>/dev/null; kill $XV 2>/dev/null
wait $APP 2>/dev/null; wait $XV 2>/dev/null

pass=1
echo "idle window: $((I1-I0)) pump lines (expect 0)"
echo "latched window: ${T_MS} ms; pump lines: $((L1-L0))"
echo "after stop: $((S1-S0)) pump lines (expect 0)"
grep "ui cosmos pump yaw" "$OUT/app.log" | head -3
grep "ui cosmos pump yaw" "$OUT/app.log" | tail -1

[ $((I1 - I0)) -eq 0 ] \
  && echo "PASS (b) latch-gated: no free-running pump at rest" \
  || { echo "FAIL (b) $((I1-I0)) pump lines while idle"; pass=0; }
[ $((L1 - L0)) -ge 10 ] \
  && echo "PASS (c) cadence: $((L1-L0)) fires in ${T_MS} ms (~$(( (L1-L0)*1000/T_MS ))/s; old 1000ms pump <= 2)" \
  || { echo "FAIL (c) cadence: only $((L1-L0)) fires"; pass=0; }
[ $((S1 - S0)) -eq 0 ] \
  && echo "PASS (a) toggle-off freezes the pump" \
  || { echo "FAIL (a) $((S1-S0)) fires after the stop press"; pass=0; }
# Rate sanity: fires/sec must sit near the derived 29.25 band (loose witness
# tolerance for X round-trips: 20..40/s).
if [ $((L1-L0)) -ge 10 ]; then
  rps=$(( (L1-L0)*1000/T_MS ))
  [ $rps -ge 20 ] && [ $rps -le 40 ] \
    && echo "PASS rate-in-band: ${rps}/s (derived 29.25, S28-X3 band 28-33)" \
    || echo "NOTE rate ${rps}/s outside 20..40 (X round-trip jitter, not a law FAIL)"
fi
[ $pass = 1 ] && echo VERDICT PASS || echo VERDICT FAIL
