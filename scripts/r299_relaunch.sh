#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

# t299: relaunch loop for the debugger leg-witness session (BREAK lottery is a
# per-attempt coin flip, t286 law 2). Each attempt is a FULL
# r299_leg_session.py run (own ring dir, Xvfb :97, scratch game-wp,
# kill-by-recorded-PID). Production :9 untouched.
# Success tell: "SESSION END rc=0" or any "STOP " line with leg= in the run's
# session.log. Lottery-lost tell: rc=1 + "BREAK lottery lost" / channel dead.
set -u
cd "$(dirname "$0")/.."
OUTDIR=work/r1/t299
mkdir -p "$OUTDIR"
for i in 1 2 3; do
  echo "=== ATTEMPT $i $(date +%H:%M:%S) ==="
  ~/.hermes/hermes-agent/venv/bin/python scripts/r299_leg_session.py \
    --disp 97 --port 55999 --tl 3600 \
    > "$OUTDIR/attempt-$i-console.log" 2>&1
  rc=$?
  run=$(grep -o 'out=[^ ]*' "$OUTDIR/attempt-$i-console.log" | head -1 | cut -d= -f2)
  echo "attempt $i rc=$rc run=$run"
# Success tell (t302 TIGHTENED): a lone early STOP is NOT the goal — t302-2
# banked one real stop then died on the resume defect while the loop celebrated.
# Require the FULL battery: "SESSION END rc=0", or a stop whose tag names a
# click (sprite/planet/empty/row). An early post-run-immediate stop alone =
# keep looping AND report the resume defect.
  if [ -n "${run:-}" ] && grep -qE "SESSION END rc=0|STOP [^ ]*(sprite|planet|empty)[^ ]* leg=" "$run/session.log" 2>/dev/null; then
    echo "ATTEMPT $i BANKED A FULL-WITNESS — stopping loop"
    break
  fi
  if [ -n "${run:-}" ] && grep -q "leg=" "$run/session.log" 2>/dev/null; then
    echo "ATTEMPT $i partial: banked an early stop but battery incomplete (resume defect?)"
  fi
  if [ "$rc" -eq 2 ]; then
    echo "ATTEMPT $i harness error — NOT retrying (fix the script)"
    break
  fi
  echo "attempt $i negative; retrying"
done
echo "=== LOOP DONE $(date +%H:%M:%S) ==="
