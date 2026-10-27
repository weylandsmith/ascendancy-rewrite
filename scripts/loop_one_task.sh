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
#
# Journal law (t95b): every iteration gets an honest verdict —
#   OK          gate+audit green AND new commit AND rc clean
#   NO_COMMIT   session exited cleanly but HEAD did not move (task unfinished)
#   KILLED      SIGKILL at budget+grace (wall clock ran out)
#   GATE_RED / AUDIT_FAIL  tree left broken -> park immediately
# NO_COMMIT/KILLED twice in a row on the same task = task too big for one
# session -> park with advice to split it, instead of burning API re-trying it.
set -uo pipefail          # NOT -e: a failing iteration must not kill the loop
cd "$(dirname "$0")/.."
ROOT="$PWD"
LOOPDIR="work/r1/loop"
mkdir -p "$LOOPDIR"
MAX_ITERS="${MAX_ITERS:-0}"          # 0 = unlimited
MAX_TURNS="${MAX_TURNS:-500}"        # tool-iteration cap inside the one turn
RUN_BUDGET="${RUN_BUDGET:-10800}"    # 3 h wall per task (slow local model:
GRACE="${GRACE:-1800}"               # time is cheap, context is not — see contract)
KILL_AT=$((RUN_BUDGET + GRACE))
COOLDOWN="${COOLDOWN:-15}"           # seconds between iterations
CONTRACT="docs/TASK_CONTRACT.txt"

log() { echo "[$(date '+%F %T')] $*"; }

if [ "${1:-}" = "--status" ]; then
  echo "journal rows     : $(wc -l < "$LOOPDIR/journal.tsv" 2>/dev/null || echo 0)"
  echo "iteration id at  : $(cat "$LOOPDIR/iter.count" 2>/dev/null || echo 0)"
  echo "fail streak      : $(cat "$LOOPDIR/fail_streak" 2>/dev/null || echo 0)"
  echo "stop flag        : $([ -f "$LOOPDIR/STOP" ] && echo PRESENT || echo absent)"
  echo "needs human      : $([ -f "$LOOPDIR/NEEDS_HUMAN.txt" ] && echo PRESENT || echo absent)"
  echo "dirty tree       : $([ -n "$(git status --porcelain)" ] && echo YES || echo no)"
  echo "next action      : $(awk '/^#+ *NEXT ACTION/{f=1;next} f&&NF{print;exit}' docs/STATE.md)"
  echo "last 6 journal rows (time, iter, VERDICT, rc, task, HEAD subject):"
  tail -6 "$LOOPDIR/journal.tsv" 2>/dev/null | awk -F'\t' '{printf "  %s  %-3s  %-10s rc=%-4s %-7s %.100s\n", $1, $2, $3, $4, $5, substr($6,1,100)}' || echo "  (none)"
  exit 0
fi

[ -f "$CONTRACT" ] || { echo "missing $CONTRACT"; exit 1; }
command -v hermes >/dev/null || { echo "hermes not on PATH"; exit 1; }

