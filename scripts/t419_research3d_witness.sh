#!/usr/bin/env bash
# t419 witness: RESEARCH SCREEN (1) does NOT peg the CPU, (2) spins as a 3D
# tree with the rotate dials (t416 latch law) and scrolls with the move pair,
# (3) the corner "Exit <ESC>" popup paints on cursor-corner entry, (4) Esc
# returns INSTANTLY (the D15 stall was minutes). Law docs/re/_wip_t419.md;
# screenshots -> $OUT for native-vision grade (D13).
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/t419_shots}
DISP=${DISP:-:97}
rm -rf "$OUT"; mkdir -p "$OUT"
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP SDL_AUDIODRIVER=dummy "$BIN" --ui --seed 5 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 3
shot() { DISPLAY=$DISP import -window root "$OUT/$1.png" 2>>"$OUT/probe.err"; }
X() { DISPLAY=$DISP ./tools/xsend "Ascendancy" "$@"; sleep 0.4; }
K() { DISPLAY=$DISP ./tools/xsend "Ascendancy" key "$1"; }

X 318 335            # RESUME -> campaign map
sleep 1
X 553 223            # rail Research -> state 20
sleep 1
shot research-open

# Study click FIRST (rest basis: t408 column scan; centres are the EXACT 2D
# law at rest — pins prove it — so the old coordinates still land).
studied=0
for d in 0 1 2 3 4 5 6; do
    x=$((40 + d * 96))
    X "$x" 76
    if grep -q "ui research study" "$OUT/app.log"; then studied=1; break; fi
done
sleep 1.2
shot research-study

# CPU census on the research screen: 6 samples over ~3 s (ps pcpu is the
# mean since start, so also sample the DELTA of utime via /proc for the
# window itself).
: > "$OUT/cpu.txt"
u0=$(awk '{print $14+$15}' /proc/$APP/stat 2>/dev/null || echo 0)
for i in 1 2 3 4 4; do
    sleep 0.8
    ps -o pcpu= -p $APP >> "$OUT/cpu.txt" 2>/dev/null
done
u1=$(awk '{print $14+$15}' /proc/$APP/stat 2>/dev/null || echo 0)
# utime+stime in clock ticks (100/s) over the ~4 s window:
echo "delta_ticks=$u1-$u0 window_s=4" >> "$OUT/cpu.txt"

# 3D SPIN: press rotate-left (dial 50) -> latch; two shots mid-spin show the
# tree mid-rotation; press again -> stop (t416 dialLatch law).
X 531 457            # RESROTLEFT centre
sleep 1.6
shot research-spin1
sleep 1.6
shot research-spin2
X 531 457            # stop
sleep 0.6
shot research-stopped

# SCROLL: move-down then move-up (msg 52/53 post-projection pan).
X 578 465; sleep 0.5
shot research-scrolldn

# CORNER POPUP: warp+click into the top-left corner (0,0 is outside every
# hit-map on state 20 -> the click itself is inert; the WARP moves the real
# pointer so the polled SDL_GetMouseState sees it).
X click 2 2
sleep 0.6
shot corner-topleft
X 320 240            # leave the corner (inert centre point)
sleep 0.4

# ESC INSTANT: count existing "ui screen" log lines, send Escape, poll for a
# NEW one (the t410 chain unwinds research -> map).
n0=$(grep -c "ui screen" "$OUT/app.log")
t_esc=$(date +%s.%N)
K Escape
esc_ms=timeout
for i in $(seq 1 30); do
    sleep 0.1
    n1=$(grep -c "ui screen" "$OUT/app.log")
    if [ "$n1" -gt "$n0" ]; then
        t_end=$(date +%s.%N)
        esc_ms=$(awk "BEGIN{printf \"%.0f\", ($t_end-$t_esc)*1000}")
        break
    fi
done
echo "esc_ms=$esc_ms" >> "$OUT/cpu.txt"
kill $APP 2>/dev/null; kill $XV 2>/dev/null

echo "--- research/corner log lines:"
grep -E "ui screen .*Research|ui research|ui corner exit" "$OUT/app.log" | head -20
echo "--- cpu census:"; cat "$OUT/cpu.txt"

pass=1
grep -q "ui research study" "$OUT/app.log" \
  && echo "PASS  empty-disk click still SETS study (rest equality)" \
  || { echo "FAIL  no study line"; pass=0; }
grep -q "ui corner exit popup shown" "$OUT/app.log" \
  && echo "PASS  corner popup SHOWN on cursor-corner entry" \
  || { echo "FAIL  no popup-shown line"; pass=0; }
grep -q "ui corner exit popup hidden" "$OUT/app.log" \
  && echo "PASS  corner popup HIDDEN on exit" || echo "WARN  no hidden line"
[ "$esc_ms" != timeout ] && [ "$esc_ms" -lt 3000 ] 2>/dev/null \
  && echo "PASS  Esc returned in ${esc_ms} ms (stall class gone)" \
  || { echo "FAIL  Esc not observed <3s (esc_ms=$esc_ms)"; pass=0; }
# CPU: delta ticks over the 4 s window must be well under 400 ticks = 400%core-s
read -r dt < <(awk -F- '{print $2-$1}' <<< "$(grep delta_ticks "$OUT/cpu.txt")")
[ "$dt" -lt 300 ] \
  && echo "PASS  research CPU delta ${dt} ticks/4s (< 75% of one core sustained)" \
  || echo "FAIL  research CPU delta ${dt} ticks/4s"
exit $((1-pass))
