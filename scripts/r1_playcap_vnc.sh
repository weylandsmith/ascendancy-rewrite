#!/usr/bin/env bash
# r1_playcap_vnc.sh — RESUMABLE played-session harness (t85 redesign).
#
# WHY REDESIGNED: the t85 incident — TL=1500 killed the user's game
# mid-sitting. Ascendancy is played over HOURS across sittings, so:
#   * Xvfb + x11vnc are daemon-like and PERSIST across ssh logouts.
#   * Each 'start' launches ONE dosbox session that resumes the in-game
#     save (title menu "Return to Current Game"; game writes RESUME.GAM).
#   * Evidence dir work/r1/playcap ACCUMULATES across sittings; the
#     watcher dedups by (slot,mtime), so restarting mid-session is free.
#   * NO wall-clock play cap. -time-limit stays (BLOCKED.md runbook) as a
#     RUNAWAY guard only: TL=172800 default (48 h — t277 raised it from
#     28800; see the TL line). End a sitting in-game (Save,
#     then quit) or via this script's 'stop'.
#
# VNC: loopback only (-localhost == -allow 127.0.0.1); auth boundary is the
# SSH tunnel. x11vnc: SYSTEM binary or the sudo-free extraction under
# work/r1/localdeb. Kill model: tracked PIDs only (never pattern-kills;
# pgrep -x adoption below records pids but never signals by pattern).
#
# Usage:
#   bash scripts/r1_playcap_vnc.sh            # start or reattach
#   bash scripts/r1_playcap_vnc.sh status     # what's alive + live progress
#   bash scripts/r1_playcap_vnc.sh analyze    # analyzers on accumulated data
#   bash scripts/r1_playcap_vnc.sh stop       # end dosbox sitting (+analyze)
#   bash scripts/r1_playcap_vnc.sh --stop     # stop + tear down VNC stack
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEB="$ROOT/work/r1/localdeb"
RUNDIR="$ROOT/work/r1/vnc"
OUT="$ROOT/work/r1/playcap"
PORT="${PORT:-5910}"
VN="${VN:-9}"
GEOM="${RES:-800x600x16}"
SCRATCH="$ROOT/work/r1/game"
# t277 MEASURED (docs/re/selfplay.md t277 block F1): 18 of 33 logged :9
# sessions died at 28810-28820 s wall with exactly TL/CADENCE = 28800/10 =
# 2880 autosaves banked — the ring save count IS the -time-limit counter.
# The "unexplained" Nov-1 15:45 and Nov-2 07:04 deaths were 28800 s expiries,
# and dosbox-x logs NO farewell line on that exit (golden witness:
# work/r1/selftest-t111-playcap/dosbox.out, TL=90, ends `Active save slot: 1
# [Empty]` at EOF). A guard that fires mid-sitting is worse than a late one,
# so the runaway bound is 48 h: longer than any realistic sitting, still a
# hard stop for a forgotten process. Override with TL=<seconds>.
TL="${TL:-172800}"                    # runaway guard (48 h, t277), NOT a play cap
CMDS="${1:-start}"

XV_BIN="$(command -v x11vnc 2>/dev/null || true)"
XV_LIB=""
if [ -z "$XV_BIN" ] && [ -x "$DEB/root/usr/bin/x11vnc" ]; then
  XV_BIN="$DEB/root/usr/bin/x11vnc"
  XV_LIB="$DEB/root/usr/lib/x86_64-linux-gnu"
fi
mkdir -p "$RUNDIR" "$OUT/save" "$OUT/caps"

alive() { [ -f "$RUNDIR/$1.pid" ] && kill -0 "$(cat "$RUNDIR/$1.pid")" 2>/dev/null; }

