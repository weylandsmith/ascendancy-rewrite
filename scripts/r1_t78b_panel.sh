#!/usr/bin/env bash
# r1_t78b_panel.sh — step B of OQ-012(a): click GALAXY_MORE button
# (windows.txt NEWGAMEWND child, rect 7,381..122,472 -> center (64,426)),
# screenshot the resulting density panel for coordinate adjudication.
# Baseline law: T (hi-u16 DAT_00016143 via pointer law) == 50 from run A
# (r1size-20261012-033341). Exit: 0 completed with saves; 1 no saves.
set -u
cd "$(dirname "$0")/.."
ROOT=$(pwd)
DISP="${DISPNO:-92}"
OUT="$ROOT/work/r1/r1dens-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUT" || exit 2
SCRATCH="$ROOT/work/r1/game"
Xvfb ":$DISP" -screen 0 640x480x24 >"$OUT/xvfb.out" 2>&1 &
XV=$!
cleanup() { kill "$XV" 2>/dev/null; pkill -x dosbox-x 2>/dev/null; }
trap cleanup EXIT
sleep 1
CONF="$OUT/r1dens.conf"
cat > "$CONF" <<EOF
[dosbox]
machine=svga_s3
memsize=16
captures=$OUT/caps
autosave=10 41-60
saveremark=false
[sdl]
output=x11
fullscreen=false
autolock=false
[mixer]
nosound=true
[autoexec]
MOUNT C $SCRATCH
C:
ASCEND.EXE
EOF
TL=320
DISPLAY=":$DISP" timeout -s KILL $((TL + 20)) dosbox-x -conf "$CONF" -nogui \
  -time-limit "$TL" </dev/null >"$OUT/dosbox.out" 2>&1 &
DB=$!
shot() { DISPLAY=":$DISP" import -window root "$OUT/shot-$(printf %02d $1).png" 2>/dev/null; }
T0=$(date +%s); i=1
ST=""
while kill -0 "$DB" 2>/dev/null; do
  NOW=$(date +%s); REL=$((NOW - T0))
  if [ "$ST" = "" ] && [ "$REL" -ge 75 ]; then
    DISPLAY=":$DISP" "$ROOT/tools/xsend" "DOSBox-X" 318 293 >>"$OUT/click.log" 2>&1
    echo "newgame at t=$REL" >>"$OUT/click.log"; ST=setup; NEXT=$((REL + 25))
  fi
  if [ "$ST" = setup ] && [ "$REL" -ge "$NEXT" ]; then
    shot $i; i=$((i+1))
    DISPLAY=":$DISP" "$ROOT/tools/xsend" "DOSBox-X" 64 426 >>"$OUT/click.log" 2>&1
    echo "galaxy_more click at t=$REL" >>"$OUT/click.log"
    ST=panel; NEXT=$((REL + 8))
  fi
  if [ "$ST" = panel ] && [ "$REL" -ge "$NEXT" ] && [ "$REL" -le 200 ]; then
    shot $i; i=$((i+1))
    NEXT=$((REL + 200))   # one panel shot then hold
  fi
  sleep 4
done
head -c 65536 "$OUT/dosbox.out" > "$OUT/dosbox.out.trim" 2>/dev/null && mv "$OUT/dosbox.out.trim" "$OUT/dosbox.out"
echo "run=$OUT shots=$((i-1))"
[ "$i" -ge 3 ] && exit 0 || exit 1
