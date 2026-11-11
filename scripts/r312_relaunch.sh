#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

# t312: ORDER-PLACEMENT WRITER RUN (docs/re/_wip_t312.md). The t311 amendment
# refuted 0x1c01-into-STATUSWND; the remaining never-armed destination writers
# are fn 0x51b68's pair {w43504_52003 DAT_43504 eax=[esi+0x59], w43508_51fc2
# DAT_43508 eax=[edx+0x59]} (t309 S3.4 inventory: fn 0x51b68 owns the densest
# selection-write cluster; table-member-called so ret_stack names the caller).
# Choreography = the t298-B order shape the existing r299 census path already
# drives: --pre-turn 1 (kind-4 owner-0 gate) -> bare-map digit keys 1..9 (t311
# shape, cheap sender witness) -> fleet rowjump -> sprite click -> planet click
# (separate armed windows) -> NEXTTURN -> holds.
# Legset ORDER: fn51834_entry FIRST (code-entry leg -> census-ctl MATCH is
# meaningful, t311 law; kept ONLY as ctl anchor + sender witness — do NOT
# expect it to fire, REFUTED-ROUTES t311). s2_356a5 = digit sender's own call
# site. btn_hdlr = positive control. NO batmode legs (t306 amendment).
# CLOSE: stop at 0x52003/0x51fc2 = writer WITNESSED; all-writer zeros with
# btn_hdlr alive = fn 0x51b68 unreached by order clicks (bank, narrow OQ-019).
# Production :9 untouched; scratch game-wp; kill-by-recorded-PID inside python.
set -u
cd "$(dirname "$0")/.."
OUTDIR=work/r1/t312
mkdir -p "$OUTDIR"
LEGSET=fn51834_entry,w43504_52003,w43508_51fc2,s2_356a5,btn_hdlr
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
