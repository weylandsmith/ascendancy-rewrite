#!/usr/bin/env bash
# tPF-10 HOVER/SELECT WITNESS (D28 items 19/20). Legs (docs/re/_wip_tPF10.md):
#   (1) research screen at rest: hover log EMPTY (-1 never logged before
#       motion over a disk);
#   (2) WARP onto the first-available node centre (from the app's OWN
#       "ui research center" line) -> "ui research hover <row>" appears and
#       the ring box shows a STRONG BLUE increase (frame k2, port decode
#       mean (76,157,198)) vs the idle frame;
#   (3) WARP off any disk -> "ui research hover -1" (0xffff leg 0x47484);
#   (4) CLICK the node -> study line (commit reads the hover word);
#   (5) Escape out and back in -> re-entry clears the word (window-init
#       0x476f2): the first motion over the disk re-acquires hover, and the
#       studied ring (frame 0 WARM) is a DIFFERENT render than idle-pre-
#       study (persistence = studied row, not the click latch).
# Scratch Xvfb :99, kill BY PID (host law). Build BOTH run_tests AND
# ascendancy first (tPF-3e trap). Census boxes start x>=16 (tPF-9 border).
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/tpf10_shots}
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
W() { DISPLAY=$DISP ./tools/xsend "Ascendancy" warp "$1" "$2"; sleep 1; }
shot() { sleep 0.3; DISPLAY=$DISP import -window root -crop 640x480+0+0 +repage "$OUT/$1.png" 2>>"$OUT/app.log"; }

X 318 335            # RESUME -> campaign map
X 553 223            # RESEARCH rail -> state 20
sleep 1
# The app's own centre line for the first available row (tPF-8 rest law).
CENTER=$(grep -m1 "ui research center" "$OUT/app.log")
echo "CENTER LINE: $CENTER"
CX=$(echo "$CENTER" | awk "{print \$5}")
CY=$(echo "$CENTER" | awk "{print \$6}")
[ -n "$CX" ] && [ -n "$CY" ] || { echo "NO CENTRE LINE"; kill $APP $XV 2>/dev/null; exit 1; }
shot research_idle
W "$CX" "$CY"        # hover onto the disk
shot research_hover
W 300 100            # warp off any disk (upper empty field)
shot research_off
X clickdn "$CX" "$CY"; X clickup "$CX" "$CY"   # commit (study)
sleep 1
shot research_studied
X key Escape         # leave research
X 553 223            # re-enter research
sleep 1
W "$CX" "$CY"        # re-acquire hover after re-entry
shot research_reentry
kill $APP 2>/dev/null; kill $XV 2>/dev/null
wait $APP 2>/dev/null; wait $XV 2>/dev/null

echo "--- hover log lines ---"
grep -n "ui research hover" "$OUT/app.log" | head -12
grep -n "ui research study" "$OUT/app.log" | head -3

"$PY" scripts/tPF10_hover_census.py "$OUT" "$CX" "$CY" | tee "$OUT/census.out"
grep -q "VERDICT PASS" "$OUT/census.out" && echo "VERDICT PASS" || { echo "VERDICT FAIL"; exit 1; }
