#!/usr/bin/env bash
# tPF5-A INDICATOR-POPUP FRAME WITNESS. Legs:
#   (1) fresh campaign (seed 5), RESUME, click a planet -> PLANETALLOC;
#   (2) click the PLRES tile (60,50 inside windows.txt 7,7..114,106) ->
#       msg-50 popup; shoot;
#   (3) CENSUS (inline python): the help.shp k0 frame edges OUTSIDE the old
#       dim-backing rect (x/y 7..9) must be NON-BLACK (the old build paints
#       black there — clean discriminator; non-black-frac law tPF-11);
#   (4) log legs: 'ui planet popup plres' fired AND 'frame lib refused'
#       ABSENT. Scratch Xvfb :99, kill BY PID.
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/tpf5a_shots}
DISP=${DISP:-:99}
PY=${PY:-$HOME/tools/revenv/bin/python}
rm -rf "$OUT"; mkdir -p "$OUT"
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP SDL_AUDIODRIVER=dummy "$BIN" --ui --campaign 1 --seed 5 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 3
X() { DISPLAY=$DISP ./tools/xsend "Ascendancy" "$@"; sleep 1; }
shot() { sleep 0.3; DISPLAY=$DISP import -window root -crop 640x480+0+0 +repage "$OUT/$1.png" 2>>"$OUT/app.log"; }

X 318 335            # RESUME -> campaign map
X 553 145            # STATUS rail -> planets list (tPF5_port nav law)
sleep 1
X 300 100            # ROW 0 -> planet view (PLANETALLOC)
sleep 1
X 60 50              # PLRES tile -> msg-50 indicator popup
sleep 1
X warp 400 470       # park the cursor off the census bands (tPF5_port law)
shot indpopup
kill $APP 2>/dev/null; kill $XV 2>/dev/null
wait 2>/dev/null

grep -q "ui planet popup plres" "$OUT/app.log" || { echo "FAIL: popup log line absent"; cat "$OUT/app.log"; exit 1; }
grep -q "frame lib refused" "$OUT/app.log" && { echo "FAIL: help.shp refused"; exit 1; }
"$PY" - "$OUT/indpopup.png" <<'EOF'
import sys
from PIL import Image
im = Image.open(sys.argv[1]).convert("RGB")
px = im.load()
def nb(x0, y0, x1, y1):
    tot = n = 0
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            tot += 1
            if sum(px[x, y]) > 30:
                n += 1
    return n / tot
# Frame edges OUTSIDE the old dim backing (old backing = 17,17..332,214):
top = nb(30, 7, 320, 10)      # top frame band rows 7..10
left = nb(7, 40, 10, 200)     # left frame band
bot = nb(30, 259, 320, 262)   # bottom frame band (k0 rows 252..255)
# Control: mid-screen far from any popup art (starfield area right side)
ctl = nb(420, 300, 560, 400)
print(f"top={top:.3f} left={left:.3f} bot={bot:.3f} ctl={ctl:.3f}")
ok = top > 0.5 and left > 0.5 and bot > 0.5
print("VERDICT", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
EOF
