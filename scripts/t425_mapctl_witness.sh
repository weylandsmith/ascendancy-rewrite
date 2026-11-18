#!/bin/bash
# t425 MAP-CTL witness: every lower-right cluster button and every race
# filter slot must produce a LOGGED state change AND (for the visual ones)
# a frame diff. Prints VERDICT PASS/FAIL. Law: docs/re/_wip_t425.md F1b.
set -e
cd /home/hrethric/projects/ascendancy
pgrep -x Xvfb >/dev/null || { (Xvfb :9 -screen 0 1024x768x24 >/dev/null 2>&1 &); sleep 2; }
pkill -x ascendancy 2>/dev/null || true
sleep 1
DISPLAY=:9 SDL_AUDIODRIVER=dummy ./rewrite/build/ascendancy \
  --data /tmp/uishow --ui --campaign 1 --seed 5 > /tmp/t425_witness.log 2>&1 &
UI=$!
trap 'kill $UI 2>/dev/null || true' EXIT
sleep 4
# RESUME -> campaign map (t411 witness law: title button centre 318,335)
DISPLAY=:9 ./tools/xsend Ascendancy click 318 335 >/dev/null
sleep 2
shoot () { DISPLAY=:9 timeout 15 import -window root "$1"; }
WP=$(DISPLAY=:9 ./tools/winpos Ascendancy)
set -- $WP; X=$1; Y=$2; W=$3; H=$4
shoot /tmp/t425_base.png

clicks=( "572 418 togships" "611 418 togcolonies" "533 418 togempire" "494 418 toglanes" )
for c in "${clicks[@]}"; do
  set -- $c
  DISPLAY=:9 ./tools/xsend Ascendancy click "$1" "$2" >/dev/null
  sleep 1
done
# race filter: hide slot 5 (1-based; x 567..583 y 449..465) — RACE5CONTROL
# row bit 16 == 1<<4, so the mask reads 0xff ^ 0x10 = 0xef.
DISPLAY=:9 ./tools/xsend Ascendancy click 575 457 >/dev/null
sleep 1
shoot /tmp/t425_after.png

grep -c "lanes 0 ships 0 colonies 0 empire 1" /tmp/t425_witness.log >/dev/null \
  && echo "toggle-state line OK (all four flipped in one witness line)" \
  || { echo "MISSING combined toggle line:"; grep "ui cam yaw" /tmp/t425_witness.log | tail -3; exit 1; }
grep -c "ui race filter slot 5 mask 0xef" /tmp/t425_witness.log >/dev/null \
  && echo "race filter law OK (RACE5CONTROL bit 16 -> mask 0xef)" \
  || { echo "MISSING race filter line"; exit 1; }

~/tools/revenv/bin/python - "$X" "$Y" "$W" "$H" <<'EOF'
import sys, numpy as np
from PIL import Image
x,y,w,h = (int(v) for v in sys.argv[1:5])
a = np.asarray(Image.open('/tmp/t425_base.png').convert('RGB'))[y:y+h, x:x+w]
b = np.asarray(Image.open('/tmp/t425_after.png').convert('RGB'))[y:y+h, x:x+w]
fails=[]
# t425b FACE LAW (docs/re/_wip_t425.md F5): visible slot paints the OUTLINED
# member (chromatic), filtered slot paints the GREY member (neutral). Check
# BOTH the chroma collapse on the clicked slot and the neighbour stability.
def chroma(img, x0):
    c = img[449:466, x0:x0+17].astype(int)
    return (c.max(axis=2) - c.min(axis=2)).mean()
def lum(img, x0):
    c = img[449:466, x0:x0+17].astype(float)
    return (0.299*c[:,:,0] + 0.587*c[:,:,1] + 0.114*c[:,:,2]).mean()
ca, cb = chroma(a, 567), chroma(b, 567)
la, lb = lum(a, 567), lum(b, 567)
print(f"slot5 chroma {ca:.1f} -> {cb:.1f}; lum {la:.1f} -> {lb:.1f}")
if not ca > 12: fails.append(f"slot5 not chromatic while visible (chroma {ca:.1f})")
if not cb < 4: fails.append(f"slot5 still chromatic after filtering (chroma {cb:.1f})")
if lb > la: fails.append(f"slot5 did not dim ({la:.1f}->{lb:.1f})")
# the OTHER slots must be UNCHANGED (the mask touches only slot 5)
oa, ob = chroma(a, 479), chroma(b, 479)
print(f"slot1 chroma {oa:.1f} -> {ob:.1f}")
if abs(ob-oa) > 2: fails.append(f"slot1 changed too ({oa:.1f}->{ob:.1f})")
# 3) the field must still render (non-trivial content; lanes toggled back ON
#    is NOT part of this witness — the four clicks leave lanes OFF, ships ON,
#    colonies OFF, empire ON; field pixels must still exist: stars draw
#    unconditionally, only ownership tint is layered).
field = a[10:468, 10:462]
n = int((b[10:468, 10:462].max(axis=2) > 60).sum())
print(f"after-field non-black px: {n}")
if n < 50: fails.append(f"field nearly empty after toggles ({n})")
print('VERDICT', 'FAIL: ' + '; '.join(fails) if fails else 'PASS')
sys.exit(1 if fails else 0)
EOF

# 4) CORNER POPUP ACTIVATION: on the map (screen stack empty) the Escape
#    chain quits — so a click inside the top-left popup rect must LOG
#    "ui corner exit popup click" AND end the process. (Popup drawn from
#    t419; the D17 defect was that clicking it did nothing.)
DISPLAY=:9 ./tools/xsend Ascendancy click 10 10 >/dev/null
sleep 2
if grep -c "ui corner exit popup click" /tmp/t425_witness.log >/dev/null; then
  echo "corner popup click OK"
else
  echo "MISSING corner popup click"; exit 1
fi
if kill -0 $UI 2>/dev/null; then echo "process still alive after popup click"; exit 1; fi
echo "process exited via popup click (quit-at-bottom chain)"
cp /tmp/t425_base.png /tmp/t425_after.png work/r1/loop/ 2>/dev/null || true
echo "shots -> work/r1/loop/t425_{base,after}.png"
