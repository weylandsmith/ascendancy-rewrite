#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

# r1_t78c_cycle.sh — OQ-012(a) decisive leg: click GALAXY_MORE N times on
# the setup screen (rect center (64,426), windows.txt NEWGAMEWND law),
# ENTER campaign ((600,440) r1deep law), measure T=hi-u16 DAT_00016143
# offline per pointer law. Baselines: N=0 -> T=50 (r1size-20261012-033341);
# N=1 preview label = "Dense Star Cluster" (r1dens-20261012-034418 shot-02,
# vision-transcribed). Screenshot after each cycle step banks the label.
# SAFETY: scratch only, /dev/null stdin, -time-limit, pkill -x, capped out.
# Env: NCLICKS(1) DISPNO(94)
set -u
cd "$(dirname "$0")/.."
ROOT=$(pwd)
N="${NCLICKS:-1}"
DISP="${DISPNO:-94}"
OUT="$ROOT/work/r1/r1size-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUT" || exit 2
SCRATCH="$ROOT/work/r1/game"
Xvfb ":$DISP" -screen 0 640x480x24 >"$OUT/xvfb.out" 2>&1 &
XV=$!
cleanup() { kill "$XV" 2>/dev/null; pkill -x dosbox-x 2>/dev/null; }
trap cleanup EXIT
sleep 1
CONF="$OUT/r1size.conf"
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
TL=$((220 + N * 20))
DISPLAY=":$DISP" timeout -s KILL $((TL + 20)) dosbox-x -conf "$CONF" -nogui \
  -time-limit "$TL" </dev/null >"$OUT/dosbox.out" 2>&1 &
DB=$!
shot() { DISPLAY=":$DISP" import -window root "$OUT/shot-$(printf %02d $1).png" 2>/dev/null; }
T0=$(date +%s); i=1; ST=""; DONE=0; NEXT=75
while kill -0 "$DB" 2>/dev/null; do
  NOW=$(date +%s); REL=$((NOW - T0))
  if [ "$ST" = "" ] && [ "$REL" -ge "$NEXT" ]; then
    DISPLAY=":$DISP" "$ROOT/tools/xsend" "DOSBox-X" 318 293 >>"$OUT/click.log" 2>&1
    echo "newgame at t=$REL" >>"$OUT/click.log"
    ST=setup; NEXT=$((REL + 25))
  fi
  if [ "$ST" = setup ] && [ "$REL" -ge "$NEXT" ] && [ "$N" -gt 0 ]; then
    DISPLAY=":$DISP" "$ROOT/tools/xsend" "DOSBox-X" 64 426 >>"$OUT/click.log" 2>&1
    N=$((N-1)); echo "galaxy_more click, left=$N at t=$REL" >>"$OUT/click.log"
    if [ "$N" -eq 0 ]; then ST=cycled; NEXT=$((REL + 10))
    else NEXT=$((REL + 15)); fi
    sleep 3; shot $i; i=$((i+1))
  fi
  if [ "$ST" = cycled ] && [ "$DONE" -eq 0 ] && [ "$REL" -ge "$NEXT" ]; then
    shot $i; i=$((i+1))
    DISPLAY=":$DISP" "$ROOT/tools/xsend" "DOSBox-X" 600 440 >>"$OUT/click.log" 2>&1
    echo "ok/enter at t=$REL" >>"$OUT/click.log"
    DONE=1; sleep 25; shot $i; i=$((i+1))
  fi
  sleep 4
done
head -c 65536 "$OUT/dosbox.out" > "$OUT/dosbox.out.trim" 2>/dev/null && mv "$OUT/dosbox.out.trim" "$OUT/dosbox.out"
echo "run=$OUT slots=$(ls "$OUT/save" 2>/dev/null | wc -l)"
[ "$(ls "$OUT/save" 2>/dev/null | wc -l)" -ge 1 ] && exit 0 || exit 1