analyze() {
  echo "=== progress timeline (accumulated across sittings; $OUT) ==="
  (cd "$ROOT" && python3 scripts/r1_slot.py "$OUT") || true
  echo "=== OQ-021 victory threshold ==="
  (cd "$ROOT" && python3 scripts/r1_t85_victory.py "$OUT") || true
  echo "=== OQ-023 relation-state enum ==="
  (cd "$ROOT" && python3 scripts/r1_t85_relation.py "$OUT") || true
  echo "=== OQ-010 combat evidence ==="
  (cd "$ROOT" && python3 scripts/r1_t85_combat.py "$OUT") || true
}

stop_dosbox() {
  if alive dosbox; then
    kill "$(cat "$RUNDIR/dosbox.pid")" 2>/dev/null || true   # TERM = graceful
    for _ in 1 2 3 4 4 4 4 4 4 4; do
      alive dosbox || break
      sleep 1
    done
    kill -9 "$(cat "$RUNDIR/dosbox.pid")" 2>/dev/null || true
    echo "harness: dosbox sitting ended"
  else
    echo "harness: no dosbox sitting running"
  fi
  rm -f "$RUNDIR/dosbox.pid"
  sleep 7                                  # let the watcher flush last slots
  if alive watch; then kill "$(cat "$RUNDIR/watch.pid")" 2>/dev/null || true; fi
  rm -f "$RUNDIR/watch.pid"
}

teardown() {
  for p in x11vnc xvfb; do
    if alive "$p"; then kill "$(cat "$RUNDIR/$p.pid")" 2>/dev/null || true; fi
    rm -f "$RUNDIR/$p.pid"
  done
  echo "harness: VNC stack torn down"
}

case "$CMDS" in
  status)
    for p in xvfb x11vnc dosbox watch; do
      if alive "$p"; then echo "$p: RUNNING (pid $(cat "$RUNDIR/$p.pid"))"
      else echo "$p: not running"; fi
    done
    # t267: full health pass (game pid + TL expiry + watcher census + ring
    # freshness). Exit code intentionally not propagated to status.
    python3 "$ROOT/scripts/r1_game_health.py" || true
    [ -f "$OUT/live-timeline.jsonl" ] && echo "timeline: $(wc -l < "$OUT/live-timeline.jsonl") observations banked"
    echo "--- last banked state (10 s cadence law) ---"
    grep -vE 'PROCESS ERROR' "$OUT/watch.out" 2>/dev/null | tail -n 4 || true
    exit 0 ;;
  analyze) analyze; exit 0 ;;
  stop)    stop_dosbox; analyze; exit 0 ;;
  --stop)  stop_dosbox; analyze; teardown; exit 0 ;;
  start) ;;
  *) echo "usage: $0 [start|status|analyze|stop|--stop]"; exit 2 ;;
esac

command -v dosbox-x >/dev/null || { echo "dosbox-x not found"; exit 2; }
[ -f "$SCRATCH/ascend.exe" ] || { echo "scratch build missing"; exit 2; }

# ---- Xvfb (persist; adopt orphans by exact comm name, never signal them) ----
if [ ! -e "/tmp/.X11-unix/X$VN" ]; then
  Xvfb ":$VN" -screen 0 "$GEOM" -nolisten tcp >"$RUNDIR/xvfb.log" 2>&1 &
  echo $! > "$RUNDIR/xvfb.pid"
  sleep 2
else
  echo "harness: reusing display :$VN"
  if ! alive xvfb; then
    _o="$(pgrep -xn Xvfb || true)"; [ -n "$_o" ] && echo "$_o" > "$RUNDIR/xvfb.pid"
  fi
fi
[ -e "/tmp/.X11-unix/X$VN" ] || { echo "harness: Xvfb failed (see $RUNDIR/xvfb.log)"; exit 2; }

# ---- x11vnc (persist; port already open => adopt existing listener) ----
if ! alive x11vnc; then
  if ss -tln 2>/dev/null | grep -q ":$PORT "; then
    _o="$(pgrep -x x11vnc || true)"
    [ -n "$_o" ] && { echo "$_o" > "$RUNDIR/x11vnc.pid"; echo "harness: adopted existing x11vnc (pid $_o) on $PORT"; }
  fi
