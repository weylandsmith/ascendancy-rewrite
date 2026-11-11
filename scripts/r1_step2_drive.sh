#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

# t55 OUTER driver for r1_adcapture.sh — step-2 scripted sequence with
# banked-verification only (refuted route: scheduled UNVERIFIED in-game
# clicks, 2026-10-06c; every click here is verified by the turn counter).
#
# Requires: run dir exported as $OUT (the r1_adcapture.sh output dir).
# End-Turn geometry [verified extracted/ascend00/windows.txt NEXTTURN]:
# X0 474 Y0 52 X1 548 Y1 82 -> center (511,67) game-screen coords;
# game screen == xsend window frame for the golden title click (refcap law:
# root = window + 40, title button window (318,333) hit at game y 333), but
# the 640x480 in-game mapping is [unverified] -> two candidates tried in
# order with turn-advance verification: A=(511,67) top-origin,
# B=(511,413) bottom-origin mirror.
set -u
CKLOG="$OUT/ck.log"; TLOG="$OUT/turns.log"; CLICK="$OUT/cmd_click"; CKEP="$OUT/cmd_ck"; SHOT="$OUT/cmd_shot"
log() { echo "$(date +%H:%M:%S) $*" >> "$OUT/driver.log"; }

turn_now() { grep -oE 'turn [0-9]+' "$TLOG" 2>/dev/null | awk '{print $2}' | tail -1; }
ck_count() { wc -l < "$CKLOG" 2>/dev/null | tr -d ' '; }
wait_cmd() { # file consumed by inner 10s tick
  local f="$1" i=0
  while [ -f "$f" ] && [ $i -lt 14 ]; do sleep 2; i=$((i+1)); done
}
send_click() { printf '%s %s\n' "$1" "$2" > "$CLICK"; wait_cmd "$CLICK"; }

# phase 1: wait for campaign entry (grid-hash law inside the inner script)
for i in $(seq 1 120); do
  grep -q "campaign phase done" "$OUT/click.log" 2>/dev/null && break
  sleep 4
done
grep -q "campaign phase done" "$OUT/click.log" || { log "FAIL: no campaign entry"; exit 1; }
# first checkpoint lands AFTER phase-done; turns.log may lag (race hit t55 run 1)
T0=""
for i in $(seq 1 15); do T0=$(turn_now); [ -n "$T0" ] && break; sleep 4; done
log "entered; baseline turn=${T0:-none}"
[ -n "${T0:-}" ] || { log "FAIL: turn counter unreadable after 60s"; touch "$SHOT"; exit 1; }

# phase 2: acquire End-Turn per BLOCKED t55 recipe: (511,67) 25 s apart x8,
# then ONE key Return; B-frame once only if both above died.
GEO=""; TRIES=0
while [ $TRIES -lt 8 ]; do
  send_click 511 67; TRIES=$((TRIES+1))
  j=0
  while [ $j -lt 2 ]; do sleep 10; j=$((j+1)); t=$(turn_now); [ "${t:-0}" -gt "$T0" ] && break; done
  t=$(turn_now)
  if [ "${t:-0}" -gt "$T0" ]; then GEO="511 67"; T0=$t; log "ENDTURN acquired at (511,67) try $TRIES turn $t"; break; fi
  log "try $TRIES (511,67): no advance (turn=${t:-?})"
  sleep 5
done
if [ -z "$GEO" ]; then
  printf 'Return\n' > "$OUT/cmd_key"; wait_cmd "$OUT/cmd_key"
  j=0
  while [ $j -lt 4 ]; do sleep 10; j=$((j+1)); t=$(turn_now); [ "${t:-0}" -gt "$T0" ] && break; done
  t=$(turn_now)
  if [ "${t:-0}" -gt "$T0" ]; then GEO="KEY Return"; T0=$t; log "ENDTURN acquired via key Return turn $t"; fi
fi
[ -n "$GEO" ] || log "ALL EndTurn attempts failed (clicks x$TRIES + key); idle checkpoints only"

# phase 3: advance turns (dispatch click vs key by acquired GEO mode)
advance() {
  case "$GEO" in
    "KEY Return") printf 'Return\n' > "$OUT/cmd_key"; wait_cmd "$OUT/cmd_key" ;;
    *) send_click $GEO ;;
  esac
}
ADV=0
MAX_ADV="${MAX_ADV:-6}"
while [ $ADV -lt "$MAX_ADV" ]; do
  [ -n "$GEO" ] || break
  before=$T0
  advance
  j=0
  while [ $j -lt 8 ]; do sleep 10; j=$((j+1)); t=$(turn_now); [ "${t:-0}" -gt "$before" ] && break; done
  t=$(turn_now)
  if [ "${t:-0}" -gt "$before" ]; then ADV=$((ADV+1)); T0=$t; log "turn $before -> $t (adv $ADV)"; else log "stall at turn $t"; break; fi
done

# phase 4: screenshots + final checkpoint, exit
touch "$SHOT"; sleep 3; touch "$CKEP"
log "driver done; ck=$(ck_count) turns=$(grep -cE 'turn [0-9]+' "$TLOG" 2>/dev/null)"
exit 0
