#!/usr/bin/env bash
# Reference-capture harness for the ORIGINAL game under dosbox-x + Xvfb.
# Closes the "dosbox screenshot comparison (needs a reference capture
# harness)" subitem in STATE.md P5. Produces ground-truth PNGs only; the
# comparison side is scripts/refcap_match.py.
#
# SAFETY (inherits STATE.md DOSBOX RULE + R1 invariants deliberately):
#   * NEVER mounts game/ — runs from the scratch copy in work/r1/game
#   * stdin=/dev/null, -time-limit bounds the emulator, all waits deadline'd
#   * emulator killed by EXACT name only: pkill -x dosbox-x
#   * all output under work/refcap/run-<stamp>/, logs size-capped
#
# Env knobs: DISPNO BOOT_WAIT CLICK_X CLICK_Y CLICK_AFTER SHOTS INTERVAL_MS
#            TIME_LIMIT EXTRA_ARGS (space-separated dosbox args)
set -u
cd "$(dirname "$0")/.."
ROOT=$(pwd)

DISPLAY_NO="${DISPNO:-92}"
BOOT_WAIT="${BOOT_WAIT:-10}"
CLICK_AFTER="${CLICK_AFTER:-2}"      # seconds after first shot before clicking
CLICK_X="${CLICK_X:-}"               # empty = no click (menu shot only)
CLICK_Y="${CLICK_Y:-}"
SHOTS="${SHOTS:-6}"
INTERVAL_MS="${INTERVAL_MS:-500}"
SCRATCH="$ROOT/work/r1/game"
OUT="$ROOT/work/refcap/run-$(date +%Y%m%d-%H%M%S)"

for tool in Xvfb import dosbox-x; do
  command -v "$tool" >/dev/null || { echo "MISSING $tool"; exit 2; }
done

pkill -x dosbox-x 2>/dev/null && sleep 1
rm -rf "$OUT"; mkdir -p "$OUT" || exit 2

if [ ! -f "$SCRATCH/ascend.exe" ]; then
  mkdir -p "$SCRATCH"
  cp -a "$ROOT/game/." "$SCRATCH/" || exit 2
  cp -a "$ROOT/extracted/ascend00/." "$SCRATCH/" 2>/dev/null
  mkdir -p "$SCRATCH/data"
  cp -a "$ROOT/extracted/ascend02/data/." "$SCRATCH/data/" 2>/dev/null
fi
EXE=$(ls "$SCRATCH" | grep -im1 '^ascend\.exe$')
[ -n "$EXE" ] || { echo "ascend.exe missing in scratch"; exit 2; }

CONF="$OUT/refcap.conf"
cat > "$CONF" <<EOF
[dosbox]
machine=svga_s3
memsize=16
[sdl]
output=x11
fullscreen=false
autolock=false
[mixer]
nosound=true
[autoexec]
MOUNT C $SCRATCH
C:
$EXE
EOF

Xvfb ":$DISPLAY_NO" -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1

DISPLAY=":$DISPLAY_NO" timeout -s KILL 180 dosbox-x -conf "$CONF" -nogui \
  -time-limit "${TIME_LIMIT:-60}" ${EXTRA_ARGS:-} </dev/null \
  >"$OUT/dosbox.out" 2>&1 &
DB=$!

sleep "$BOOT_WAIT"
i=0
CLICKED=0
END=$((SECONDS + 150))
while [ "$i" -lt "$SHOTS" ] && [ "$SECONDS" -lt "$END" ]; do
  DISPLAY=":$DISPLAY_NO" import -window root "$OUT/frame-$(printf %02d "$i").png" 2>/dev/null
  i=$((i+1))
  if [ "$CLICKED" = 0 ] && [ -n "$CLICK_X" ] && [ $i -ge 2 ]; then
    sleep "$CLICK_AFTER"
    DISPLAY=":$DISPLAY_NO" "$ROOT/tools/xsend" "DOSBox-X" "$CLICK_X" "$CLICK_Y" \
      >>"$OUT/click.log" 2>&1
    CLICKED=1
  fi
  usleep $((INTERVAL_MS * 1000)) 2>/dev/null || sleep 1
done

kill -TERM "$DB" 2>/dev/null
pkill -x dosbox-x 2>/dev/null
kill "$XV" 2>/dev/null
wait 2>/dev/null

head -c 65536 "$OUT/dosbox.out" > "$OUT/dosbox.out.trim" 2>/dev/null &&
  mv "$OUT/dosbox.out.trim" "$OUT/dosbox.out"
echo "shots=$i"
echo "REFCAP OUT=$OUT"
cat "$OUT/click.log" 2>/dev/null
