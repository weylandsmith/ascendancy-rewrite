#!/usr/bin/env bash
# t304: relaunch loop for the COMBINED caller-witness + corrected census run
# (--witness 3 --census of r299_leg_session.py). Phase A arms cos_hdlr ONLY
# (hot 0x3b pump -> stops ~2 s; bank_stop dumps [esp] -> ret0 = caller EIP
# verbatim). Phase B re-targets legs to the 22 static slot-2 call sites +
# cos_hdlr + btn_hdlr and runs the t303-proven census click cycle WITH the
# close_eventwin-before-click fix (t298 law) and btn_hdlr armed (t303 defect
# 4b fix). PRIMARY datum = a ret0 file-offset in witness.json -> stop loop
# even if the census is negative. Production :9 untouched; scratch game-wp.
set -u
cd "$(dirname "$0")/.."
OUTDIR=work/r1/t304
mkdir -p "$OUTDIR"
for i in 1 2 3; do
  echo "=== ATTEMPT $i $(date +%H:%M:%S) ==="
  ~/.hermes/hermes-agent/venv/bin/python scripts/r299_leg_session.py \
    --witness 3 --census --window 45 --disp 97 --port 55999 --tl 7200 \
    > "$OUTDIR/attempt-$i-console.log" 2>&1
  rc=$?
  run=$(grep -o 'out=[^ ]*' "$OUTDIR/attempt-$i-console.log" | head -1 | cut -d= -f2)
  echo "attempt $i rc=$rc run=$run"
  if [ -n "${run:-}" ] && grep -q '"ret0_file_off": "0x' "$run/witness.json" 2>/dev/null; then
    echo "ATTEMPT $i BANKED A RET0 CALLER WITNESS — stopping loop"
    break
  fi
  if [ "$rc" -eq 2 ]; then
    echo "ATTEMPT $i harness error — NOT retrying (fix the script)"
    break
  fi
  echo "attempt $i negative; retrying"
done
echo "=== LOOP DONE $(date +%H:%M:%S) ==="
