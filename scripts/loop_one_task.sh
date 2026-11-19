#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

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
# Queue work while idle (wakes the loop WITHOUT a capture trigger):
#   echo "TASK TEXT" > work/r1/loop/LOOPSTEER.txt   (one-shot, consumed)
#   touch work/r1/loop/FORCE_RUN                    (run NEXT ACTION once)
# DO NOT redirect stdout to a file at launch (">> loop.log"): tee writes the
# per-iteration event log itself, and a launch redirect starves the tmux pane
# (the t178 "blank window" report — server showed 78k events, pane saw zero).
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
# IDLE GATE (t178): the trigger check runs HERE in shell, zero model calls.
# r1_idle_probe.py RC=0 stay idle / RC=1 trigger armed / RC=2 probe broken.
# This replaces ~66 model sessions that existed only to re-verify "nothing
# new" — an idle poll must cost nothing but a python run.
IDLE_PROBE="scripts/r1_idle_probe.py"
IDLE_GATE="${IDLE_GATE:-1}"
IDLE_SLEEP="${IDLE_SLEEP:-900}"      # 15 min between idle polls
# (t243) max consecutive queue-only (trigger-C) wakes before the idle gate
# re-closes even on a tag change. 8 drains any honestly-queued batch (the
# t194 queue held 5) while capping the t214..t242 ping-pong at 8, not 29.
QUEUE_CHAIN_MAX="${QUEUE_CHAIN_MAX:-8}"

log() { echo "[$(date '+%F %T')] $*"; }

if [ "${1:-}" = "--status" ]; then
  echo "journal rows     : $(wc -l < "$LOOPDIR/journal.tsv" 2>/dev/null || echo 0)"
  echo "iteration id at  : $(cat "$LOOPDIR/iter.count" 2>/dev/null || echo 0)"
  echo "fail streak      : $(cat "$LOOPDIR/fail_streak" 2>/dev/null || echo 0)"
  echo "stop flag        : $([ -f "$LOOPDIR/STOP" ] && echo PRESENT || echo absent)"
  echo "idle polls       : $(grep -c 'idle poll' "$LOOPDIR/loop.log" 2>/dev/null || echo 0) (shell-gated, no model) last: $(grep 'idle poll' "$LOOPDIR/loop.log" 2>/dev/null | tail -1 | cut -c2-40)"
  echo "needs human      : $([ -f "$LOOPDIR/NEEDS_HUMAN.txt" ] && echo PRESENT || echo absent)"
  echo "dirty tree       : $([ -n "$(git status --porcelain)" ] && echo YES || echo no)"
  echo "next action      : $(awk '/^#+ *NEXT ACTION/{f=1;next} f&&NF{print;exit}' docs/STATE.md)"
  echo "last 6 journal rows (time, iter, VERDICT, rc, task, HEAD subject):"
  tail -6 "$LOOPDIR/journal.tsv" 2>/dev/null | awk -F'\t' '{printf "  %s  %-3s  %-10s rc=%-4s %-7s %.100s\n", $1, $2, $3, $4, $5, substr($6,1,100)}' || echo "  (none)"
  exit 0
fi

[ -f "$CONTRACT" ] || { echo "missing $CONTRACT"; exit 1; }
command -v hermes >/dev/null || { echo "hermes not on PATH"; exit 1; }
if [ "${DRYRUN:-0}" = "1" ]; then IDLE_GATE=0; fi   # dryrun must reach prompt build

