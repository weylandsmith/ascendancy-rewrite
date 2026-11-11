#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

# r1_t272_wp.sh — t272 V-PRODUCER WATCHPOINT session launcher (scratch-only).
#
# WHY A SEPARATE LAUNCHER: scripts/r1_savestate.sh and r1_playcap_vnc.sh both
# touch shared state (r1savestate.sh literally `pkill -x dosbox-x`, which is the
# t267 production-kill footgun; vnc uses work/r1/game + work/r1/playcap). This
# session must coexist with the LIVE production game on :9 (pid recorded in
# work/r1/vnc/*.pid), so: own scratch tree, own ring dir, own display, kill by
# recorded PID ONLY, and a FIFO stdin so the debugger cannot EOF-spam (GOAL.txt
# R5 trap).
#
# Usage:
#   bash scripts/r1_t272_wp.sh prep     # scratch copy + conf + fifo (no launch)
#   bash scripts/r1_t272_wp.sh launch   # launch dosbox-x (needs prep)
#   bash scripts/r1_t272_wp.sh status   # pids + out tail + newest save
#   bash scripts/r1_t272_wp.sh stop     # kill tracked pids only
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WP="$ROOT/work/r1/wp-t272"
SCRATCH="$ROOT/work/r1/wp-t272/game"   # gate 3n2 wants /work/ literal; NEVER work/r1/game (production + user RESUME.GAM live there)
RING="$WP/save"                    # MEASURED: dosbox-x strips the last path component of captures= (r1_savestate.sh law); own ring (two-writer law, t266)
DISP="${DISPNO:-94}"               # production is :9
TL="${TL:-1200}"
CMDS="${1:-prep}"

mkdir -p "$WP" "$RING"

scratch_copy() {
  [ -f "$SCRATCH/ascend.exe" ] && { echo "scratch exists"; return 0; }
  mkdir -p "$SCRATCH/data" || return 2
  cp -a "$ROOT/game/." "$SCRATCH/" || return 2
  cp -a "$ROOT/extracted/ascend00/." "$SCRATCH/" 2>/dev/null
  cp -a "$ROOT/extracted/ascend02/data/." "$SCRATCH/data/" 2>/dev/null
  echo "scratch copied: $(du -sh "$SCRATCH" | cut -f1)"
}

write_conf() {
  cat > "$WP/wp.conf" <<EOF
[dosbox]
machine=svga_s3
memsize=16
captures=$WP/cap
autosave=10 41-60
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
  # variant that enters the debugger at program entry via the DOS internal
  # DEBUGBOX command (en_US.lng:2376-2382). -break-start is REFUTED: this build
  # accepts the switch and ignores it (t272, measured — game reached title screen).
  sed 's|^ASCEND.EXE|DEBUGBOX ASCEND.EXE|' "$WP/wp.conf" > "$WP/wp-dbg.conf"
  echo "conf=$WP/wp.conf (+ wp-dbg.conf)"
}

case "$CMDS" in
  prep)
    scratch_copy || exit 2
    write_conf
    [ -p "$WP/stdin.fifo" ] || mkfifo "$WP/stdin.fifo"
    echo "fifo=$WP/stdin.fifo disp=:$DISP tl=$TL"
    echo "NEXT: bash $0 launch"
    ;;
  launch)
    [ -f "$WP/wp.conf" ] || { echo "run prep first"; exit 2; }
    # tracked pids only — never pkill -x dosbox-x (kills production, t267)
    if [ -f "$WP/dosbox.pid" ] && kill -0 "$(cat "$WP/dosbox.pid")" 2>/dev/null; then
      echo "already running pid $(cat "$WP/dosbox.pid")"; exit 0
    fi
    Xvfb ":$DISP" -screen 0 800x600x24 >"$WP/xvfb.out" 2>&1 &
    echo $! > "$WP/xvfb.pid"
    sleep 1
    # hold the fifo open for writing so the debugger's stdin never EOFs
    ( exec sleep 100000 > "$WP/stdin.fifo" ) &
    echo $! > "$WP/hoder.pid"
    : > "$WP/dosbox.out"
    CONF="${CONF:-$WP/wp.conf}"
    BREAKFLAG=()
    [ "${BREAKSTART:-0}" = "1" ] && BREAKFLAG=(-break-start)
    DISPLAY=":$DISP" nohup dosbox-x -conf "$CONF" $GUIFLAG "${BREAKFLAG[@]}" \
      -time-limit "$TL" < "$WP/stdin.fifo" >> "$WP/dosbox.out" 2>&1 &
    echo $! > "$WP/dosbox.pid"
    echo "launched pid $(cat "$WP/dosbox.pid") disp=:$DISP tl=$TL breakstart=${BREAKSTART:-1}"
    ;;
  status)
    for p in xvfb hoder dosbox; do
      if [ -f "$WP/$p.pid" ] && kill -0 "$(cat "$WP/$p.pid")" 2>/dev/null; then
        echo "$p ALIVE $(cat "$WP/$p.pid")"
      else echo "$p dead"; fi
    done
    echo "--- dosbox.out tail ---"; tail -c 600 "$WP/dosbox.out" 2>/dev/null
    echo "--- newest saves ---"
    find "$RING" -name '*.sav' -printf '%T@ %p\n' 2>/dev/null | sort -g | tail -3
    ;;
  stop)
    for p in dosbox hoder xvfb; do
      [ -f "$WP/$p.pid" ] && kill "$(cat "$WP/$p.pid")" 2>/dev/null && echo "killed $p $(cat "$WP/$p.pid")"
    done
    ;;
  *) echo "unknown cmd"; exit 2;;
esac
