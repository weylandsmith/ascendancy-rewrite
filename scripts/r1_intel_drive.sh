#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

# t65 OUTER driver — OQ-005 draw-path capture. Opens the Intelligence
# panel [verified geometry extracted/ascend00/windows.txt "Intelligence"
# button X0 474 Y0 303 X1 632 Y1 333 -> center (553,318), SENDMESSAGE 1
# SENDPARAM1 14] so the game performs real shape blits (14intel.shp
# family), then advances turns with the banked End-Turn recipe while
# re-clicking intel every cycle (idempotent open; toggle-close risk is
# acceptable — ANY draw between checkpoints is what the t64 strict
# blit-input scan detects). Verification law: turn counter only for
# End-Turn; the intel click CANNOT be screen-verified (R13) — its effect
# is verified post-hoc by the RAM scan.
set -u
CKLOG="$OUT/ck.log"; TLOG="$OUT/turns.log"; CLICK="$OUT/cmd_click"
log() { echo "$(date +%H:%M:%S) $*" >> "$OUT/driver.log"; }
turn_now() { grep -oE 'turn [0-9]+' "$TLOG" 2>/dev/null | awk '{print $2}' | tail -1; }
wait_cmd() { local f="$1" i=0; while [ -f "$f" ] && [ $i -lt 14 ]; do sleep 2; i=$((i+1)); done; }
send_click() { printf '%s %s\n' "$1" "$2" > "$CLICK"; wait_cmd "$CLICK"; }

# phase 1: campaign entry
for i in $(seq 1 150); do
  grep -q "campaign phase done" "$OUT/click.log" 2>/dev/null && break
  sleep 4
done
grep -q "campaign phase done" "$OUT/click.log" || { log "FAIL: no campaign entry"; exit 1; }
T0=""; for i in $(seq 1 15); do T0=$(turn_now); [ -n "$T0" ] && break; sleep 4; done
log "entered; baseline turn=${T0:-none}"
[ -n "${T0:-}" ] || { log "FAIL: turn unreadable"; exit 1; }

# phase 2: open intel, wait one full ck interval, log
send_click 553 318; log "intel click sent (553,318)"
sleep 40

# phase 3: End-Turn acquire (BLOCKED t55 recipe bounded) then spin with
# intel re-click each cycle
GEO=""; TRIES=0
while [ $TRIES -lt 8 ]; do
  send_click 511 67; TRIES=$((TRIES+1))
  j=0
  while [ $j -lt 3 ]; do sleep 10; j=$((j+1)); t=$(turn_now); [ "${t:-0}" -gt "$T0" ] && break; done
  t=$(turn_now)
  if [ "${t:-0}" -gt "$T0" ]; then GEO="click"; T0=$t; log "ENDTURN acquired try $TRIES turn $t"; break; fi
  sleep 5
done
[ -n "$GEO" ] || log "EndTurn failed; continuing intel-only idle capture"
NADV=0
while [ $NADV -lt 12 ]; do
  send_click 553 318
  sleep 15
  send_click 511 67
  sleep 25
  t=$(turn_now)
  [ "${t:-0}" -gt "$T0" ] && { log "turn $t (intel redrawn)"; T0=$t; NADV=$((NADV+1)); }
done
log "t65 drive complete"
