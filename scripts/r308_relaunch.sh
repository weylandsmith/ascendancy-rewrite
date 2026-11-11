#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

# t308: WITNESS A TRUE DAT_43504 DELTA. Same 9-leg set as t307 (8 store-census
# writers + btn_hdlr control; bytes payload-verified t307), same fixed normal-
# core conf + FirePat detector (regression 5/5 re-run this session). Changes:
# sel_oracle pair is NAME-BEARING (DAT_43504_name via star_name_at + the
# disambiguating alt_285504 read), the star phase BREAKS the pip loop on the
# first entered-click whose oracle pair flips DAT_43504 (the strict-close
# datum), and --star-click 3 -> 6 (t307 needed 2 pips for one ENTER; the idle
# scalar is the Icarus ptr so the witness needs an ENTER on a DIFFERENT star).
# S1 law this session: oracle address == rebased store target (member +0x88 ==
# linear); no oracle re-pointing needed — only the alt read for disambiguation.
# Production :9 untouched; scratch game-wp; kill-by-recorded-PID inside python.
set -u
cd "$(dirname "$0")/.."
OUTDIR=work/r1/t308
mkdir -p "$OUTDIR"
LEGSET=w43504_28ec2,w43504_28ef6,w43504_36b01,w43504_52003,w43504_55d35,w43508_51a8e,w43508_51fc2,w43508_55bbd,btn_hdlr
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
