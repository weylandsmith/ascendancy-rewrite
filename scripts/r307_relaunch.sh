#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

# t307: SELECTION-WRITER WITNESS at the SURVIVING STORE FAMILY. Arm the eight
# non-batmode members of the t296 store census (w43504_{28ec2,28ef6,36b01,
# 52003,55d35} + w43508_{51a8e,51fc2,55bbd}; every byte verified vs payload
# this session) + btn_hdlr positive control, under the fixed [cpu]core=normal
# conf with the t305 FirePat detector. NEW --star-click N: click N bright
# galaxy-map pips (r293 enter_system candidate law), classify hit by screen
# diff >15000, escape ladder between clicks. --target-kinds none: the
# system-view sprite phase is SKIPPED (t305/t306 measured it; campaign-load
# view IS the map, open_fleet would drag us off it mid-run). Windows:
# baseline(15s) + star0..2 + control_nextturn. cos_hdlr/56cda NOT armed
# (0x3b pump storm crowds bank_stop cap 6; pty census counts armed legs only).
# Production :9 untouched; scratch game-wp; kill-by-recorded-PID inside python.
set -u
cd "$(dirname "$0")/.."
OUTDIR=work/r1/t307
mkdir -p "$OUTDIR"
LEGSET=w43504_28ec2,w43504_28ef6,w43504_36b01,w43504_52003,w43504_55d35,w43508_51a8e,w43508_51fc2,w43508_55bbd,btn_hdlr
for i in 1 2 2; do
  echo "=== ATTEMPT $i $(date +%H:%M:%S) ==="
  ~/.hermes/hermes-agent/venv/bin/python scripts/r299_leg_session.py \
    --census --legs "$LEGSET" \
    --star-click 3 --target-kinds none \
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
