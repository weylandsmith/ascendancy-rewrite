#!/usr/bin/env bash
# Launch the Ascendancy RE Ralph loop in tmux with the standing goal + gate set.
# Usage:  bash scripts/launch_ralph.sh     (detached; watch: tmux attach -t ascend)
# Stop:   /goal clear inside the session, or: tmux kill-session -t ascend
set -eu
cd "$(dirname "$0")/.."
SESSION=ascend
if tmux has-session -t $SESSION 2>/dev/null; then
  echo "session '$SESSION' already exists — attach with: tmux attach -t $SESSION"; exit 0
fi
tmux new-session -d -s $SESSION -x 200 -y 50 "cd $(pwd) && exec hermes --yolo"
# wait for the hermes prompt (prompt_toolkit painted something)
ready=no
for i in $(seq 1 45); do
  sleep 2
  if tmux capture-pane -t $SESSION -p 2>/dev/null | grep -qE '➤|>|>|hermes'; then ready=yes; break; fi
done
[ "$ready" = yes ] || { echo "hermes did not paint a prompt in 90s; attach manually: tmux attach -t $SESSION"; exit 1; }
sleep 5
# Multi-line goal so the contract fields (Outcome:/Verification:/...) parse.
# Bracketed paste keeps it in the input buffer as ONE submission.
tmux load-buffer -b goalbuf "$PWD/docs/GOAL.txt"
tmux send-keys -t $SESSION "/goal "
tmux paste-buffer -p -b goalbuf -t $SESSION
sleep 1
tmux send-keys -t $SESSION Enter
sleep 3
tmux send-keys -t $SESSION "/goal gate add bash scripts/gate.sh" Enter
sleep 3
tmux send-keys -t $SESSION "/goal status" Enter
sleep 3
# Option C cadence (docs/BLOCKED.md): one bounded R1 attempt per session.
# Skip if one ran within 12 h. Bounded by the script itself (timeout+kill);
# bounded here too so a hung harness can never delay the loop's first turn.
LAST=$(find "$PWD/work/r1" -maxdepth 1 -name 'attempt-*' -type d -mmin -720 2>/dev/null | head -1 || true)
if [ -z "$LAST" ]; then
  echo "R1 session attempt starting (bounded)..." > /tmp/r1_session.log
  R1RC=0
  timeout -s KILL 420 bash scripts/r1_attempt.sh >> /tmp/r1_session.log 2>&1 || R1RC=$?
  echo "r1 exit=$R1RC (0=LIVE upgrade formulas, 1=negative-normal, 2=harness error)" >> /tmp/r1_session.log
  tail -c 600 /tmp/r1_session.log
else
  echo "R1 attempt within 12 h already present: $LAST — skipping session attempt"
fi
echo "--- goal status as rendered by hermes: ---"
tmux capture-pane -t $SESSION -p | grep -v '^$' | tail -12
echo "-------------------------------------------"
echo "If the status above does NOT show an active goal, attach and type it by hand:"
echo "  tmux attach -t $SESSION   then: /goal <paste docs/GOAL.txt on one line> + Enter, /goal gate add bash scripts/gate.sh"
echo "Watch:  tmux attach -t ascend (detach: Ctrl-b d)   Stop: /goal clear"
