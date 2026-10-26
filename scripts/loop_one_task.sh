#!/usr/bin/env bash
# One task per session, forever. Each iteration spawns a FRESH hermes process
# (new context, no compaction), which must complete exactly one task, write its
# findings to disk, and exit. The loop then verifies and starts the next task.
#
# Usage:
#   bash scripts/loop_one_task.sh              # run forever
#   MAX_ITERS=6 bash scripts/loop_one_task.sh  # stop after 6 tasks
#   DRYRUN=1 bash scripts/loop_one_task.sh     # verify wiring, no model calls
#   bash scripts/loop_one_task.sh --status     # where is the loop at?
# Stop: Ctrl-C (finishes the current iteration first), or:
#   touch work/r1/loop/STOP   (checked between iterations)
#
# Why not /goal in one tmux session: a single long-lived session keeps grinding
# in the same context, so it chains task after task through compaction cycles.
# Scheduling belongs OUTSIDE the model — this script is the scheduler.
set -uo pipefail          # NOT -e: a failing iteration must not kill the loop
cd "$(dirname "$0")/.."
ROOT="$PWD"
LOOPDIR="work/r1/loop"
mkdir -p "$LOOPDIR"
MAX_ITERS="${MAX_ITERS:-0}"          # 0 = unlimited
MAX_TURNS="${MAX_TURNS:-80}"         # hard cap per session
RUN_BUDGET="${RUN_BUDGET:-2700}"     # 45 min per task
COOLDOWN="${COOLDOWN:-15}"           # seconds between iterations
CONTRACT="docs/TASK_CONTRACT.txt"

log() { echo "[$(date '+%F %T')] $*"; }

if [ "${1:-}" = "--status" ]; then
  echo "iterations run : $(wc -l < "$LOOPDIR/journal.tsv" 2>/dev/null || echo 0)"
  echo "stop flag      : $([ -f "$LOOPDIR/STOP" ] && echo PRESENT || echo absent)"
  echo "next action    : $(awk '/^#+ *NEXT ACTION/{f=1;next} f&&NF{print;exit}' docs/STATE.md)"
  echo "last 5 journal :"
  tail -5 "$LOOPDIR/journal.tsv" 2>/dev/null | sed 's/^/  /' || echo "  (none)"
  exit 0
fi

[ -f "$CONTRACT" ] || { echo "missing $CONTRACT"; exit 1; }
command -v hermes >/dev/null || { echo "hermes not on PATH"; exit 1; }

i=0
while :; do
  i=$((i+1))
  [ "$MAX_ITERS" -gt 0 ] && [ "$i" -gt "$MAX_ITERS" ] && { log "MAX_ITERS reached"; i=$((i-1)); break; }
  [ -f "$LOOPDIR/STOP" ] && { log "STOP flag present — exiting"; break; }

  # Pre-flight: never start an iteration from a red tree.
  if ! bash scripts/gate.sh > "$LOOPDIR/preflight_gate.log" 2>&1; then
    log "iter $i: GATE RED before start — not launching. See $LOOPDIR/preflight_gate.log"
    sleep 60; continue
  fi

  next=$(awk '/^#+ *NEXT ACTION/{f=1;next} f&&NF{print;exit}' docs/STATE.md)
  log "iter $i: NEXT = ${next:-<unparsed>}"

  out="$LOOPDIR/iter-$(date +%Y%m%d-%H%M%S)-$i.log"
  # Steering hook: if LOOPSTEER.txt exists, its contents replace the task text
  # for THIS iteration only (then get archived, so it can't go stale).
  { cat "$CONTRACT";
    if [ -s "$LOOPDIR/LOOPSTEER.txt" ]; then
      echo; echo "STEERING FOR THIS ITERATION (overrides the NEXT ACTION assignment):"
      cat "$LOOPDIR/LOOPSTEER.txt"
      mv "$LOOPDIR/LOOPSTEER.txt" "$LOOPDIR/steer-used-$i.txt"
    fi; } > "$LOOPDIR/prompt-$i.txt"

  if [ "${DRYRUN:-0}" = "1" ]; then
    log "iter $i: DRYRUN — prompt built ($(wc -l < "$LOOPDIR/prompt-$i.txt") lines), no model call"
    break
  fi

  # One session, one task, exits on completion (or on the caps).
  timeout -s KILL "$((RUN_BUDGET + 120))" \
    hermes chat --query-file "$LOOPDIR/prompt-$i.txt" --oneshot -Q \
      --yolo --max-turns "$MAX_TURNS" --run-budget "$RUN_BUDGET" \
      > "$out" 2>&1
  rc=$?
  log "iter $i: session exited rc=$rc (log: $out)"
  [ "$rc" = 137 ] && log "iter $i: KILLED by timeout/budget cap"

  # POST-FLIGHT: did the session actually land something on disk?
  verdict=OK
  if ! bash scripts/gate.sh > "$LOOPDIR/post_gate.log" 2>&1; then verdict=GATE_RED; fi
  if ! python3 scripts/ledger_audit.py > "$LOOPDIR/post_audit.log" 2>&1; then
    [ "$verdict" = OK ] && verdict=AUDIT_FAIL
  fi
  committed=$(git log -1 --format='%h %s' 2>/dev/null)
  printf '%s\t%s\t%s\t%s\t%s\n' "$(date '+%F %T')" "$i" "$verdict" "$rc" "$committed" \
    >> "$LOOPDIR/journal.tsv"
  log "iter $i: $verdict | HEAD $committed"

  if [ "$verdict" != OK ]; then
    # Do not spin on a broken tree: park for a human.
    echo "Iteration $i left the tree $verdict. Loop parked; inspect $LOOPDIR/post_*.log and $out, then: rm work/r1/loop/STOP (if you set it) and relaunch." > "$LOOPDIR/NEEDS_HUMAN.txt"
    log "iter $i: NEEDS_HUMAN — parking (touch $LOOPDIR/STOP to keep it down)"
    break
  fi

  sleep "$COOLDOWN"
done
log "loop ended after $i iteration(s); journal: $LOOPDIR/journal.tsv"
