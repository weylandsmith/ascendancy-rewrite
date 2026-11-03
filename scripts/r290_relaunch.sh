#!/usr/bin/env bash
# t290: relaunch loop for the threshold-freeze session (BREAK lottery, t286
# law 2: retry until 'armed:' in session.log). Each attempt is a FULL
# r290_poke_session.py run (owns its ring dir, Xvfb :96, scratch game-wp,
# kill-by-recorded-PID). Production :9 untouched.
#   usage: r290_relaunch.sh <mode> <arm-value> [max-attempts]
set -u
cd "$(dirname "$0")/.."
MODE="${1:-freeze}"
AV="${2:-34}"
MAX="${3:-4}"
OUTDIR=work/r1/t290-loop
mkdir -p "$OUTDIR"
for i in $(seq 1 "$MAX"); do
  echo "=== ATTEMPT $i $(date +%H:%M:%S) mode=$MODE arm=$AV"
  python3 scripts/r290_poke_session.py --mode "$MODE" --arm-value "$AV" \
    > "$OUTDIR/attempt-$i-$MODE-$AV-console.log" 2>&1
  rc=$?
  run=$(grep -o 'out=[^ ]*' "$OUTDIR/attempt-$i-$MODE-$AV-console.log" | tail -1 | cut -d= -f2)
  echo "attempt $i rc=$rc run=${run:-none}"
  if [ "$rc" -eq 0 ]; then
    echo "ATTEMPT $i POSITIVE — stopping loop"
    exit 0
  fi
  if [ -n "${run:-}" ] && ! grep -q "armed:" "$run/session.log" 2>/dev/null; then
    echo "attempt $i lost the BREAK lottery — relaunching"
    continue
  fi
  if grep -q "NEGATIVE: title menu" "$OUTDIR/attempt-$i-$MODE-$AV-console.log" 2>/dev/null; then
    echo "attempt $i hit the title-menu bail — relaunching is safe (no clicks landed)"
    continue
  fi
  # armed, ran to a real negative conclusion: relaunching repeats the same
  # deterministic pass; two independent negatives are enough, three is waste.
  echo "attempt $i ran armed to a negative — stopping loop (honest negative banked)"
  exit 1
done
echo "=== LOOP DONE (attempts exhausted) $(date +%H:%M:%S)"
exit 1
