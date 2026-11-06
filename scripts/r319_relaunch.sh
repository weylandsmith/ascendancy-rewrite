#!/usr/bin/env bash
# t319: PUMP CALLER/GATE SEPARATION RUN (docs/re/_wip_t319.md; REFUTED-ROUTES
# t318 amendment (3) is the binding shape spec). t318 measured pump DISPATCH
# s2_56c74 COLD whole-log while s2_56cda fired 26x — the question is WHY fn
# 0x56b5c's poster road never delivers: (A) caller-never, (B) poster-gate-
# never-equal, (C) pump-entry-never. Legset separates all three in ONE run:
# pump_entry_56b5c banks ret0 (which of the NINE E8 callers fired) + edx (msg
# id); p54a47 (ds:0x484a4-EQUAL road) and p54a88 (the [esi+0x24da4] cmp, edi=
# msg id candidate, esi=core obj) name which gate road traffic takes;
# s2_56c74 + s2_56cda carried for continuity with t317/t318. fn51cc4_entry +
# the writer pair DROP (zero twice, strictly downstream).
# Choreography: the PROVEN --shipclick 4 phase VERBATIM (runs
# t299-leg-20261106-012002 + -021602 rc=0) + the standard tail.
# relaunch loop per r318 pattern: attempt-1 short-circuit law (rc=0 +
# pty-whole-log-census probe => NO attempt 2); rc=2 => never retry.
# Production :9 (pid 1957) untouched; scratch game-wp; kill-by-recorded-PID.
set -u
cd "$(dirname "$0")/.."
OUTDIR=work/r1/t319
mkdir -p "$OUTDIR"
LEGSET=pump_entry_56b5c,p54a47,p54a88,s2_56c74,s2_56cda
for i in 1 2 2; do
  echo "=== ATTEMPT $i $(date +%H:%M:%S) ==="
  ~/.hermes/hermes-agent/venv/bin/python scripts/r299_leg_session.py \
    --census --legs "$LEGSET" \
    --star-click 0 --target-kinds sprite,planet \
    --pre-turn 1 --digit-keys 0 --fleet-keys 0 --shipclick 4 \
    --window 60 --disp 97 --port 55999 --tl 7200 \
    > "$OUTDIR/attempt-$i-console.log" 2>&1
  rc=$?
  run=$(grep -o 'out=[^ ]*' "$OUTDIR/attempt-$i-console.log" | head -1 | cut -d= -f2)
  echo "attempt $i rc=$rc run=$run"
  if [ -n "${run:-}" ] && grep -q '"probe": "pty-whole-log-census"' "$run/probes.json" 2>/dev/null; then
    if grep -q 'SESSION END rc=0' "$run/session.log" 2>/dev/null; then
      echo "ATTEMPT $i MEASURED CENSUS (rc=0) — stopping loop"
      break
    fi
  fi
  if [ "$rc" -eq 2 ]; then
    echo "ATTEMPT $i harness error — NOT retrying (fix the script)"
    break
  fi
  echo "attempt $i negative; retrying"
done
echo "=== LOOP DONE $(date +%H:%M:%S) ==="
