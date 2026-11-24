#!/usr/bin/env bash
# tPL-V1f probe: find the working window-grab recipe on this host.
# Suspect: the campaign UI window title is "Ascendancy rewrite (P5a)"
# (ui.cpp:114), so `import -window Ascendancy` never matched.
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=/tmp/tplv1_probe
export DISPLAY=:98   # once, exported: per-command DISPLAY= prefixes did NOT
                     # reach `import` in this shell (unable to open X server '')
rm -rf "$OUT"; mkdir -p "$OUT"
Xvfb :98 -screen 0 640x480x24 >"$OUT/xvfb.log" 2>&1 &
XV=$!
sleep 2
DISPLAY=:98 "$BIN" --ui --campaign 1 --seed 5 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 4
echo "--- winpos Ascendancy:"
DISPLAY=:98 ./tools/winpos "Ascendancy" 2>&1
echo "--- xdotool-ish: try import by title candidates"
for T in "Ascendancy" "Ascendancy rewrite (P5a)"; do
  timeout 10 import -window "$T" "$OUT/t_${T:0:12}.png" 2>"$OUT/imp.err"
  echo "title='$T' exit=$? err=$(head -c 120 "$OUT/imp.err")"
done
echo "--- root grab size check:"
timeout 10 import -window root "$OUT/root.png" 2>>"$OUT/imp.err"
echo "root exit=$?"
python3 - <<'EOF'
import zlib, struct, os
def png_size(p):
    with open(p,'rb') as f: d=f.read()
    if len(d)<24: return None
    w,h=struct.unpack('>II', d[16:16+8]); return (w,h,len(d))
for f in sorted(os.listdir('/tmp/tplv1_probe')):
    if f.endswith('.png'):
        print(f, png_size('/tmp/tplv1_probe/'+f))
EOF
kill $APP 2>/dev/null; sleep 1; kill $XV 2>/dev/null
echo PROBE_DONE
