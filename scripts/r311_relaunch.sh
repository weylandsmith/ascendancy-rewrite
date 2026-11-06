#!/usr/bin/env bash
# t311: STATUSWND-FOCUSED DIGIT KEYS + fn 0x51834 ENTRY LEG (docs/re/
# _wip_t311.md). The entry leg (0x51834, entry bytes 56 57 55 83 ec 0c
# payload-verified t311) fires for EVERY msg to the STATUSWND class with
# dx=msg id — it separates 'class never messaged' from '0x1c01 never sent'.
# Digit keys 1..9 now press on the BARE MAP immediately after --pre-turn +
# close_eventwin + assert_on_map (the t310 focus defect: keys hit a 'Cancel'
# popup), with a post-arm popup reguard.
# Legset ORDER: fn51834_entry FIRST (code-entry leg -> census-ctl MATCH is
# meaningful; t310 lesson: store-imm leg[0] => expected False noise).
# CLOSE: (a) entry stop dx=0x1c01 + store stop -> writer WITNESSED;
# (b) entry stops other dx -> bank msg-id SET; (c) entry zero whole-log with
# btn_hdlr alive -> 0x1c01-into-STATUSWND REFUTED-ROUTES candidate.
# Production :9 untouched; scratch game-wp; kill-by-recorded-PID inside python.
set -u
cd "$(dirname "$0")/.."
OUTDIR=work/r1/t311
mkdir -p "$OUTDIR"
LEGSET=fn51834_entry,w43508_51a8e,w51ac9,s2_1616f,btn_hdlr
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
