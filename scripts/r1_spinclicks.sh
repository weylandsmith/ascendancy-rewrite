#!/usr/bin/env bash
# r1_spinclicks.sh — fixed-cadence End-Turn clicker for the tail of an r1ad run.
# Motivation (t58): r1_step2_drive.sh phase 3 waits <=80 s per advance and
# stalls when turn resolution is slower; the inner capture keeps
# checkpointing and the game keeps moving, so the tail wants a dumb cadence,
# not a strict state machine. Turn law = SAME as the banked driver: max
# 'turn N' in $OUT/turns.log (inner-maintained; pointer law untouched).
# End-Turn law (t56): (511,67) works-but-flaky. If the counter sits still
# for STALL readings, fire ONE key Return (t55 recipe), then keep clicking.
# Stops when $OUT/cmd_stop appears or r1_adcapture.sh dies.
set -u
OUT="${OUT:?OUT required}"
DISP="${DISPNO:-93}"
CADENCE="${CADENCE:-25}"
STALL="${STALL:-6}"

turn_now() { grep -oE 'turn [0-9]+' "$OUT"/turns.log 2>/dev/null | awk '{print $2}' | sort -n | tail -1; }

prev=""; same=0; key_done=0; n=0
while pgrep -f "r1_adcapture.sh" >/dev/null && [ ! -f "$OUT/cmd_stop" ]; do
  printf '511 67\n' > "$OUT/cmd_click"
  sleep "$CADENCE"
  t=$(turn_now)
  n=$((n+1))
  echo "$(date +%T) click $n turn=${t:-?}" >> "$OUT/spin.log"
  case "$t" in
    ""|*[!0-9]*) continue ;;
  esac
  if [ -n "$prev" ] && [ "$t" = "$prev" ]; then
    same=$((same+1))
    if [ "$same" -ge "$STALL" ] && [ "$key_done" -eq 0 ]; then
      printf 'Return\n' > "$OUT/cmd_key"
      key_done=1
      echo "$(date +%T) stalled $same readings -> ONE key Return" >> "$OUT/spin.log"
    fi
  else
    same=0
  fi
  prev="$t"
done
echo "$(date +%T) spinner done (clicks=$n last turn=${prev:-?})" >> "$OUT/spin.log"
