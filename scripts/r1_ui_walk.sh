#!/bin/bash
# D13 UI walkthrough kit (native-vision era).
#   scripts/r1_ui_walk.sh state-name  [click X Y]...
# Launches the rewrite on Xvfb :9 (fresh process per run), applies each
# `click X Y` (WINDOW coords, xsend focuses first) or `key KEYSYM`, waits,
# then crops the game window to work/r1/loop/walk/<state>.png and prints
# the path + tail of the app log. The CALLER (loop session) grades the
# PNG with its OWN vision (D13: native self-grading is policy).
set -e
cd /home/hrethric/projects/ascendancy
STATE="${1:?usage: r1_ui_walk.sh state [click X|key KEYSYM]...}"; shift
OUT=work/r1/loop/walk; mkdir -p "$OUT"
pgrep -x Xvfb >/dev/null || { (Xvfb :9 -screen 0 1024x768x24 >/dev/null 2>&1 &); sleep 2; }
pkill -x ascendancy 2>/dev/null || true
sleep 1
DISPLAY=:9 SDL_AUDIODRIVER=dummy ./rewrite/build/ascendancy \
  --data /tmp/uishow --ui --seed "${SEED:-2024}" > /tmp/walk.log 2>&1 &
UI=$!
sleep 4
while [ $# -ge 2 ]; do
  case "$1" in
    click) DISPLAY=:9 ./tools/xsend Ascendancy click "$2" "$3" >/dev/null;;
    key)   DISPLAY=:9 ./tools/xsend Ascendancy key "$2" >/dev/null;;
    *) echo "unknown step '$1'"; break;;
  esac
  shift 2 2>/dev/null || shift
  sleep "${STEP_WAIT:-2}"
done
DISPLAY=:9 timeout 15 import -window root /tmp/wroot.png
WP=$(DISPLAY=:9 ./tools/winpos Ascendancy)
set -- $WP; X=$1; Y=$2; W=$3; H=$4
~/tools/revenv/bin/python - "$X" "$Y" "$W" "$H" "$OUT/$STATE.png" <<'EOF'
import sys
from PIL import Image
x,y,w,h,out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
x,y,w,h = int(x),int(y),int(w),int(h)
Image.open('/tmp/wroot.png').convert('RGB').crop((x,y,x+w,y+h)).save(out)
print('saved', out)
EOF
echo "--- app log tail:"; tail -4 /tmp/walk.log
echo "STATE_PID=$UI  (leave running for follow-up shots; kill -9 $UI when done)"
