#!/usr/bin/env bash
# t309: WITNESS THE RING CONSUMER FAMILY (0x55ae8 RING-B consumer, 0x55df4
# RING-A resolver) INSIDE ARMED WINDOWS, incl. the two HOT HOLD windows that
# fix the t308 blind spot (post-disarm execution is invisible to the pty
# whole-log census; only an ARMED leg can stop — docs/re/_wip_t309.md S1.7).
# Legset (bytes payload-verified this session): cons_entry 0x55ae8,
# ringB_post 0x55a60, ringB code-0x10 posters {0x41c17,0x499e0},
# ringA_resolver 0x55df4 (positive control), w43504_28ec2 (t308 witness leg),
# btn_hdlr (NEXTTURN control). Oracle extended with mode4226 / ring counters /
# pump_gate_660c / guard_7a358 + turn-delta pair around control_nextturn.
# Production :9 untouched; scratch game-wp; kill-by-recorded-PID inside python.
set -u
cd "$(dirname "$0")/.."
OUTDIR=work/r1/t309
mkdir -p "$OUTDIR"
LEGSET=cons_entry,ringB_post,ringB_w10_41c17,ringB_w10_499e0,ringA_resolver,w43504_28ec2,btn_hdlr
for i in 1 2 2; do
  echo "=== ATTEMPT $i $(date +%H:%M:%S) ==="
  ~/.hermes/hermes-agent/venv/bin/python scripts/r299_leg_session.py \
    --census --legs "$LEGSET" \
    --star-click 6 --target-kinds none \
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
