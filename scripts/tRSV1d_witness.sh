#!/usr/bin/env bash
# tRS-V1d WITNESS (seam TRSV1c-E closure): the DRAWN ring centre must land
# on the app's own logged centre word (== the vendor hit centre). Flow is
# the tRS-V1c witness nav (RESUME -> RESEARCH -> dolly out until a frontier
# disk is on-frame); then BEFORE the click, every logged "available" centre
# is checked against the pixels with tRSV1d_ringcentre_census.py.
# Scratch Xvfb :99, kill BY PID (host law).
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/trsv1d_shots}
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
X 553 223            # RESEARCH rail -> state 20
# tPF-7 HOLD LAW: the dolly runs ONLY while the button is held (vendor
# release msg 0x47d3b). clickdn = press-only, clickup = release-only; the
# hold is POLLED against the app's centre re-log (adaptive across cadences —
# the pump now runs at ResCam::kPumpMs=34, not the old 1000).
BEFORE_N=$(grep -c "ui research center " "$OUT/app.log")
X clickdn 578 449
for i in 1 2 3 4 40 80; do
  sleep 0.5
  NOW_N=$(grep -c "ui research center " "$OUT/app.log")
  [ "$NOW_N" -ge $((BEFORE_N + 8)) ] && break
done
X clickup 578 449
sleep 1
shot tree
# Collect EVERY logged available-centre line (latest report per row).
PTS=$("$PY" - <<'EOF'
import re
seen = {}
for line in open("/tmp/trsv1d_shots/app.log"):
    m = re.search(r"ui research center (\d+) (-?\d+) (-?\d+) available", line)
    if m: seen[int(m.group(1))] = (int(m.group(2)), int(m.group(3)))
print(" ".join(f"{x} {y}" for x, y in sorted(seen.values())))
EOF
)
if [ -z "$PTS" ]; then
  echo "FAIL  app logged no 'ui research center ... available' line"
  kill $APP 2>/dev/null; kill $XV 2>/dev/null
  echo VERDICT FAIL; exit 1
fi
echo "logged centres: $PTS"
"$PY" scripts/tRSV1d_ringcentre_census.py "$OUT/tree.png" $PTS
rc=$?
kill $APP 2>/dev/null; kill $XV 2>/dev/null
exit $rc
