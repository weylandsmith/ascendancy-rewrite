#!/bin/bash
# t411 MAP LOOK witness: launch the rewrite on Xvfb, shoot the map screen,
# run the MECHANICAL census (pale-skip pixels, digit green ratio, texture
# lag-1 statistic, bevel darkness). Prints VERDICT PASS/FAIL.
set -e
cd /home/hrethric/projects/ascendancy
pgrep -x Xvfb >/dev/null || { (Xvfb :9 -screen 0 1024x768x24 >/dev/null 2>&1 &); sleep 2; }
pkill -x ascendancy 2>/dev/null || true
sleep 1
DISPLAY=:9 SDL_AUDIODRIVER=dummy ./rewrite/build/ascendancy \
  --data /tmp/uishow --ui --campaign 1 --seed 5 > /tmp/t411_witness.log 2>&1 &
UI=$!
sleep 4
# RESUME -> campaign map (t394 witness law: title button centre 318,335)
DISPLAY=:9 ./tools/xsend Ascendancy click 318 335 >/dev/null
sleep 2
DISPLAY=:9 timeout 15 import -window root /tmp/t411_root.png
WP=$(DISPLAY=:9 ./tools/winpos Ascendancy)
set -- $WP; X=$1; Y=$2; W=$3; H=$4
~/tools/revenv/bin/python - "$X" "$Y" "$W" "$H" <<'EOF'
import sys
import numpy as np
from PIL import Image
x,y,w,h = (int(v) for v in sys.argv[1:5])
a = np.asarray(Image.open('/tmp/t411_root.png').convert('RGB'))[y:y+h, x:x+w]
Image.fromarray(a).save('work/r1/loop/t411-map.png')
fails = []
# 1) NO pale-skip pixels (game.pal[170] = (146,178,134)) anywhere in the
#    chrome zones (blend-mode fix, _wip_t411 F2).
t = (146,178,134)
pale = (a[:,:,0]==t[0])&(a[:,:,1]==t[1])&(a[:,:,2]==t[2])
n = int(pale.sum())
print(f'census pale(146,178,134) pixels: {n}')
if n > 0: fails.append(f'pale-skip pixels {n} > 0')
# 2) TURNCOUNT digit slots: green fraction must sit near the vendor's 14-17%
#    (was 63%). Bound < 40%.
def greenf(band):
    b = band.reshape(-1,3).astype(int)
    g = (b[:,1]>90)&(b[:,1]>b[:,0]+30)&(b[:,1]>b[:,2]+30)
    return g.mean()
fr = [greenf(a[7:44, xs:xs+31]) for xs in (482,513,544,575,606)]
print('digit slot green fractions:', [f'{v:.2f}' for v in fr])
if any(v > 0.40 for v in fr): fails.append(f'digit green {fr} > 0.40')
# 3) texture lag-1 statistic < 0.6 on the sidebar band (vendor 0.23, static 1.45)
band = a[100:400, 474:632].mean(axis=2)
r1 = np.abs(np.diff(band,axis=1)).mean()/np.abs(band-band.mean()).mean()
print(f'texture lag-1 ratio: {r1:.2f}')
if not (0.05 < r1 < 0.60): fails.append(f'texture lag-1 {r1:.2f} outside (0.05,0.60)')
# 4) bevel: pixel just inside COSMOSWnd top edge (240,7) dark (<60); the old
#    flat frame line was 120.
bv = int(a[7,240].mean())
print(f'bevel pixel (240,7) luminance: {bv}')
if bv >= 60: fails.append(f'bevel pixel {bv} >= 60')
# 5) stars render: non-black blobs inside the field
field = a[10:468, 10:462]
print(f'field non-black px: {int((field.max(axis=2)>60).sum())}')
if (field.max(axis=2)>60).sum() < 200: fails.append('field nearly empty')
print('VERDICT', 'FAIL: ' + '; '.join(fails) if fails else 'PASS')
sys.exit(1 if fails else 0)
EOF
VERDICT=$?
# ---- dial walk (queue item 6): click each cluster control, expect the cam
# line to MOVE for the 7 wired controls and the seam line for the 3 toggles
# with no overlay model. Rect centres from kMapCtl (mapchrome.cpp).
dial_walk() {
  local fails=0
  for spec in "rotleft 486 379" "rotright 502 379" "rotup 533 371" "rotdown 533 387" \
              "zoomin 572 371" "zoomout 572 387" "centerholo 611 379" "toglanes 494 418"; do
    set -- $spec
    DISPLAY=:9 ./tools/xsend Ascendancy click $2 $3 >/dev/null; sleep 0.4
  done
  for spec in "togempire 533 418" "togships 572 418" "togcolonies 611 418"; do
    set -- $spec
    DISPLAY=:9 ./tools/xsend Ascendancy click $2 $3 >/dev/null; sleep 0.4
  done
  grep -c "ui cam yaw" /tmp/t411_witness.log
}
CAM_LINES=$(dial_walk)
SEAMS=$(grep -c "map-ctl seam" /tmp/t411_witness.log)
echo "dial walk: cam lines $CAM_LINES (expect >=8: 7 movers + togLanes), toggle seams $SEAMS (expect 3)"
if [ "$CAM_LINES" -lt 8 ] || [ "$SEAMS" -lt 3 ]; then
  echo "VERDICT FAIL: dial walk (cam $CAM_LINES seams $SEAMS)"; VERDICT=1
fi
kill -9 $UI 2>/dev/null || true
exit $VERDICT
