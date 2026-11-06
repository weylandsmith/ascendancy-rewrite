#!/usr/bin/env bash
# t314: FLEETWND-FOCUS msg-0x1c01 LIVE CAPTURE (docs/re/_wip_t314.md). t313
# closed the offline caller hunt: fn 0x51b68 is mid-body of fn 0x51b64 =
# FLEETWND class-grid slot 3, and FLEETWND's msg handler fn 0x51cc4 owns its
# own msg-0x1c01 path (je@0x51cfa->0x51f3b raw-verified) whose continuation
# blocks ARE the t312 writer pair {w43508_51fc2 DAT_43508 states 1-3,
# w43504_52003 DAT_43504 state 4} via the runtime state table RAM 0x211188.
# The writers were dark in t312 because digit focus was the NEXTTURNCONT btn
# class, never FLEETWND (REFUTED-ROUTES t313 amendment binding).
# Legset ORDER: fn51cc4_entry FIRST (code-entry leg -> census-ctl MATCH is
# meaningful, t311 entry-leg law; fires for ANY msg to FLEETWND, edx = msg id
# at the stop, ret0 = dispatch site). NO STATUSWND legs and NO bare-map digit
# sender leg (t311/t312/t313 amendments binding). btn_hdlr = positive control.
# Choreography: --pre-turn 1 (kind-4 owner-0 gate) -> open_fleet -> rowjump0
# (fleet-list selection, NOT the map pixel) -> --fleet-keys 9 with the FLEET
# window OPEN (post-arm popup reguard) -> sprite/planet click windows ->
# NEXTTURN control -> hold.
# CLOSE: a writer stop with named ret0 = WITNESSED (ret0 in 0x211xxx = the
# RAM-composed dispatch stub — first direct witness of that mechanism).
# fn51cc4_entry fires but no 0x1c01 = digit sender's window-selection is the
# hole (bank msg ids). fn51cc4_entry zero with FLEET open = FLEETWND receives
# no key msgs at all. Production :9 untouched; scratch game-wp; kill-by-
# recorded-PID inside python.
set -u
cd "$(dirname "$0")/.."
OUTDIR=work/r1/t314
mkdir -p "$OUTDIR"
LEGSET=fn51cc4_entry,w43508_51fc2,w43504_52003,btn_hdlr
for i in 1 2 2; do
  echo "=== ATTEMPT $i $(date +%H:%M:%S) ==="
  ~/.hermes/hermes-agent/venv/bin/python scripts/r299_leg_session.py \
    --census --legs "$LEGSET" \
    --star-click 0 --target-kinds sprite,planet \
    --pre-turn 1 --digit-keys 0 --fleet-keys 9 \
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
