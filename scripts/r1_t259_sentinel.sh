#!/usr/bin/env bash
# r1_t259_sentinel.sh — one-call census for the WAIT-TRIGGER sentinel (t259).
# WHY: t259 measured that the parked :9 game DIED unattributed at 15:45:08
# (docs/re/_wip_t259.md). The old sentinel premises ("the ring keeps banking",
# "trigger A structurally always armed while the watcher lives") are FALSE.
# Re-arm adjudication is now: game-alive first, watcher second. Keep this
# script's output TINY (rows are 4-28 KB; never print raw timeline lines —
# t259 context-law incident).
# Read-only. Prints one line per check + a verdict line. Exit 0 always.
cd "$(dirname "$0")/.." || exit 0
TL="work/r1/playcap/live-timeline.jsonl"

# 1. GAME ALIVE (authoritative: pgrep -x, not the pidfile — pidfiles are
#    stale by design; t259 measured dosbox.pid pointing at a dead pid).
if pgrep -x dosbox-x >/dev/null 2>&1; then
  echo "game: ALIVE ($(pgrep -x dosbox-x | tr '\n' ' '))"
else
  echo "game: DEAD"
fi

# 2. TIMELINE heartbeat
if [ -f "$TL" ]; then
  age=$(( $(date +%s) - $(stat -c %Y "$TL") ))
  echo "timeline: size=$(stat -c %s "$TL") mtime_age=${age}s"
else
  echo "timeline: MISSING"
fi

# 3. WITNESS scan (V>=25 or selector arm) over the last 400 KB, byte-capped.
if [ -f "$TL" ]; then
  w=$(tail -c 400000 "$TL" | grep -cE '"selector_byte": [1-9]|"score_stars": (2[5-9]|[3-9][0-9])')
  echo "witness_rows_tail400k: $w"
fi

# 4. USER SITTING: a new playcap-* dir is the ONLY sitting signal (t247 law).
pc=$(ls -d work/r1/playcap/playcap-* 2>/dev/null | wc -l)
echo "playcap_dirs: $pc"

# 5. WATCHER census (writerhood = open fd, t215 law) — count only.
n=0
for p in $(pgrep -f 'r1_playcap_watch.py' 2>/dev/null); do
  for fd in /proc/$p/fd/*; do
    tgt=$(readlink "$fd" 2>/dev/null) || continue
    case "$tgt" in *live-timeline.jsonl) n=$((n+1)); break;; esac
  done
done
echo "watchers_with_timeline_fd: $n"

# 6. Banks + user-save integrity (never overwrite RESUME.GAM).
echo "resume_md5: $(md5sum work/r1/game/RESUME.GAM 2>/dev/null | cut -c1-12) (expect 5b382afbb789 = user-oct29 copy)"

# 7. Ring newest (the only copy of unsaved turn states, t251 law).
echo "ring_newest: $(ls -t work/r1/playcap/save/*.sav 2>/dev/null | head -1) $(stat -c '%y %s' "$(ls -t work/r1/playcap/save/*.sav 2>/dev/null | head -1)" 2>/dev/null | cut -c1-19)"

# Verdict lines are advisory; a human/next session reads them, never greps them.
if ! pgrep -x dosbox-x >/dev/null 2>&1; then
  echo "VERDICT: witness pipeline DARK (game dead) — passive trigger A is IMPOSSIBLE until a relaunch decision (BLOCKED.md t259 addendum)."
fi
