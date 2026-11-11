#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

# t318: BROADCAST-PUMP LEG WITNESS (docs/re/_wip_t318.md; REFUTED-ROUTES
# t317 amendment (5) is the binding shape spec). t317 proved vendor gutter
# clicks arrive at fn 0x56ca4 as msg 8 on STATSHIPLST's OWN entry and that
# the msg-0xc/4 intake road is the broadcast pump fn 0x56b5c whose slot-2
# dispatch site is file 0x56c74 (call *[tgt+0xa7+8]) — a leg t317 NEVER
# armed, so msg-0xc/4 traffic last run is arming scope, not a measurement.
# Legset: s2_56c74 FIRST priority (at the stop: eax=target rec candidate,
# msg=[esp+8] via ret_stack dump — bank record NAME + msg id), s2_56cda
# (fn 0x56ca4 call site; edi==0x1c01 still names the whole chain),
# fn51cc4_entry (FLEETWND msg entry, edx=msg id), w43508_51fc2 +
# w43504_52003 (writer pair), btn_hdlr (NEXTTURN positive control; 6 legs
# is inside the proven census budget — t304 ran 22).
# Choreography: the PROVEN --shipclick 4 phase VERBATIM (run
# t299-leg-20261106-012002 rc=0: FLEET rails=188 reguard, NO rowjump before
# the phase, one armed window per click x=620 y 250/120/453/300, popup
# reguard, RAW gate 0x600058 read per window) + the STANDARD TAIL
# (rowjump/sprite/planet/NEXTTURN) since pump posters 0x54aa9/0x54ab2 fire
# off the click record ds:0x484ec/0x484f0 — any pump msg into any window is
# banked with its target NAME.
# relaunch loop per r317 pattern: attempt-1 short-circuit law (rc=0 +
# pty-whole-log-census probe => NO attempt 2); rc=2 => never retry.
# Production :9 (pid 1957) untouched; scratch game-wp; kill-by-recorded-PID.
set -u
cd "$(dirname "$0")/.."
OUTDIR=work/r1/t318
mkdir -p "$OUTDIR"
LEGSET=s2_56c74,s2_56cda,fn51cc4_entry,w43508_51fc2,w43504_52003,btn_hdlr
for i in 1 2 2; do
  echo "=== ATTEMPT $i $(date +%H:%M:%S) ==="
  ~/.hermes/hermes-agent/venv/bin/python scripts/r299_leg_session.py \
    --census --legs "$LEGSET" \
    --star-click 0 --target-kinds sprite,planet \
    --pre-turn 1 --digit-keys 0 --fleet-keys 0 --shipclick 4 \
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
