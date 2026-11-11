#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

# One-shot: render N intro frames under Xvfb, capture the screen mid-play,
# and pixel-verify the window equals a Python-decoded frame (independent
# cross-check of the C++ blit path). Bounded; no dosbox; kills only its own
# Xvfb pid. Pure-PIL (no numpy on this host). Exit 0 = exact match found.
set -u
cd "$(dirname "$0")/.."
N_FRAMES=${1:-40}
CAP_AFTER=${2:-1.5}
XVFB_DISPLAY_NUM=${3:-78}
Xvfb ":$XVFB_DISPLAY_NUM" -screen 0 1024x768x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=":$XVFB_DISPLAY_NUM" ./rewrite/build/ascendancy --intro "$N_FRAMES" >/tmp/intro_run.log 2>&1 &
APP=$!
sleep "$CAP_AFTER"
DISPLAY=":$XVFB_DISPLAY_NUM" import -window root /tmp/intro_shot.png 2>/dev/null
wait "$APP"
RC=$?
kill "$XV" 2>/dev/null
echo "app rc=$RC"
cat /tmp/intro_run.log
"$HOME/tools/revenv/bin/python" - <<'EOF'
import sys
sys.path.insert(0, 'scripts')
from PIL import Image
from flc_probe import ftc_decode
shot = Image.open('/tmp/intro_shot.png').convert('RGB')
print('shot', shot.size)
frames = {}
def on(i, fr, meta):
    frames[i] = (bytes(fr.px), list(fr.pal))
ftc_decode('extracted/ascend02/data/intro65a.flc', on_frame=on, max_frames=45)
# SDL_WINDOWPOS_CENTERED on 1024x768 for a 640x480 window -> (192,144);
# capture ~1.5 s in at 71 ms -> frames ~15-30; tolerate +/-16 px origin.
hits = []
for i in sorted(frames)[:45]:
    px, pal = frames[i]
    pim = Image.frombytes('P', (640, 480), px)
    pim.putpalette([c for rgb in pal for c in rgb])
    img = pim.convert('RGB')
    target = img.tobytes()
    found = False
    for y in range(128, 161, 2):
        for x in range(176, 209, 2):
            crop = shot.crop((x, y, x + 640, y + 480)).tobytes()
            if crop == target:
                hits.append((i, x, y)); found = True; break
        if found:
            break
for i, x, y in hits:
    print(f'EXACT window match: decoded frame {i} at ({x},{y})')
if not hits:
    print('NO exact window match in the frame band 0..44')
    sys.exit(1)
EOF
