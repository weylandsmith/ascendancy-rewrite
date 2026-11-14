#!/usr/bin/env bash
# t387 dev check (bounded): title -> LOAD -> pick -> FRESHGAME -> child click
# -> RESUME -> NEXT TURN, all through ONE window (t385b law).
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
mkdir -p /tmp/t387_saves
python3 - <<'EOF'
import struct, os
os.makedirs("/tmp/t387_saves", exist_ok=True)
for name, day in [("07.sav", 300), ("41.sav", 1086), ("42.sav", 1200)]:
    open(f"/tmp/t387_saves/{name}","wb").write(struct.pack('<I',day)+b'x'*256)
open("/tmp/t387_saves/43.sav","wb").write(b"ab")  # torn slot
EOF
Xvfb :79 -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=:79 "$BIN" --ui --campaign 1 --seed 5 --saves /tmp/t387_saves >/tmp/t387_ui.log 2>&1 &
APP=$!
sleep 2
DISPLAY=:79 ./tools/xsend "Ascendancy" 318 375   # LOAD button (159,360)-(477,390)
sleep 1
DISPLAY=:79 ./tools/xsend "Ascendancy" 318 60    # load row 0 (46..75): 07.sav day 300
sleep 1
DISPLAY=:79 ./tools/xsend "Ascendancy" 318 84    # gutter on load screen / no-op at title
sleep 1
DISPLAY=:79 ./tools/xsend "Ascendancy" 318 375   # LOAD again
sleep 1
DISPLAY=:79 ./tools/xsend "Ascendancy" 318 170   # row 3 = 43.sav TORN (163..192)
sleep 1
DISPLAY=:79 ./tools/xsend "Ascendancy" key Escape   # cancel load -> Title
sleep 1
DISPLAY=:79 ./tools/xsend "Ascendancy" 318 295   # FRESHGAME -> raceconfig
sleep 1
DISPLAY=:79 ./tools/xsend "Ascendancy" 60 420    # GALAXY_MORE child button (7..122, 381..472)
sleep 1
DISPLAY=:79 ./tools/xsend "Ascendancy" 318 335   # RESUME -> campaign
sleep 1
DISPLAY=:79 ./tools/xsend "Ascendancy" 510 66    # NEXT TURN
wait $APP; RC=$?
kill $XV 2>/dev/null
echo "RC=$RC"
cat /tmp/t387_ui.log
