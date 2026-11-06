#!/usr/bin/env bash
# t320: THE MOUSE-ACTIVE POSTER-PASS RUN (docs/re/_wip_t320.md; STATE.md NEXT
# ACTION t320; REFUTED-ROUTES t319 amendment (1)-(4) binding). t319 banked the
# poster call site 0x54ac5 LIVE with msg 4; msg 0xc requires [core+0x24da4]==-1
# which requires ds:0x484ac!=0 in the SAME fn 0x54650 pass (writer census,
# _wip_t320 S1.2). Shape: legs {pump_entry_56b5c} ONLY + the proven
# --shipclick 4 gutter choreography + --pulse-clicks (extra Button1 pulses at
# the click coord INSIDE each armed window; xsend has no motion verb and SDL
# rejects synthetic MotionNotify — a real click is the activator).
# relaunch loop per r319 pattern: attempt-1 short-circuit law (rc=0 +
# pty-whole-log-census probe => NO attempt 2); rc=2 => never retry.
# Production :9 (pid 1957) untouched; scratch game-wp; kill-by-recorded-PID.
set -u
cd "$(dirname "$0")/.."
OUTDIR=work/r1/t320
mkdir -p "$OUTDIR"
LEGSET=pump_entry_56b5c
for i in 1 2 2; do
  echo "=== ATTEMPT $i $(date +%H:%M:%S) ==="
  ~/.hermes/hermes-agent/venv/bin/python scripts/r299_leg_session.py \
    --census --legs "$LEGSET" \
    --star-click 0 --target-kinds sprite,planet \
    --pre-turn 1 --digit-keys 0 --fleet-keys 0 --shipclick 4 \
    --pulse-clicks 30 \
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
