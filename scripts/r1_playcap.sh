#!/usr/bin/env bash
# r1_playcap.sh — USER-FACED original-game capture session (t82).
#
# PURPOSE: the three remaining user-level blocks (OQ-021 victory selector,
# OQ-023 relation-state enum, OQ-010 combat application) all close from ONE
# played session of the ORIGINAL game with the autosave ring running:
#   play a few turns, colonize past half the galaxy, declare war / make
#   peace, fight ONE battle, then quit normally (or let the time-limit end).
# The slot ring under $OUT/save is the evidence; an offline analyzer (this
# script's tail, or scripts/r1_t75_read.py + relation/ship diffs) reads it.
# NOTHING is scripted: no injection, no synthetic clicks — real play only.
#
# SAFETY (docs/BLOCKED.md invariants): runs ONLY against the scratch copy
# work/r1/game (game/ is never mounted); -time-limit hard bound (generous
# default, override TL=seconds); pkill -x dosbox-x only; bounded output dir.
# This session is INTERACTIVE by design (you watch the screen); the
# headless-invariant applies to the agent's automated capture runs, not to
# a human playing on their own display.
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRATCH="$ROOT/work/r1/game"
OUT="$ROOT/work/r1/playcap-$(date +%Y%m%d-%H%M%S)"
TL="${TL:-1500}"                       # seconds of play; default 25 min
# DISPLAY (t111 fix): this host has NO :0 at all — /tmp/.X11-unix holds a
# single socket (X9), fronted by x11vnc on localhost:5910. The old default
# ":0" made a bare invocation die inside dosbox with zero slots and no
# diagnostic, which is why the capture sessions never landed despite VNC
# clients connecting. Respect an explicit DISPLAY; otherwise AUTO-DETECT the
# first local socket that actually answers, and never guess a number.
if [ -z "${DISPLAY:-}" ]; then
  for s in /tmp/.X11-unix/X*; do
    [ -S "$s" ] || continue
    d=":${s##*/X}"
    if DISPLAY="$d" timeout 5 xdpyinfo >/dev/null 2>&1; then DISPLAY="$d"; break; fi
    DISPLAY=""
  done
  [ -n "$DISPLAY" ] || { echo "playcap: no answering X display (sockets: $(ls /tmp/.X11-unix 2>/dev/null | tr '\n' ' ')) — start Xvfb+x11vnc or pass DISPLAY=..."; exit 2; }
fi
command -v dosbox-x >/dev/null || { echo "dosbox-x not found"; exit 2; }
[ -f "$SCRATCH/ascend.exe" ] || { echo "scratch build missing"; exit 2; }
mkdir -p "$OUT/save"

cleanup() { pkill -x dosbox-x 2>/dev/null || true; }
trap cleanup EXIT

CONF="$OUT/playcap.conf"
cat > "$CONF" <<EOF
[dosbox]
machine=svga_s3
memsize=16
captures=$OUT/caps
autosave=10 41-60
saveremark=false
[sdl]
output=x11
fullscreen=false
autolock=false
[mixer]
nosound=false
[autoexec]
MOUNT C $SCRATCH
C:
ASCEND.EXE
EOF

echo "playcap: scratch=$SCRATCH out=$OUT TL=${TL}s display=$DISPLAY"
echo "playcap: autosave ring 41-60 (10 s host-clock cadence law — a slot is"
echo "         overwritten ~200 s after it lands; the live watcher below"
echo "         parses each slot the moment it appears)."
echo "playcap: to close OQ-021 colonize past 50% of stars (T=50 -> 26)."
echo "playcap: to close OQ-023 declare war AND propose/join alliance, then End Turn."
echo "playcap: to close OQ-010 let two fleets exchange fire once, then End Turn."
DISPLAY="$DISPLAY" timeout -s KILL $((TL + 30)) dosbox-x -conf "$CONF" -nogui \
  -time-limit "$TL" >"$OUT/dosbox.out" 2>&1 &
DB=$!
# LIVE collector (t85): parses every new slot into $OUT/live-timeline.jsonl
# while you play; exits by itself ~5 s after dosbox-x is gone.
(cd "$ROOT" && python3 scripts/r1_playcap_watch.py "$OUT" >"$OUT/watch.out" 2>&1) &
WATCH=$!
wait $DB || true
sleep 8
kill "$WATCH" 2>/dev/null || true

SLOTS=$(ls "$OUT/save"/*.sav 2>/dev/null | wc -l)
echo "playcap: slots captured = $SLOTS"
if [ "$SLOTS" -gt 0 ]; then
  # instant offline readout (t85: shared r1_slot layer; v1 read DAT_00016143
  # as u16-then->>16, which is ALWAYS 0; selector now BYTE per score.md)
  (cd "$ROOT" && python3 scripts/r1_slot.py "$OUT") || echo "playcap: offline analyzer hit an issue; slots still banked for offline work"
  echo "playcap: OQ closeouts run these from $ROOT:"
  echo "  python3 scripts/r1_t85_victory.py  $OUT   # OQ-021 threshold"
  echo "  python3 scripts/r1_t85_relation.py $OUT   # OQ-023 state enum"
  echo "  python3 scripts/r1_t85_combat.py   $OUT   # OQ-010 battle evidence"
fi
echo "playcap: done. Evidence lives in $OUT — tell the assistant this path."
