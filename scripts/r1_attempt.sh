#!/usr/bin/env bash
# R1 attempt (option C cadence, docs/BLOCKED.md): ONE bounded attempt to dump
# the live data base from the original game under dosbox-x. Safe by
# construction (STATE.md DOSBOX RULE, 12 GB incident):
#   * dosbox NEVER mounts game/ — it runs from a scratch copy in work/r1/game
#   * headless: output=dummy, nosound, stdin=/dev/null, -time-limit inside
#     scripts/r1_tracer.py; every wait is WNOHANG with a deadline
#   * stray emulators are killed by EXACT name (pkill -x), never -f
#   * all output lands in work/r1/attempt-<stamp>/ and is size-capped
# Exit codes (the loop records these in STATE.md, does not retry the turn):
#   0 = TRACABLE with payload hit  -> R1 route LIVE: upgrade formulas (BLOCKED.md)
#   1 = attempt ran, negative       -> normal under C; continue B-priority work
#   2 = harness error               -> fix the harness (a human decision item)
set -u
cd "$(dirname "$0")/.."
ROOT=$(pwd)
STAMP=$(date +%Y%m%d-%H%M%S)
OUT="$ROOT/work/r1/attempt-$STAMP"
mkdir -p "$OUT" || exit 2

# no nested attempts, no orphans from an earlier crash
pkill -x dosbox-x 2>/dev/null && sleep 1

# Scratch copy. game/ is opened read-only and checksummed by the gate; the
# emulator must never get a writable mount of it. Layout follows the OQ-004
# hypothesis (installer unpacked the archives): game files at root, ascend00
# plaintext loose, ascend02 data\ under DATA\. If the hypothesis is wrong the
# game just exits early and the attempt records that — still bounded.
SCRATCH="$ROOT/work/r1/game"
mkdir -p "$SCRATCH" "$OUT"
rm -rf "${SCRATCH:?}"/*
cp -a "$ROOT/game/." "$SCRATCH/" || exit 2
cp -a "$ROOT/extracted/ascend00/." "$SCRATCH/" 2>/dev/null
mkdir -p "$SCRATCH/data"
cp -a "$ROOT/extracted/ascend02/data/." "$SCRATCH/data/" 2>/dev/null

# bounded headless config — every key verified present in the dosbox-x
# 2025.02.01 generated user conf ([dosbox] machine/memsize, [sdl] output,
# [mixer] nosound); nothing invented
CONF="$OUT/r1.conf"
cat > "$CONF" <<EOF
[dosbox]
machine=svga_s3
memsize=16
[sdl]
output=dummy
autolock=false
[mixer]
nosound=true
[autoexec]
MOUNT C $SCRATCH
C:
ASCEND.EXE
EOF

timeout -s KILL 300 /usr/bin/python3 "$ROOT/scripts/r1_tracer.py" \
  --conf "$CONF" --needle "$ROOT/work/ascend_payload.bin" \
  --dump-dir "$OUT/dumps" --boot-seconds "${R1_BOOT_SECONDS:-30}" \
  </dev/null >"$OUT/tracer.log" 2>&1
RC=$?

# last-resort cleanup: exact-name only (pkill -f matches this script's own
# command line — it killed the gate's shell once already)
pkill -x dosbox-x 2>/dev/null

echo "--- r1 attempt $STAMP (rc=$RC) ---"
head -c 4000 "$OUT/tracer.log"
if [ "$RC" -eq 0 ] && grep -q 'PAYLOAD HIT' "$OUT/tracer.log"; then
  echo "R1 LIVE: runtime base recoverable — see docs/BLOCKED.md upgrade branch"
  exit 0
elif grep -q 'harness-error\|Traceback' "$OUT/tracer.log" || [ "$RC" -gt 2 ]; then
  echo "R1 HARNESS ERROR — do not log as a negative result"
  exit 2
else
  echo "R1 negative this attempt (expected under C; B-priority unchanged)"
  exit 1
fi
