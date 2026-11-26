#!/usr/bin/env bash
# tRS-V2w GROWN-FILL WITNESS (research apply law docs/re/research.md S9(e) +
# income-law.md tRS-V2w block; diagnosis docs/re/_wip_tRSV2.md P11). The
# tRS-V2p grown leg failed because the PLAYER research bucket is legitimately
# ~0 for the first ~80 turns (home RES channel 0, T34 law): 15 manual NEXT
# TURNs cannot reach a grown q. This witness lets the port's own kBuildOrder
# policy build Laboratory (RES 1/turn) via --autoplay (250 ms/turn, ui.cpp:
# 1211 advanceOnce — no clicks needed), and POLLS app.log for the grown fill
# line "ui research fill <row> <q>" with q>2 before the progressed shot.
# Stages: before (q=0) -> sliver (select, q=2) -> progressed (q>2, autoplay).
# Census = scripts/tRSV2p_census.py UNCHANGED (it asserts exactly these log
# legs + content growth). Scratch Xvfb :99, kill BY PID (host law).
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/trsv2w_shots}
DISP=${DISP:-:99}
PY=${PY:-$HOME/tools/revenv/bin/python}
rm -rf "$OUT"; mkdir -p "$OUT"
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
# --campaign N in --ui mode IS the TURN CAP (main.cpp -> ui.cpp quit at
# played>=N). 400 covers Laboratory completion (~t77 seed 5) + grown q;
# --autoplay advances a turn every 250 ms; --dbg-res prints the per-owner
# bucket/add/prog channel (tRS-V2w instrument) for the diagnosis log.
DISPLAY=$DISP SDL_AUDIODRIVER=dummy "$BIN" --ui --autoplay --campaign 400 \
  --seed 5 --dbg-res >"$OUT/app.log" 2>&1 &
APP=$!
sleep 3
X() { DISPLAY=$DISP ./tools/xsend "Ascendancy" "$@"; sleep 1; }
shot() { sleep 0.3; DISPLAY=$DISP import -window root -crop 640x480+0+0 +repage "$OUT/$1.png" 2>>"$OUT/app.log"; }
die() { kill $APP 2>/dev/null; kill $XV 2>/dev/null; echo "VERDICT FAIL ($1)"; exit 1; }
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
shot before
CENTER_LINE=$(grep "ui research center " "$OUT/app.log" | grep available | tail -1)
if [ -z "$CENTER_LINE" ]; then
  echo "FAIL  app logged no 'ui research center ... available' line"
  die "no center line"
fi
# "ui research center <row> <x> <y> available" -> awk fields 4,5,6.
read -r CROW CX CY _ <<< "$(awk '{print $4, $5, $6, $7}' <<< "$CENTER_LINE")"
echo "target row=$CROW centre=($CX,$CY)"
X "$CX" "$CY"        # SELECT (the tRS-B1 hit square is centred on the word)
sleep 1
shot sliver
grep "ui research study" "$OUT/app.log" | tail -1 || true
# GROWN LEG: poll for a fill line q>2 on the selected row (Lab completion +
# apply law). Autoplay ~250 ms/turn; cap the wait at 150 s.
GROWN=""
for i in $(seq 150); do
  GROWN=$(grep -E "ui research fill $CROW ([3-9]|[1-9][0-9])" "$OUT/app.log" | tail -1)
  [ -n "$GROWN" ] && break
  kill -0 $APP 2>/dev/null || die "app exited before grown fill line (turn $(grep -c 'dbg-res' "$OUT/app.log" 2>/dev/null | head -1) dbg lines)"
  sleep 1
done
if [ -z "$GROWN" ]; then die "no grown fill line within 150 s"; fi
echo "grown leg: $GROWN"
shot progressed
kill $APP 2>/dev/null
grep "dbg-res" "$OUT/app.log" | grep "owner 0 " | tail -5
"$PY" scripts/tRSV2p_census.py "$OUT" "$CX" "$CY" "$CROW"
rc=$?
kill $XV 2>/dev/null
echo "VERDICT $([ $rc -eq 0 ] && echo PASS || echo FAIL)"
exit $rc
