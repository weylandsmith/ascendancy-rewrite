#!/usr/bin/env bash
# t286b: relaunch loop for the blind planet-list watchpoint hunt (BREAK
# lottery ~50% per attempt, t286 law 2: retry until 'armed:' in session.log).
# Each attempt is a FULL r1_wp_session.py session (script owns its ring dir,
# Xvfb :97, scratch game-wp, kill-by-recorded-PID). Production :9 untouched.
# Corrected target (off-by-H fix): linear 0xfda8b3 = member 0xfda93b - 0x88.
set -u
cd "$(dirname "$0")/.."
OUTDIR=work/r1/t286b
mkdir -p "$OUTDIR"
for i in 1 2 3; do
  echo "=== ATTEMPT $i $(date +%H:%M:%S) ==="
  python3 scripts/r1_wp_session.py \
    --target heap-planets-blind --expect-base 0x1bf4d8 \
    --break-early --phases quiet,reopen \
    > "$OUTDIR/attempt-$i-console.log" 2>&1
  rc=$?
  run=$(grep -o 'out=[^ ]*' "$OUTDIR/attempt-$i-console.log" | head -1 | cut -d= -f2)
  echo "attempt $i rc=$rc run=$run"
  if [ -n "${run:-}" ] && grep -q "armed:" "$run/session.log" 2>/dev/null; then
    echo "ATTEMPT $i ARMED (BREAK survived)"
    if grep -q "REAL FIRE" "$OUTDIR/attempt-$i-console.log"; then
      echo "ATTEMPT $i FIRED — stopping loop"
      break
    fi
    echo "armed but no fire; assignment allows up to 3 attempts — continuing"
  fi
done
echo "=== LOOP DONE $(date +%H:%M:%S) ==="
