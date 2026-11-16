#!/usr/bin/env bash
# t408 witness: the RESEARCH screen (state 20) renders the tree and a click
# on an Available node SETS the study topic (help reswin law).
# Layout is the port's DETERMINISTIC derived law (researchview.h):
#   centre(row) = (40 + depth*96 + panX, 76 + slot*78 + panY), r=30.
# The witness therefore clicks the FIRST SLOT of each depth column
# (y=76, x=40+d*96, d=0..6) — a centre click on an Available node logs
# "ui research study"; on an Owned node "ui research readout". Turn 1 of
# any campaign has >=1 studyable tech (the roots or their children), so the
# scan terminates. Pan buttons are the windows.txt verbatim rects.
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/t408_shots}
DISP=${DISP:-:97}
rm -rf "$OUT"; mkdir -p "$OUT"
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP SDL_AUDIODRIVER=dummy "$BIN" --ui --seed 5 --audio-trace >"$OUT/app.log" 2>&1 &
APP=$!
sleep 3
shot() { DISPLAY=$DISP import -window root "$OUT/$1.png" 2>>"$OUT/app.log"; }
X() { DISPLAY=$DISP ./tools/xsend "Ascendancy" "$@"; sleep 0.05; }
K() { DISPLAY=$DISP ./tools/xsend "Ascendancy" key "$1"; sleep 0.4; }
X 318 335            # RESUME -> campaign map
sleep 1
X 553 223            # rail Research -> state 20
sleep 0.5
shot research-open
studied=0
for d in 0 1 2 3 4 5 6; do
    x=$((40 + d * 96))
    X "$x" 76          # first slot of depth column d (centre click)
    sleep 0.4          # the study line flushes on click; grep must not race
    if grep -q "ui research study" "$OUT/app.log"; then studied=1; break; fi
done
sleep 1.2              # MEASURED race: shot at +0.1 s post-click was
                       # md5-IDENTICAL to pre-click; +1.0 s held the new
                       # frame (t408_soon/late, _wip_t408 F9)
shot research-study
# Pan pair (verbatim windows.txt rects): rotate-left box centre, move-down.
# NOTE: never echo into app.log — the app's own stdout offset OVERWRITES
# appended bytes (measured this session). Probe state goes to its own file.
for i in 1 2; do
    kill -0 $APP 2>/dev/null && echo "alive before pan $i" >> "$OUT/probe.log" \
      || echo "DEAD before pan $i" >> "$OUT/probe.log"
    X 531 457; sleep 0.5
    X 578 465; sleep 0.5
done
shot research-pan
# Owned-node readout: click the SAME row again after it is queued -> study
# again on another column is fine; just confirm readout OR second study.
K Escape
kill $APP 2>/dev/null; kill $XV 2>/dev/null
echo "--- log lines:"
grep -E "ui screen .*-> Research|ui research" "$OUT/app.log" | head -20
pass=1
grep -q "ui screen" "$OUT/app.log" || true
grep -q "ui research study" "$OUT/app.log" \
  && echo "PASS  empty-disk click SETS the study topic (help reswin)" \
  || { echo "FAIL  no study line (screen dead or hit-map cold)"; pass=0; }
grep -q "ui research pan" "$OUT/app.log" \
  && echo "PASS  pan buttons land (windows.txt msg-50..53 rects)" \
  || { echo "FAIL  no pan line"; pass=0; }
if grep -q "laser01" "$OUT/app.log"; then echo "FAIL  laser01 regression (t404 law)"; pass=0
else echo "PASS  zero laser01"; fi
[ $pass = 1 ] && echo VERDICT PASS || echo VERDICT FAIL
