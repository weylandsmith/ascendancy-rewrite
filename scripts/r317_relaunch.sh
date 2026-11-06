#!/usr/bin/env bash
# t317: SHIP-LIST-GUTTER-CLICK -> FLEETWND msg-0x1c01 LIVE WITNESS
# (docs/re/_wip_t317.md). t316 made the chain continuous statically (click in
# STATSHIPLST -> fn 0x33320 -> fn 0x56ca4(0x7a35c, edx=[w+0x63]=95, msg 0x1c01)
# -> registry slot95 win = FLEETWND rec -> [rec+0xa7+8] = fn 0x51cc4 -> gate
# 0x600058 -> writer pair) and proved saves can never witness delivery.
# t317 S1 CORRECTED the click geometry: the emit road is the RIGHT 28-px
# GUTTER (x in (604,632], y in [46,472]), msg 4/5 family — NOT the row body,
# and NOT msg 0xc ([w+0x4f]=0x66 != 0x30, measured).
# Legset: fn51cc4_entry FIRST (FLEETWND msg entry; edx=msg id; COLD in t314),
# s2_56cda = THE dispatch call site inside fn 0x56ca4 (eax=registry win rec,
# esi=cp, edi=MSG — edi==0x1c01 witnesses the whole chain in one reg set;
# call-site beats entry-leg: proves mode-gate pass + registry deref),
# w43508_51fc2 + w43504_52003 (the writer pair), btn_hdlr (road diagnosis +
# NEXTTURN positive control). NO STATUSWND/batmode legs (amendments binding).
# Choreography: --pre-turn 1 -> open_fleet (rails=188 reguard) -> BASELINE
# armed window -> 4 gutter clicks x=620 (y 250,120,453,300), one armed window
# per click, popup+FLEET double reguard, RAW gate 0x600058 read after each ->
# then the standard rowjump/sprite/planet/NEXTTURN tail.
# Production :9 untouched; scratch game-wp; kill-by-recorded-PID in python.
set -u
cd "$(dirname "$0")/.."
OUTDIR=work/r1/t317
mkdir -p "$OUTDIR"
LEGSET=fn51cc4_entry,s2_56cda,w43508_51fc2,w43504_52003,btn_hdlr
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
