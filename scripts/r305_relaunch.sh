#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

# t305: relaunch loop for the COMBINED witness+census run under the FIXED
# [cpu]core=normal conf, with the t305 FIRE-PATTERN FIX (fire_pats dual
# 6-hex/5-hex; normal core renders stop addresses TRUNCATED TO 5 HEX — run
# t299-leg-20261105-052925 proved stops were happening unbanked all along).
# PRIMARY datum this iteration = census.json with per-target measured stops at
# the 22 slot-2 sites + cos_hdlr + btn_hdlr (the OQ-019 selection-writer
# msg-ids); witness phase (cos_hdlr ret0 x3) re-confirms under normal core.
# Production :9 untouched; scratch game-wp; kill-by-recorded-PID inside the
# python session.
set -u
cd "$(dirname "$0")/.."
OUTDIR=work/r1/t305
mkdir -p "$OUTDIR"
for i in 1 2 2; do
  echo "=== ATTEMPT $i $(date +%H:%M:%S) ==="
  ~/.hermes/hermes-agent/venv/bin/python scripts/r299_leg_session.py \
    --witness 3 --census --window 60 --disp 97 --port 55999 --tl 7200 \
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
