#!/usr/bin/env bash
# t405 witness: SUB-SCREEN NAVIGATION + HIT-MAP. Xvfb, campaign seed 5,
# SDL_AUDIODRIVER=dummy + --audio-trace so a rail press leaves a "sfx button"
# marker line (t404 harness shape). Assertions are on the APP LOG:
#  1. STATUS rail opens the status screen.
#  2. (580,60) — inside the OLD 566-wide arrow rect — is now a ROW, not a
#     scroll: expect "ui status select", NOT "ui status scroll up".
#  3. (628,70) — inside the MEASURED up-arrow art box — scrolls (up).
#  4. (628,450) — measured down box — scrolls down.
#  5. (628,250) — scrollbar trough — INERT: no ui status line at all.
#  6. (553,145) — the rail's map position — hits NO rail button (no
#     "ui screen" switch line); lands on the list like the vendor.
#  7. Esc returns to the map.
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/t405_witness}
DISP=${DISP:-:97}
rm -rf "$OUT"; mkdir -p "$OUT"
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP SDL_AUDIODRIVER=dummy "$BIN" --ui --campaign 1 --seed 5 --audio-trace >"$OUT/app.log" 2>&1 &
APP=$!
sleep 3
shot() { DISPLAY=$DISP import -window root "$OUT/$1.png" 2>>"$OUT/app.log"; }
X() { DISPLAY=$DISP ./tools/xsend "Ascendancy" "$@"; sleep 1; }
K() { DISPLAY=$DISP ./tools/xkey "Ascendancy" "$1" 2>/dev/null || xdotool --display $DISP key "$1"; sleep 1; }

X 318 335            # RESUME -> campaign map
X 553 145            # STATUS rail button -> status screen
shot status-open
X 580 60             # old-arrow zone -> must be ROW select, not scroll
X 628 70             # measured up-arrow box -> scroll up
X 628 450            # measured down box -> scroll down
X 628 250            # trough -> inert
X 553 145            # rail map-position inside the screen -> no switch
shot status-after
X key Escape         # back to the map (xsend key syntax, t404 precedent)
shot back-to-map
kill $APP 2>/dev/null; kill $XV 2>/dev/null

L="$OUT/app.log"
pass=1
chk() { # desc, grep -E pattern, expected count
  n=$(grep -cE "$2" "$L")
  if [ "$n" -ge "${3:-1}" ]; then echo "PASS  $1 ($n)"; else echo "FAIL  $1 (got $n, want >=${3:-1})"; pass=0; fi
}
chkzero() { n=$(grep -cE "$2" "$L"); if [ "$n" -eq 0 ]; then echo "PASS  $1 (0)"; else echo "FAIL  $1 (got $n, want 0)"; pass=0; fi; }
chk  "rail opened status"            'ui screen map -> Planets \(STATUS\)' 1
chk  "old-arrow zone is a ROW"       'ui status select' 1
chk  "measured up box scrolls"       'ui status scroll up' 1
chk  "measured down box scrolls"     'ui status scroll down' 1
chk  "Esc returned to map"           'esc' 1
chkzero "rail-position clicks never switch screens" 'ui screen Planets -> (Ships|Research|Species|Intelligence)' 0
chkzero "no laser01 anywhere"         'laser01' 0
# trough at (628,250) is INERT: exactly the four expected status lines
# (select, up, down, select-from-rail-position) — no fifth line.
n_status=$(grep -cE 'ui status ' "$L")
[ "$n_status" -eq 4 ] && echo "PASS  trough inert (4 status lines)" || { echo "FAIL  trough inert (got $n_status, want 4)"; pass=0; }
# ordering: the FIRST status line after opening must be a select (the old
# code's first click at (580,60) scrolled up instead).
first=$(grep -E 'ui status (select|scroll)' "$L" | head -1)
case "$first" in *"ui status select"*) echo "PASS  first click = select ($first)";; *) echo "FAIL  first click = '$first'"; pass=0;; esac
[ $pass -eq 1 ] && echo "VERDICT PASS" || echo "VERDICT FAIL"
echo DONE