i=0
while :; do
  i=$((i+1))
  [ "$MAX_ITERS" -gt 0 ] && [ "$i" -gt "$MAX_ITERS" ] && { log "MAX_ITERS reached"; break; }
  [ -f "$LOOPDIR/STOP" ] && { log "STOP flag present — exiting"; break; }

  # Monotonic iteration id survives relaunches (journal rows never collide).
  n=$(( $(cat "$LOOPDIR/iter.count" 2>/dev/null || echo 0) + 1 ))
  echo "$n" > "$LOOPDIR/iter.count"

  # Pre-flight: never start an iteration from a red tree.
  if ! bash scripts/gate.sh > "$LOOPDIR/preflight_gate.log" 2>&1; then
    log "iter $n: GATE RED before start — not launching. See $LOOPDIR/preflight_gate.log"
    sleep 60; continue
  fi

  next=$(awk '/^#+ *NEXT ACTION/{f=1;next} f&&NF{print;exit}' docs/STATE.md)
  task=$(echo "$next" | awk 'NF{print $2; exit}' | tr -d ':')
  [ -n "$task" ] || task=steer
  log "iter $n: NEXT[$task] = ${next:-<unparsed>}"
  pre_head=$(git rev-parse --short HEAD 2>/dev/null)

  # Adoption rule: a killed session leaves uncommitted work behind. It is gold,
  # not garbage — the next session finishes and commits it before new work.
  dirty=""
  [ -n "$(git status --porcelain)" ] && dirty=1

  out="$LOOPDIR/iter-$(date +%Y%m%d-%H%M%S)-$n.log"
  # Steering hook: if LOOPSTEER.txt exists, its contents replace the task text
  # for THIS iteration only (then get archived, so it can't go stale).
  { cat "$CONTRACT"
    if [ -s "$LOOPDIR/LOOPSTEER.txt" ]; then
      echo; echo "STEERING FOR THIS ITERATION (overrides the NEXT ACTION assignment):"
      cat "$LOOPDIR/LOOPSTEER.txt"
      mv "$LOOPDIR/LOOPSTEER.txt" "$LOOPDIR/steer-used-$n.txt"
    fi
    if [ -n "$dirty" ]; then
      echo; echo "INTERRUPTED PRIOR WORK DETECTED: git status is not clean — a previous"
      echo "session was killed mid-task. Its uncommitted work is YOURS to adopt: review"
      echo "the diff, finish the FINISH SEQUENCE for it, and COMMIT it BEFORE starting"
      echo "the NEXT ACTION below (fold both into one commit if they are the same task)."
    fi; } > "$LOOPDIR/prompt-$n.txt"

  if [ "${DRYRUN:-0}" = "1" ]; then
    log "iter $n: DRYRUN — prompt built ($(wc -l < "$LOOPDIR/prompt-$n.txt") lines), no model call"
    break
  fi

  # One session, one task, exits on completion (or on the caps). Hermes injects
  # its own wrap-up warning at 80% of --run-budget; GRACE is what we give the
  # session after that warning to bank docs + commit before the wall kills it.
  # --format stream-json: NDJSON events land in $out AS THEY HAPPEN (a -Q run
  # writes nothing until the final response, so a working session looks dead
  # and a killed session leaves a 0-byte log). tee keeps the tmux pane live.
  timeout -s KILL "$KILL_AT" \
    hermes chat --query-file "$LOOPDIR/prompt-$n.txt" --oneshot \
      --format stream-json \
      --yolo --max-turns "$MAX_TURNS" --run-budget "$RUN_BUDGET" \
      2>&1 | tee "$out"
  rc=${PIPESTATUS[0]}
  log "iter $n: session exited rc=$rc (log: $out)"
  [ "$rc" = 137 ] && log "iter $n: KILLED at budget+grace (${KILL_AT}s wall)"

  # POST-FLIGHT: honest verdict — green tree alone is NOT progress.
  verdict=OK
  if ! bash scripts/gate.sh > "$LOOPDIR/post_gate.log" 2>&1; then verdict=GATE_RED; fi
  if ! python3 scripts/ledger_audit.py > "$LOOPDIR/post_audit.log" 2>&1; then
    [ "$verdict" = OK ] && verdict=AUDIT_FAIL
  fi
  post_head=$(git rev-parse --short HEAD 2>/dev/null)
  if [ "$verdict" = OK ] && [ "$rc" = 137 ]; then verdict=KILLED; fi
  if [ "$verdict" = OK ] && [ "$post_head" = "$pre_head" ]; then verdict=NO_COMMIT; fi
  committed=$(git log -1 --format='%h %s' 2>/dev/null)

  streak=$(cat "$LOOPDIR/fail_streak" 2>/dev/null || echo 0)
  if [ "$verdict" = OK ]; then echo 0 > "$LOOPDIR/fail_streak";
  else echo $((streak+1)) > "$LOOPDIR/fail_streak"; streak=$((streak+1)); fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$(date '+%F %T')" "$n" "$verdict" "$rc" "$task" "$committed" \
    >> "$LOOPDIR/journal.tsv"
  if [ "$post_head" != "$pre_head" ]; then
    log "iter $n: $verdict rc=$rc task=$task | HEAD $pre_head -> $post_head (ADVANCED)"
  else
    log "iter $n: $verdict rc=$rc task=$task | HEAD unchanged ($post_head)"
  fi

  if [ "$verdict" = GATE_RED ] || [ "$verdict" = AUDIT_FAIL ]; then
    # Do not spin on a broken tree: park for a human.
    echo "Iteration $n left the tree $verdict. Loop parked; inspect $LOOPDIR/post_*.log and $out. Fix the tree, rm $LOOPDIR/NEEDS_HUMAN.txt, relaunch." > "$LOOPDIR/NEEDS_HUMAN.txt"
    log "iter $n: NEEDS_HUMAN — parking"
    break
  fi
  if [ "$verdict" != OK ] && [ "$streak" -ge 2 ]; then
    echo "Iterations $n and the one before made no progress on task '$task' (verdict $verdict). The task likely does not fit one session: split it into smaller subtasks in docs/STATE.md NEXT ACTION (each independently committable), rm $LOOPDIR/NEEDS_HUMAN.txt, relaunch." > "$LOOPDIR/NEEDS_HUMAN.txt"
    log "iter $n: two no-progress runs on '$task' — parking with split advice"
    break
  fi

  sleep "$COOLDOWN"
done
log "loop ended after $i run(s) this launch (journal id $n); journal: $LOOPDIR/journal.tsv"
