#!/usr/bin/env bash
# t322: BATCON TWO-CLICK ORDER-WITNESS (docs/re/_wip_t322.md; STATE.md NEXT
# ACTION t322). FIRST-EVER arming of the batcon DAT_43508 stores 0x1b5e6 /
# 0x1baa7 (REFUTED-ROUTES t321 amendment (3): the writer-zero series t307..t320
# never tested the mouse road; the t306 "do not re-arm" clause is SUPERSEDED
# for exactly these legs by t321(3)+(6)). Legset: batmode_dead FIRST (code-entry
# leg[0] -> census-ctl MATCH meaningful, t311 law; also the fn 0x1aef8 entry
# witness) + fn1b91c_entry + the two stores + btn_hdlr positive control.
# NO cos_hdlr/s2_* (pump storm floods the 6-stop bank cap, t306 launch law).
# Choreography = t298 corrected picker path: --pre-turn 1 (kind-4 slot 8) ->
# fleet rowjump -> sprite/planet clicks (separate armed windows, close_eventwin
# between) -> NEXTTURN -> hold. Recorder-first law t318: bank_stop dumps
# [win+0xaf]/[+0xb3]/[+0xb7] at EVERY fn1b91c/batmode stop.
# relaunch loop per r319/r320 pattern: attempt-1 short-circuit law (rc=0 +
# pty-whole-log-census probe => NO attempt 2); rc=2 => never retry.
# Production :9 (pid 1957) untouched; scratch game-wp; kill-by-recorded-PID.
set -u
cd "$(dirname "$0")/.."
OUTDIR=work/r1/t322
mkdir -p "$OUTDIR"
LEGSET=batmode_dead,fn1b91c_entry,w43508_1b5e6,w43508_1baa7,btn_hdlr
for i in 1 2 2; do
  echo "=== ATTEMPT $i $(date +%H:%M:%S) ==="
  ~/.hermes/hermes-agent/venv/bin/python scripts/r299_leg_session.py \
    --census --legs "$LEGSET" \
    --star-click 0 --target-kinds sprite,planet \
    --pre-turn 1 --digit-keys 0 --fleet-keys 0 --shipclick 0 \
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
