#!/bin/bash
# t425b GRADE shot: campaign map, race-filter strip crop (port side).
set -e
cd /home/hrethric/projects/ascendancy
pgrep -x Xvfb >/dev/null || { (Xvfb :9 -screen 0 1024x768x24 >/dev/null 2>&1 &); sleep 2; }
pkill -x ascendancy 2>/dev/null || true
sleep 1
DISPLAY=:9 SDL_AUDIODRIVER=dummy ./rewrite/build/ascendancy \
  --data /tmp/uishow --ui --campaign 1 --seed 5 > /tmp/t425b_grade.log 2>&1 &
UI=$!
trap 'kill $UI 2>/dev/null || true' EXIT
sleep 4
DISPLAY=:9 ./tools/xsend Ascendancy click 318 335 >/dev/null
sleep 2
DISPLAY=:9 timeout 15 import -window root /tmp/t425b_full.png
WP=$(DISPLAY=:9 ./tools/winpos Ascendancy)
pkill -x ascendancy 2>/dev/null || true
~/tools/revenv/bin/python - "$WP" <<'EOF'
import sys, numpy as np
from PIL import Image
x,y,w,h = [int(v) for v in sys.argv[1].split()[:4]]
a=np.asarray(Image.open('/tmp/t425b_full.png').convert('RGB'))[y:y+h,x:x+w]
Image.fromarray(a[438:476,470:636]).resize((166*5,38*5), Image.NEAREST).save('/tmp/t425b_port_strip.png')
Image.fromarray(a).save('/tmp/t425b_port_map.png')
print("saved", a.shape)
EOF
