#!/usr/bin/env bash
# tNGR cadence relaunch wrapper (t286 BREAK-lottery law, r_tNGS3_w1 pattern):
# each script run is one launch lottery; retry the WHOLE launch, max 5.
cd /home/hrethric/projects/ascendancy
PY=$HOME/tools/revenv/bin/python
for i in 1 2 3 4 5; do
  echo "=== LAUNCH ATTEMPT $i $(date +%H:%M:%S) ==="
  "$PY" scripts/r_tNGR_cadence_session.py
  rc=$?
  echo "=== attempt $i rc=$rc ==="
  [ $rc -eq 0 ] && exit 0
  [ $rc -eq 2 ] && exit 2      # harness error: never retry
  sleep 8
done
exit 1
