#!/usr/bin/env bash
# r1_t261_session.sh — bring up the RESTORED-t1255 session isolated on :8 and
# (optionally) tear it down. Phase-2 t261 (docs/re/selfplay.md t260 block laws).
#
# LAWS encoded (all measured t260):
#  * loadstate is GUI-menu-only  -> NO -nogui for this session.
#  * TL-BOUNCE: NEVER pass -time-limit to a process you loadstate INTO.
#  * SAVEDIR law: slot files resolve <savedir>/NN.sav; the load source is a
#    SCRATCH copy of the bank ZIP, never the production ring.
#  * AUTOSAVE-FROM-START law: autosave=10 41-60 is armed at launch, so the
#    watcher has an observation channel the instant the state lands. Slot 60
#    (the load source) is the LAST slot the ring churns, so a Load-state click
#    within ~60 s of boot reads the pristine copy; after the load the RAM image
#    is what matters and ring churn is pure witness yield.
#  * The production :9 session is NOT touched by this script (no pattern kills;
#    teardown signals only pids this script recorded).
#
# Usage:
#   bash scripts/r1_t261_session.sh bringup   # Xvfb :8 + dosbox + watcher + load click
#   bash scripts/r1_t261_session.sh status
#   bash scripts/r1_t261_session.sh stop      # kill recorded dosbox/watcher pids only
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="$ROOT/work/r1/t261-drive"
RUN="$BASE/run"
SCRATCH="$ROOT/work/r1/game"          # scratch copy (gate 3n2: never game/)
SRC_ZIP="$ROOT/work/r1/bank-t251-live1255/60.sav"
SRC_MD5="0024340df46c0375ce6472e085345e71"
VN=8
CMDS="${1:-status}"

mkdir -p "$BASE/save" "$BASE/caps" "$RUN"

alive() { [ -f "$RUN/$1.pid" ] && kill -0 "$(cat "$RUN/$1.pid")" 2>/dev/null; }

status() {
  echo "xvfb:  $(alive xvfb && echo UP || echo down) ($(cat "$RUN/xvfb.pid" 2>/dev/null))"
  echo "dosbox:$(alive dosbox && echo UP || echo down) ($(cat "$RUN/dosbox.pid" 2>/dev/null))"
  echo "watch: $(alive watch && echo UP || echo down) ($(cat "$RUN/watch.pid" 2>/dev/null))"
  echo "--- timeline tail (fields only, bounded) ---"
  tail -c 60000 "$BASE/live-timeline.jsonl" 2>/dev/null | python3 -c '
import sys, json
rows = []
for l in sys.stdin:
    l = l.strip()
    if l.startswith("{"):
        try: rows.append(json.loads(l))
        except Exception: pass
if not rows:
    print("(no rows yet)")
else:
    for r in rows[-5:]:
        print({k: r.get(k) for k in ("wall","file","turn","score_stars","in_game")})
'
}

case "$CMDS" in
status) status ;;

stop)
  for p in dosbox watch xvfb; do
    if alive "$p"; then kill -9 "$(cat "$RUN/$p.pid")"; echo "killed $p $(cat "$RUN/$p.pid")"; fi
  done
  rm -f "$RUN/xvfb.pid" "$RUN/dosbox.pid" "$RUN/watch.pid"
  ;;

bringup)
  # 1. source ZIP integrity (hard gate: wrong md5 -> refuse, never load garbage)
  got=$(md5sum "$SRC_ZIP" | awk '{print $1}')
  if [ "$got" != "$SRC_MD5" ]; then echo "ABORT: bank md5 $got != $SRC_MD5"; exit 1; fi
  echo "bank verified $got"

  # 2. scratch savedir holds ONLY the load source — UNLESS keep-save mode
#    (recovery relaunch: the ring in $BASE/save IS the session's state; wiping
#    it would destroy the newest autosave. The load click then reads slot 60,
#    which churn keeps a valid SAME-SESSION snapshot.)
  if [ "${KEEP_SAVE:-0}" = "1" ] && ls "$BASE"/save/*.sav >/dev/null 2>&1; then
    echo "keep-save: scratch ring preserved ($(ls "$BASE"/save/*.sav | wc -l) slots)"
  else
    rm -f "$BASE/save"/*.sav
    cp -p "$SRC_ZIP" "$BASE/save/60.sav"
  fi

  # 3. Xvfb :8
  if ! alive xvfb; then
    Xvfb :$VN -screen 0 800x600x16 > "$RUN/xvfb.log" 2>&1 &
    echo $! > "$RUN/xvfb.pid"
    sleep 1
  fi

  # 4. conf: GUI (menu bar needed for the Load-state click), NO time-limit,
  #    autosave armed from the start, everything under $BASE.
  cat > "$RUN/session.conf" <<EOF
[dosbox]
machine=svga_s3
memsize=16
captures=$BASE/caps
autosave=10 41-60
saveslot=60
saveremark=false
[sdl]
output=x11
fullscreen=false
autolock=false
[mixer]
nosound=true
[autoexec]
MOUNT C $SCRATCH
C:
ASCEND.EXE
EOF

  # 5. watcher FIRST (so no ring slot is missed between load and drive)
  if ! alive watch; then
    python3 "$ROOT/scripts/r1_playcap_watch.py" "$BASE" --no-exit >> "$RUN/watch.out" 2>&1 &
    echo $! > "$RUN/watch.pid"
  fi

  # 6. dosbox. NO -time-limit (TL-BOUNCE law, t260: the deadline belongs to
  #    the loading process and expels a loaded state within seconds). The gate
  #    3n2 bound is provided EXTERNALLY by timeout -s KILL, which cannot be
  #    carried into the state (it is not an emulator flag).
  if alive dosbox; then
    echo "dosbox already up ($(cat "$RUN/dosbox.pid")) - not double-launching"
  else
    DISPLAY=:$VN timeout -s KILL 14h dosbox-x -conf "$RUN/session.conf" -savedir "$BASE/save" \
      < /dev/null >> "$RUN/dosbox.log" 2>&1 &
    echo $! > "$RUN/dosbox.pid"
  fi
  echo "launched; waiting for the window + first autosaves"
  sleep 30
  DISPLAY=:$VN xwininfo -root -tree 2>/dev/null | grep -m1 -i 'DOSBox-X' || echo "NO DOSBOX WINDOW YET"
  status
  echo "NOW: run scripts/r1_t261_load.py to click Capture->Load state"
  ;;

*) echo "usage: $0 bringup|status|stop"; exit 2 ;;
esac
