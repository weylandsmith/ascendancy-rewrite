#!/usr/bin/env bash
# tPF-8 REST-STATE WITNESS (D28 item 21). Law (docs/re/_wip_tPF8.md P1-P3):
# the vendor starts with ZERO known techs (mask 0x00, 72/72 boot saves), so
# at rest the research screen paints EXACTLY the three prereq-empty root
# disks (rows 0/2/6) — no lines, no other circles — and the roots are
# ON-FRAME at the rest camera (column k=0 -> screen y 240..381). Legs:
#   (1) the app's own centre log names a ROOT row (0/2/6) as the first
#       Available WITHOUT any dolly (the tRSB1 witness needed one pre-fix);
#   (2) pixel census: exactly three ring-sized comps, no strays
#       (scripts/tPF8_rest_census.py).
# The click-still-works leg stays with tRSB1_witness.sh (it re-derives its
# own click point; running two click flows here would double the budget).
# Scratch Xvfb :99, kill BY PID (host law).
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/tpf8_shots}
DISP=${DISP:-:99}
PY=${PY:-$HOME/tools/revenv/bin/python}
rm -rf "$OUT"; mkdir -p "$OUT"
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP SDL_AUDIODRIVER=dummy "$BIN" --ui --campaign 1 --seed 5 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 3
X() { DISPLAY=$DISP ./tools/xsend "Ascendancy" "$@"; sleep 1; }
shot() { sleep 0.3; DISPLAY=$DISP import -window root -crop 640x480+0+0 +repage "$OUT/$1.png" 2>>"$OUT/app.log"; }
X 318 335            # RESUME -> campaign map
X 553 223            # RESEARCH rail -> state 20
sleep 1
shot rest
kill $APP 2>/dev/null; kill $XV 2>/dev/null
wait $APP 2>/dev/null; wait $XV 2>/dev/null

FAIL=0
# Leg 1: first "available" centre line must name a ROOT row (0/2/6).
LINE=$(grep "ui research center " "$OUT/app.log" | grep available | head -1)
if [ -z "$LINE" ]; then echo "FAIL leg1: no available centre logged at rest"; FAIL=1; fi
read -r _ _ _ ROW CX CY _ <<< "$LINE"
echo "leg1 first-available row=$ROW at ($CX,$CY)"
case "$ROW" in 0|2|6) ;; *) echo "FAIL leg1: row $ROW is not a root (0/2/6)"; FAIL=1;; esac
# No dolly happened between entry and the log line: the FIRST line IS this
# one (count == 1 among center lines mentioning available OR offframe).
N=$(grep -c "ui research center " "$OUT/app.log")
echo "center-log lines total: $N"
# Leg 2: pixel census.
"$PY" scripts/tPF8_rest_census.py "$OUT/rest.png" "$CX" "$CY" | tee "$OUT/census.out"
grep -q "VERDICT PASS" "$OUT/census.out" || FAIL=1
if [ $FAIL -eq 0 ]; then echo "VERDICT PASS"; else echo "VERDICT FAIL"; fi
exit $FAIL
