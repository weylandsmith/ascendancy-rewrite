#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

# t369 sentinel (copy of sentinel_t368.sh, BASELINES UNCHANGED — correct while
# docs/DECISIONS.md mtime never moves). Trigger = USER adjudication. Watch:
#   (1) docs/DECISIONS.md mtime newer than 2026-11-10 06:23:41 (t365's own
#       annotation baseline; commit 5758465 post-dates it), OR
#       `git diff --quiet -- docs/DECISIONS.md` fails (content edit);
#   (2) any git-status entry naming *ruling* or *reply*.
# The OQ-005 decision-sheet baseline is CLOSED (t367) — NOT watched.
# NOTE (t368): this poller covers the RULING branch ONLY. The SITTING branch is
# a separate probe: python3 work/r1/t368_ring_turn.py (read the live ring; the
# live-timeline.jsonl feed is DEAD since 2026-11-09 17:26 — do not trust it).
# Poll 60s, cap 45min. Prints TRIGGERED:... or TIMEOUT. Read-only otherwise.
REPO=/home/hrethric/projects/ascendancy
DOC=docs/DECISIONS.md
BASE_EPOCH=$(date -d "2026-11-10 06:23:41" +%s)
deadline=$(( $(date +%s) + 2700 ))
while true; do
  cd "$REPO" || { echo "TRIGGERED:repo-missing"; exit 1; }
  m=$(stat -c %Y "$DOC" 2>/dev/null || echo 0)
  if [ "$m" -gt "$BASE_EPOCH" ]; then echo "TRIGGERED:decisions-mtime"; exit 0; fi
  if ! git diff --quiet -- "$DOC" 2>/dev/null; then echo "TRIGGERED:decisions-diff"; exit 0; fi
  hits=$(git status --porcelain 2>/dev/null | grep -iE 'ruling|reply')
  if [ -n "$hits" ]; then echo "TRIGGERED:reply-file:$hits"; exit 0; fi
  if [ "$(date +%s)" -ge "$deadline" ]; then echo "TIMEOUT:no ruling after 45min"; exit 0; fi
  sleep 60
done
