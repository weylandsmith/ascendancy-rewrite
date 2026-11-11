#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

# t303: relaunch loop for the MSG-CENSUS session (--census mode of
# r299_leg_session.py). Census mode arms legs ONLY around each measured click
# (arm -> click -> bank-window -> disarm -> liveness), so choreography between
# clicks runs leg-free and the t302 freeze laws cannot bite mid-sequence.
# Success tell: "SESSION END rc=0" in the run's session.log (census measured
# at least one click target). Lottery-lost tell: rc=1. rc=2 = harness error,
# do NOT retry. Production :9 untouched; scratch game-wp; own ring dir.
set -u
cd "$(dirname "$0")/.."
OUTDIR=work/r1/t303
mkdir -p "$OUTDIR"
for i in 1 2 3; do
  echo "=== ATTEMPT $i $(date +%H:%M:%S) ==="
  ~/.hermes/hermes-agent/venv/bin/python scripts/r299_leg_session.py \
    --census --window 45 --disp 97 --port 55999 --tl 3600 \
    > "$OUTDIR/attempt-$i-console.log" 2>&1
  rc=$?
  run=$(grep -o 'out=[^ ]*' "$OUTDIR/attempt-$i-console.log" | head -1 | cut -d= -f2)
  echo "attempt $i rc=$rc run=$run"
  if [ -n "${run:-}" ] && grep -q "SESSION END rc=0" "$run/session.log" 2>/dev/null; then
    echo "ATTEMPT $i BANKED A CENSUS — stopping loop"
    break
  fi
  if [ "$rc" -eq 2 ]; then
    echo "ATTEMPT $i harness error — NOT retrying (fix the script)"
    break
  fi
  echo "attempt $i negative; retrying"
done
echo "=== LOOP DONE $(date +%H:%M:%S) ==="