fi
if ! alive x11vnc; then
  [ -n "$XV_BIN" ] || { echo "harness: no x11vnc (system or $DEB)"; exit 2; }
  PASS_ARGS=(-nopw)
  [ -n "${VNPW:-}" ] && PASS_ARGS=(-passwd "$VNPW")
  LD_LIBRARY_PATH="${XV_LIB:+$XV_LIB:}${LD_LIBRARY_PATH:-}" \
    "$XV_BIN" -display ":$VN" -localhost -forever -shared \
    -rfbport "$PORT" "${PASS_ARGS[@]}" -noxdamage \
    >"$RUNDIR/x11vnc.log" 2>&1 &
  echo $! > "$RUNDIR/x11vnc.pid"
  sleep 2
fi
ss -tln 2>/dev/null | grep -q ":$PORT " || { echo "harness: nothing listening on $PORT — $RUNDIR/x11vnc.log"; exit 2; }

if alive dosbox; then
  echo "harness: dosbox sitting ALREADY RUNNING (pid $(cat "$RUNDIR/dosbox.pid")) — tunnel verified, nothing new launched."
else
  # t267 ADOPTION GUARD (t261 collision class ROOT): if dosbox.pid was lost
  # while a harness dosbox still runs, 'alive dosbox' says false and the old
  # code launched a SECOND game on the same ring — which is how the t261
  # stray wrote production's slots. Never launch when a harness-launched
  # dosbox-x (cmdline carries $RUNDIR/session.conf) is in /proc; record it.
  _adopt=""
  for _c in $(pgrep -x dosbox-x 2>/dev/null || true); do
    if tr '\0' ' ' < "/proc/$_c/cmdline" 2>/dev/null | grep -q "$RUNDIR/session.conf"; then
      _adopt="$_c"; break
    fi
  done
  if [ -n "$_adopt" ]; then
    echo "$_adopt" > "$RUNDIR/dosbox.pid"
    echo "harness: ADOPTED live dosbox pid $_adopt (pid file was lost) — nothing launched"
    python3 "$ROOT/scripts/r1_watch_reaper.py" "$OUT" --keep 1 || true
    if ! pgrep -f "r1_playcap_watch.py $OUT" >/dev/null 2>&1; then
      setsid bash -c "cd '$ROOT' && python3 scripts/r1_playcap_watch.py '$OUT' --no-exit >>'$OUT/watch.out' 2>&1" \
        < /dev/null > /dev/null 2>&1 &
      sleep 1; echo $! > "$RUNDIR/watch.pid"
      echo "harness: watcher launched for adopted session"
    fi
  else
  # t85b REAPER: every sitting's 'setsid ... watch &' left its watcher alive
  # (--no-exit + the dosbox-alive check kept old ones looping for days; the
  # single watch.pid file only tracked the NEWEST). Twelve concurrent
  # watchers on $OUT banked 73k duplicate rows and interleaved the streams.
  # Kill model preserved: only PIDs we recorded in $RUNDIR/watch*.pid, and
  # only after /proc comm+args confirms it is OUR r1_playcap_watch.py on $OUT
  # (never a blind pattern-kill).
  for pf in "$RUNDIR"/watch*.pid; do
    [ -f "$pf" ] || continue
    _wp="$(cat "$pf" 2>/dev/null || true)"
    if [ -n "$_wp" ] && kill -0 "$_wp" 2>/dev/null \
       && tr '\0' ' ' < "/proc/$_wp/cmdline" 2>/dev/null | grep -q "r1_playcap_watch.py $OUT"; then
      kill "$_wp" 2>/dev/null || true
      echo "harness: reaped stale watcher pid $_wp"
    fi
    rm -f "$pf"
  done
  # t267: pid files miss watchers whose starting session never recorded (or
  # whose file was overwritten by the next start) — MEASURED 3 live writers
  # with dup-row amplification on the timeline. /proc census catches the rest.
  # --keep 0: dosbox is dead here, so EVERY surviving watcher is stale; the
  # fresh one launches below. (keep>=1 would spare the newest stale watcher
  # and immediately recreate the two-writer class.)
  python3 "$ROOT/scripts/r1_watch_reaper.py" "$OUT" --keep 0 || true
  CONF="$RUNDIR/session.conf"
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
  # setsid: survives this terminal; only 'stop' (or in-game quit) ends it.
  setsid env DISPLAY=":$VN" timeout -s KILL $((TL + 30)) \
    dosbox-x -conf "$CONF" -nogui -time-limit "$TL" \
    < /dev/null >>"$RUNDIR/dosbox.log" 2>&1 &
  sleep 1
  _d="$(pgrep -nx dosbox-x || true)"
  [ -n "$_d" ] && echo "$_d" > "$RUNDIR/dosbox.pid" || echo "harness: WARNING dosbox did not start (see $RUNDIR/dosbox.log)"
  setsid bash -c "cd '$ROOT' && python3 scripts/r1_playcap_watch.py '$OUT' --no-exit >>'$OUT/watch.out' 2>&1" \
    < /dev/null > /dev/null 2>&1 &
  sleep 1
  echo $! > "$RUNDIR/watch.pid"
  # t267 BRING-UP-VERIFY (queue spec: ring row must land within 30 s of
  # start). Poll the ring's newest mtime; the 10 s cadence law means a live
  # stack lands a NEW row each 10 s — an unchanged mtime for 30 s means the
  # watcher or the guest autosave is not running. Never reads the timeline.
  _bu_ok=0
  _bu_t0=$(date +%s)
  while [ $(( $(date +%s) - _bu_t0 )) -lt 30 ]; do
    _bu_newest=$(find "$OUT/save" -name '*.sav' -newermt "-30 seconds" 2>/dev/null | head -1)
    if [ -n "$_bu_newest" ]; then _bu_ok=1; break; fi
    sleep 3
  done
  if [ "$_bu_ok" = 1 ]; then
    echo "harness: BRINGUP OK (ring row landed within 30 s: $(basename "$_bu_newest"))"
  else
    echo "harness: BRINGUP FAIL — no ring row within 30 s; run: python3 scripts/r1_game_health.py"
  fi
  fi
