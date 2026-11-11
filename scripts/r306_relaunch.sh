#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

# t306: SELECTION-WRITER WITNESS — arm the t296 static gate/effect sites
# (BatModeWnd entry 0x1aef8, msg-4 router 0x1b070, msg-0x53 effect 0x1b71f,
# mouse effect 0x1ba39) + btn_hdlr positive control, under the FIXED
# [cpu]core=normal conf with the t305 FirePat detector. Targets: sprite +
# control_nextturn ONLY (planet/empty datum done t305). Selection oracle
# (DAT_43504/43508/sel43510 before/after each click) is inside
# scripts/r299_leg_session.py (patched t306). cos_hdlr/56cda deliberately NOT
# armed: the 0x3b pump storm floods bank_stop (cap 6/window) and would crowd
# out the cold bat legs; the pty whole-log census only counts ARMED legs.
# Production :9 untouched; scratch game-wp; kill-by-recorded-PID inside python.
set -u
cd "$(dirname "$0")/.."
OUTDIR=work/r1/t306
mkdir -p "$OUTDIR"
for i in 1 2 2; do
  echo "=== ATTEMPT $i $(date +%H:%M:%S) ==="
  ~/.hermes/hermes-agent/venv/bin/python scripts/r299_leg_session.py \
    --census --legs batmode_dead,bat_router,bat_s53,bat_mouse,btn_hdlr \
    --target-kinds sprite --window 60 --disp 97 --port 55999 --tl 7200 \
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
