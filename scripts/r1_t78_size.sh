#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

# r1_t78_size.sh — OQ-012(a) new-game size options: screenshot the SETUP
# screen, cycle the density/size control with timed clicks, ENTER the
# campaign, measure star count from the final autosave offline.
# Menu law (verified t75): rows at x=318: New Game y=293 (r1ad corpus law;
# band 273-297), Return y=325, Load y=372. Setup control coords UNSEEN —
# this run banks shot files; the click loop clicks a small set of candidate
# coords per t78 doc note only AFTER vision adjudication of shot-02, so
# THIS rev only screenshots at timed intervals through setup and entry.
# SAFETY (docs/BLOCKED.md invariants): scratch scratch game dir only (game/
# never mounted), stdin /dev/null, -time-limit, pkill -x dosbox-x only,
# Xvfb tracked, outputs capped.
# Env: BOOT=210 DISPNO=93 CYCLE_FROM=95 CYCLE_TO=170 (click cadence 15s)
# Exit: 0 run completed with >=1 save; 1 failed boot.
set -u
cd "$(dirname "$0")/.."
ROOT=$(pwd)
BOOT="${BOOT:-210}"
DISP="${DISPNO:-93}"
CYCLE_FROM="${CYCLE_FROM:-95}"
CYCLE_TO="${CYCLE_TO:-170}"
OUT="$ROOT/work/r1/r1size-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUT" || exit 2
SCRATCH="$ROOT/work/r1/game"
command -v Xvfb >/dev/null || { echo "MISSING Xvfb"; exit 2; }
command -v dosbox-x >/dev/null || { echo "MISSING dosbox-x"; exit 2; }
[ -x "$ROOT/tools/xsend" ] || { echo "MISSING tools/xsend"; exit 2; }

pkill -x dosbox-x 2>/dev/null && sleep 1
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
TL=$((BOOT + 120))
DISPLAY=":$DISP" timeout -s KILL $((TL + 20)) dosbox-x -conf "$CONF" -nogui \
  -time-limit "$TL" </dev/null >"$OUT/dosbox.out" 2>&1 &
DB=$!
shot() { DISPLAY=":$DISP" import -window root "$OUT/shot-$(printf %02d $1).png" 2>/dev/null; }

# REL-only timer law (t75b lesson)
T0=$(date +%s); i=1
NEWCLICK=75; ENTERED=0
LAST_CYCLE=0
while kill -0 "$DB" 2>/dev/null; do
  NOW=$(date +%s); REL=$((NOW - T0))
  # New Game entry click (r1ad law (318,293))
  if [ "$REL" -ge "$NEWCLICK" ] && [ "$REL" -lt $((NEWCLICK + 10)) ]; then
    shot $i; i=$((i+1))
    DISPLAY=":$DISP" "$ROOT/tools/xsend" "DOSBox-X" 318 293 >>"$OUT/click.log" 2>&1
    echo "newgame click at t=$REL" >>"$OUT/click.log"
    NEWCLICK=999999
    sleep 6
    shot $i; i=$((i+1))   # setup screen after menu
  fi
  # SETUP screenshots through the cycle window (no clicks yet in rev A:
  # control coords come from vision adjudication; shots bracket the phase)
  if [ "$REL" -ge "$CYCLE_FROM" ] && [ "$REL" -le "$CYCLE_TO" ] && [ $((REL - LAST_CYCLE)) -ge 15 ]; then
    shot $i; i=$((i+1))
    LAST_CYCLE=$REL
  fi
  # ENTER campaign late (r1ad law (600,440) = OK/continue)
  if [ "$ENTERED" -eq 0 ] && [ "$REL" -ge "$CYCLE_TO" ]; then
    DISPLAY=":$DISP" "$ROOT/tools/xsend" "DOSBox-X" 600 440 >>"$OUT/click.log" 2>&1
    echo "ok/enter click at t=$REL" >>"$OUT/click.log"
    ENTERED=1
    sleep 20
    shot $i; i=$((i+1))
  fi
  sleep 4
done
head -c 65536 "$OUT/dosbox.out" > "$OUT/dosbox.out.trim" 2>/dev/null && mv "$OUT/dosbox.out.trim" "$OUT/dosbox.out"
echo "run=$OUT slots=$(ls "$OUT/save" 2>/dev/null | wc -l)"
[ "$(ls "$OUT/save" 2>/dev/null | wc -l)" -ge 1 ] && exit 0 || exit 1