fi

cat <<EOF
============================================================
PLAYCAP READY — view from your workstation:
    ssh -L $PORT:localhost:$PORT hrethric@$(hostname -I | awk '{print $1}')
    then any VNC viewer -> localhost:$PORT

RESUME: if the game is at its title menu, click "Return to Current
Game" (top option). ALWAYS use in-game Save before ending a sitting —
that is what persists across restarts; the dosbox save-state ring is
EVIDENCE only, not a resume mechanism.

GALAXY: choose AVERAGE (the default — do not click GALAXY_MORE) = 50
stars. Thresholds at T=50: vendor-comment victory at 26 systems
(score 52%); vendor-prose 2/3 at 34 (score 68%). Watch the terminal
pane or 'status' — the banked line prints score=<owned>/50 every 10 s.

EVENTS THIS CAPTURE NEEDS (any number of sittings):
  OQ-021  own >=26 of 50 systems; cross 26 and keep playing 2 min
  OQ-023  declare war once AND propose/accept an alliance, End Turn
  OQ-010  two enemy fleets exchange fire once, then End Turn
  BETWEEN events: End Turn and let >=15 s pass (10 s autosave law)

END SITTING: in-game Save, then either close nothing (game idles at
title harmlessly) or on the VM:
    bash scripts/r1_playcap_vnc.sh stop     # runs analyzers too
ANALYZE ANYTIME:
    bash scripts/r1_playcap_vnc.sh analyze
============================================================
EOF
