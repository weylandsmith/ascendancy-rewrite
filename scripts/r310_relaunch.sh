#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

# t310: WITNESS THE DESTINATION-WIDGET WRITER FAMILY (DAT_43508 / DAT_43504
# stores of fn 0x51834's msg-0x1c01 path, docs/re/_wip_t310.md S1b) VIA A LIVE
# ORDER FLOW, and name the callers from ret_stack (bank_stop dumps [esp]).
# Legset (bytes payload-verified this session): w43508_51a8e, w43508_51fc2,
# w51ac9 (NEW), w43504_52003, s2_1616f (msg-0x1c01 relay site, NEW), btn_hdlr
# (NEXTTURN control). Battery: --pre-turn 1 (t298 gate: no kind-4 owner-0 ship
# at t=1086) -> fleet view -> sprite select -> planet destination click ->
# --digit-keys 9 (the OTHER 0x1c01 sender, digit-key handler 0x35696) ->
# control_nextturn + hot hold. Star-click omitted (star-case closed t308).
# Oracle extended: gate_7e5aa / gate_7e89e / gate_484ec.
# Production :9 untouched; scratch game-wp; kill-by-recorded-PID inside python.
set -u
cd "$(dirname "$0")/.."
OUTDIR=work/r1/t310
mkdir -p "$OUTDIR"
LEGSET=w43508_51a8e,w43508_51fc2,w51ac9,w43504_52003,s2_1616f,btn_hdlr
for i in 1 2 2; do
  echo "=== ATTEMPT $i $(date +%H:%M:%S) ==="
  ~/.hermes/hermes-agent/venv/bin/python scripts/r299_leg_session.py \
    --census --legs "$LEGSET" \
    --star-click 0 --target-kinds sprite,planet \
    --pre-turn 1 --digit-keys 9 \
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