i=0          # real sessions launched this run (MAX_ITERS counts these)
idle_skips=0
n=$(cat "$LOOPDIR/iter.count" 2>/dev/null || echo 0)
armed_report=""
while :; do
  [ "$MAX_ITERS" -gt 0 ] && [ "$i" -ge "$MAX_ITERS" ] && { log "MAX_ITERS reached"; break; }
  [ -f "$LOOPDIR/STOP" ] && { log "STOP flag present — exiting"; break; }

  # Adoption check FIRST: a dirty tree is interrupted work, not idleness, and
  # outranks the idle gate entirely. A LOOPSTEER.txt is a human assigning work
  # — that also wakes the loop (queue: write the file, or edit NEXT ACTION and
  # set FORCE_RUN once).
  dirty=""
  [ -n "$(git status --porcelain)" ] && dirty=1
  steer_wake=""
  [ -s "$LOOPDIR/LOOPSTEER.txt" ] && steer_wake=1
  [ -f "$LOOPDIR/FORCE_RUN" ] && { steer_wake=1; rm -f "$LOOPDIR/FORCE_RUN"; }
  # (t243) human steering is likewise an external wake — chain restarts.
  [ -n "$steer_wake" ] && echo 0 > "$LOOPDIR/chain_count"

  # TRIGGER C (t199): OFFLINE-QUEUE DRAIN. Triggers A (capture) and B (human
  # edit) cannot see a queue the LOOP itself staged into NEXT ACTION, so the
  # loop idled forever with t195 pending (t199: ran the two wake-woken tasks,
  # then slept on a full queue). Marker law kept per t186: compare NEXT's task
  # TAG (single awk field) against $LOOPDIR/last_task, written by POST-FLIGHT
  # ONLY on an OK verdict of a NON-STEERED run — no prose diffs, and a steered
  # run never marks the queue task done. Sentinels WAIT*/IDLE*/PARK*/steer/
  # empty NEVER arm; empty last_task (fresh install) never arms.
  next=$(awk '/^#+ *NEXT ACTION/{f=1;next} f&&NF{print;exit}' docs/STATE.md)
  # CONT-cycle rows ("NEXT tNNN CONT cycle K —") must extract a tag that
  # DIFFERS from the parent task AND from prior cycles, else field-2 ==
  # last_done and the wake trigger reads "already done" (t422 stopped the
  # batch this way 2026-11-17): tag = tNNNCONT<K>.
  task=$(echo "$next" | awk 'NF{ w3=toupper($3); w4=toupper($4); if (w3=="CONT" && w4 ~ /^CYCLE/) print $2 "CONT" toupper($5); else print $2; exit }' | tr -d ':')
  [ -n "$task" ] || task=steer
  queue_wake=""; steer_used=""
  last_ok_tag=$(cat "$LOOPDIR/last_task" 2>/dev/null)
  case "$task" in
    WAIT*|IDLE*|PARK*|steer) : ;;
    *) if [ -n "$last_ok_tag" ] && [ "$task" != "$last_ok_tag" ]; then queue_wake=1; fi ;;
  esac

  # CHAIN CAP (t243): trigger C self-armed TWENTY-NINE times (t214..t242)
  # because an iteration that finds nothing still rewrites NEXT to the next
  # LETTER, so the tag keeps differing — the same self-arm class t186 killed
  # for prose, reborn as tags. LAW: idle/sitting-probing is SHELL-GATE work
  # (t178 IDLE IS HARNESS'S PROBLEM), never a numbered NEXT task; the loop
  # must park NEXT on a WAIT*/IDLE* sentinel when it has no research left. The
  # cap is the backstop: QUEUE_CHAIN_MAX consecutive queue-only wakes with no
  # external trigger (A/B) or steering is enough to drain any real queue; past
  # that the gate closes even on a tag change. Counter resets on any external
  # wake and on any probe pass through the gate.
  chain=$(cat "$LOOPDIR/chain_count" 2>/dev/null || echo 0)
  if [ -n "$queue_wake" ] && [ "$chain" -ge "$QUEUE_CHAIN_MAX" ] \
     && [ -z "$steer_wake" ] && [ -z "$dirty" ]; then
    log "queue chain cap: $chain consecutive queue-only wakes >= QUEUE_CHAIN_MAX=$QUEUE_CHAIN_MAX — holding at the idle gate (park NEXT on a WAIT*/IDLE* sentinel to stop the ping-pong)"
    queue_wake=""
  fi

  # (t248) QUEUE-DRIVEN MODE: IDLE_GATE=0 skips the probe, so without this the
  # loop would launch a steer-less session every COOLDOWN forever once the
  # queue drains (the t214..t243 churn arriving through a different door).
  # Exit when NOTHING is runnable: no queue wake (drained WAIT sentinel OR
  # chain cap), no human steering, no dirty tree to adopt. Retries still work:
  # last_task is written only on an OK verdict, so a failed task keeps waking.
  if [ "$IDLE_GATE" = "0" ] && [ -z "$queue_wake" ] && [ -z "$steer_wake" ] && [ -z "$dirty" ]; then
    log "nothing runnable (NEXT tag '$task', no wake, IDLE_GATE=0) — batch complete, exiting"
    break
  fi

  # IDLE GATE (t178): poll triggers in SHELL before spending any model budget.
  # dirty tree => adopt interrupted work (launch regardless of probe);
  # probe RC=0 clean => IDLE: sleep, check STOP, no session, no journal row;
  # probe RC=1 => trigger armed: launch with the probe report appended;
  # probe RC=2 => trigger detector broken: park, never grade idle on it.
  armed_report=""
  if [ -n "$steer_wake" ] && [ -z "$dirty" ]; then log "WAKE: human steering queued (LOOPSTEER.txt/FORCE_RUN) — bypassing idle gate"; fi
  if [ -n "$queue_wake" ] && [ -z "$dirty" ] && [ -z "$steer_wake" ]; then log "WAKE: TRIGGER C queue drain ($last_ok_tag -> $task) — bypassing idle gate"; fi
  if [ "$IDLE_GATE" = "1" ] && [ -z "$dirty" ] && [ -z "$steer_wake" ] && [ -z "$queue_wake" ]; then
    timeout 300 python3 "$IDLE_PROBE" > "$LOOPDIR/probe-last.log" 2>&1
    prc=$?
    if [ "$prc" = "0" ]; then
      idle_skips=$((idle_skips+1))
      log "idle poll $idle_skips: IDLE — no session launched (sleep ${IDLE_SLEEP}s)"
      elapsed=0
      while [ "$elapsed" -lt "$IDLE_SLEEP" ]; do
        [ -f "$LOOPDIR/STOP" ] && break
        sleep 30; elapsed=$((elapsed+30))
      done
      continue
    elif [ "$prc" = "1" ]; then
      log "IDLE-GATE: TRIGGER ARMED — launching with probe context"
      armed_report=1
      # external (capture/human) wake: the chain is no longer queue-only, so
      # the cap counter restarts (t243 law stated in the CHAIN CAP block).
      echo 0 > "$LOOPDIR/chain_count"
    else
      echo "r1_idle_probe.py exited $prc (probe broken, not idle): see $LOOPDIR/probe-last.log. Fix the probe; triggers cannot be judged without it." > "$LOOPDIR/NEEDS_HUMAN.txt"
      log "idle probe RC=$prc — parking"
      break
    fi
  fi

  i=$((i+1))
  # Monotonic iteration id survives relaunches (journal rows never collide).
  n=$(( $(cat "$LOOPDIR/iter.count" 2>/dev/null || echo 0) + 1 ))
  echo "$n" > "$LOOPDIR/iter.count"

  # t267 SELF-HEAL (advisory, sub-second): stamp game/TL/watcher/ring state
  # EVERY iteration — including under IDLE_GATE=0, where r1_idle_probe.py
  # never runs and the t266 15:45 death sat unnoticed 1.5 h. Runs BEFORE the
  # pre-flight gate so a dead game is timestamped even on a red tree.
  # Non-fatal by design: relaunching the game is research-schedule policy,
  # not something the scheduler should do unattended.
  python3 scripts/r1_game_health.py > "$LOOPDIR/health-last.log" 2>&1
  log "GAME-HEALTH(rc=$?): $(head -1 "$LOOPDIR/health-last.log")"
  [ -f "$LOOPDIR/GAME_DEAD.txt" ] && log "GAME-HEALTH: $(cat "$LOOPDIR/GAME_DEAD.txt" | head -1)"

  # Pre-flight: never start an iteration from a red tree.
  if ! bash scripts/gate.sh > "$LOOPDIR/preflight_gate.log" 2>&1; then
    log "iter $n: GATE RED before start — not launching. See $LOOPDIR/preflight_gate.log"
    sleep 60; continue
  fi

  # (t199) task/next extracted EARLIER (trigger C needs the tag pre-gate).
  log "iter $n: NEXT[$task] = ${next:-<unparsed>}"
  pre_head=$(git rev-parse --short HEAD 2>/dev/null)

  out="$LOOPDIR/iter-$(date +%Y%m%d-%H%M%S)-$n.log"
  # Steering hook: if LOOPSTEER.txt exists, its contents replace the task text
  # for THIS iteration only (then get archived, so it can't go stale).
  { cat "$CONTRACT"
    if [ -n "$armed_report" ]; then
      echo; echo "IDLE-GATE TRIGGER ARMED — r1_idle_probe.py report follows. The task is"
      echo "to act on the armed trigger (inspect the new capture / the user delta),"
      echo "not to re-run the idle protocol:"
      cat "$LOOPDIR/probe-last.log"
    fi
    if [ -s "$LOOPDIR/LOOPSTEER.txt" ]; then
      echo; echo "STEERING FOR THIS ITERATION (overrides the NEXT ACTION assignment):"
      cat "$LOOPDIR/LOOPSTEER.txt"
      mv "$LOOPDIR/LOOPSTEER.txt" "$LOOPDIR/steer-used-$n.txt"
      steer_used=1
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
  # OOM FENCE (2026-11-18): a t426 numpy census ballooned to the tmux
  # scope's 20.8G peak and the OOM killer killed the tmux SERVER (and the
  # scheduler with it) — scope death takes everything down. Run each
  # session in its OWN systemd user scope capped at 14G: a runaway child
  # OOMs inside its cgroup (SIGKILL -> rc=137, journal KILLED, next
  # iteration adopts the dirty tree) instead of nuking the host session.
  systemd-run --user --scope --quiet -p MemoryMax=14G -p MemorySwapMax=1G \
    bash -c 'timeout -s KILL "$1" hermes chat --query-file "$2" --oneshot \
      --format stream-json --yolo --max-turns "$3" --run-budget "$4"' \
    _ "$KILL_AT" "$LOOPDIR/prompt-$n.txt" "$MAX_TURNS" "$RUN_BUDGET" \
      2>&1 | tee "$out"
  rc=${PIPESTATUS[0]}
  log "iter $n: session exited rc=$rc (log: $out)"
  [ "$rc" = 137 ] && log "iter $n: KILLED at budget+grace (${KILL_AT}s wall) OR cgroup OOM (check journalctl -k)"

  # POST-FLIGHT: honest verdict — green tree alone is NOT progress.
  verdict=OK
  if ! bash scripts/gate.sh > "$LOOPDIR/post_gate.log" 2>&1; then verdict=GATE_RED; fi
  if ! python3 scripts/ledger_audit.py > "$LOOPDIR/post_audit.log" 2>&1; then
    [ "$verdict" = OK ] && verdict=AUDIT_FAIL
  fi
  post_head=$(git rev-parse --short HEAD 2>/dev/null)
  if [ "$verdict" = OK ] && [ "$rc" = 137 ]; then verdict=KILLED; fi
  # rc!=0 means the session never reached its own finish sequence (2026-11-18:
  # a cgroup OOM surfaced as rc=130 "Interrupted"; the adoption commit
  # advanced HEAD and the OK verdict marked the queue tag DONE — t426 was
  # skipped). HEAD-advanced proves a COMMIT happened, never that the TASK
  # finished; adoption commits advance HEAD too. Only rc=0 closes a task.
  if [ "$verdict" = OK ] && [ "$rc" != 0 ]; then verdict=ABORT; fi
  if [ "$verdict" = OK ] && [ "$post_head" = "$pre_head" ]; then verdict=NO_COMMIT; fi
  committed=$(git log -1 --format='%h %s' 2>/dev/null)

  streak=$(cat "$LOOPDIR/fail_streak" 2>/dev/null || echo 0)
  if [ "$verdict" = OK ]; then echo 0 > "$LOOPDIR/fail_streak";
  else echo $((streak+1)) > "$LOOPDIR/fail_streak"; streak=$((streak+1)); fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$(date '+%F %T')" "$n" "$verdict" "$rc" "$task" "$committed" \
    >> "$LOOPDIR/journal.tsv"
  # (t199) trigger-C marker: an OK verdict on a NON-steered run means NEXT's
  # task tag was actually done, so the queue advances; a steered run ran
  # different work and MUST NOT mark it. NO_COMMIT/KILLED/GATE_RED never mark.
  if [ "$verdict" = OK ] && [ -z "$steer_used" ]; then
    echo "$task" > "$LOOPDIR/last_task"
  fi
  # CHAIN COUNTER (t243): "substantive" is measured from the COMMIT DIFF, not
  # the commit subject — MEASURED t243: 5/5 idle commits touch exactly
  # docs/STATE.md + docs/re/_wip_tNNN.md; real research touches research docs,
  # the ledger, rewrite/, or scripts/. Only a substantive delta resets the
  # chain; an idle adjudication that renumbers NEXT to the next letter does
  # not, which is precisely the ping-pong the cap must stop.
  if [ "$verdict" = OK ] && [ "$post_head" != "$pre_head" ]; then
    if git diff --name-only "$pre_head" "$post_head" | grep -qvE '^(docs/STATE\.md|docs/re/_wip_.*\.md|docs/BLOCKED\.md)$'; then
      echo 0 > "$LOOPDIR/chain_count"
    else
      echo $(( $(cat "$LOOPDIR/chain_count" 2>/dev/null || echo 0) + 1 )) > "$LOOPDIR/chain_count"
    fi
  fi
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
