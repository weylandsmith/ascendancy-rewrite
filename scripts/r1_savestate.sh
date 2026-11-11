#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

# R1 via SAVESTATE, not ptrace (2026-10-05): external attach is dead on this
# box (dosbox-x blocks PTRACE_ATTACH/SEIZE — docs/BLOCKED.md), but dosbox-x's
# own autosave writes ZIP save-states whose 'Memory' member is the FULL guest
# RAM (measured: 17,055,880 B uncompressed == 16 MB + ROM area). That converts
# "dump the live base" into "boot the game headless, grab slot files, grep the
# payload". Smoke-tested 2026-10-05: conf keys machine/memsize/captures/
# autosave/saveremark all accepted; slot files land in <captures>/save/NN.sav.
#
# SAFETY (inherits DOSBOX RULE + R1 invariants):
#   * dosbox NEVER mounts game/ — scratch copy work/r1/game only
#   * stdin=/dev/null, -time-limit hard bound, output under work/r1/r1sav-*
#   * kill by EXACT name only (pkill -x dosbox-x); Xvfb killed by tracked PID
#   * save dir is inside the bounded run dir; sizes printed, never streamed
#
# Usage: scripts/r1_savestate.sh [boot-seconds]   (default 60)
# Exit: 0 = payload found in a save's Memory member (prints guest offset)
#       1 = ran, negative    2 = harness error
set -u
cd "$(dirname "$0")/.."
ROOT=$(pwd)
BOOT="${1:-60}"
OUT="$ROOT/work/r1/r1sav-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUT" || exit 2
SCRATCH="$ROOT/work/r1/game"

pkill -x dosbox-x 2>/dev/null && sleep 1
[ -f "$SCRATCH/ascend.exe" ] || {
  mkdir -p "$SCRATCH/data" || exit 2
  cp -a "$ROOT/game/." "$SCRATCH/" || exit 2
  cp -a "$ROOT/extracted/ascend00/." "$SCRATCH/" 2>/dev/null
  cp -a "$ROOT/extracted/ascend02/data/." "$SCRATCH/data/" 2>/dev/null
}

# X display for the game (output=x11 is what ref_capture.sh proves works)
DISP="${DISPNO:-93}"
Xvfb ":$DISP" -screen 0 800x600x24 >"$OUT/xvfb.out" 2>&1 &
XV=$!
sleep 1

CONF="$OUT/r1sav.conf"
# MEASURED LAW (2026-10-05, two runs): slot files land at <dirname(captures)>/
# save/NN.sav — dosbox-x strips the last path component of `captures` for
# states. Set captures=$OUT/caps states so saves land exactly at $OUT/save.
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

DISPLAY=":$DISP" timeout -s KILL $((BOOT + 40)) dosbox-x -conf "$CONF" -nogui \
  -time-limit "$BOOT" </dev/null >"$OUT/dosbox.out" 2>&1
RC=$?
kill "$XV" 2>/dev/null
pkill -x dosbox-x 2>/dev/null

SIZE=$(du -sk "$OUT/save" 2>/dev/null | cut -f1)
echo "run=$OUT dosbox_rc=$RC save_kb=${SIZE:-0} slots=$(ls "$OUT/save" 2>/dev/null | wc -l)"
head -c 2000 "$OUT/dosbox.out"

if [ ! -d "$OUT/save" ]; then echo "NEGATIVE: no save dir"; exit 1; fi

python3 "$ROOT/scripts/r1_sav_scan.py" --run-dir "$OUT" \
  --needle "$ROOT/work/ascend_payload.bin" > "$OUT/scan.log" 2>&1
SC=$?
head -c 3000 "$OUT/scan.log"
exit $SC
