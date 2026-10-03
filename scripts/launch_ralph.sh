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
echo "--- goal status as rendered by hermes: ---"
tmux capture-pane -t $SESSION -p | grep -v '^$' | tail -12
echo "-------------------------------------------"
echo "If the status above does NOT show an active goal, attach and type it by hand:"
echo "  tmux attach -t $SESSION   then: /goal <paste docs/GOAL.txt on one line> + Enter, /goal gate add bash scripts/gate.sh"
echo "Watch:  tmux attach -t ascend (detach: Ctrl-b d)   Stop: /goal clear"
