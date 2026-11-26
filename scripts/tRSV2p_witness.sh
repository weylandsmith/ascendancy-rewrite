#!/usr/bin/env bash
# tRS-V2p WITNESS (disk fill port; law docs/re/research.md S9, spec
# docs/re/_wip_tRSV2.md P7(4)). Stages on scratch seed 5:
#   before     = frontier disk, unselected (q=0 -> NO picture)
#   sliver     = after the app-logged click (q=2 -> 0.10 central sliver)
#   progressed = after >=1 turns of research on the topic (q grown)
# The click point is RE-DERIVED from "ui research center ..." (tRS-V1c law);
# the census asserts the LOGGED law values ("ui research fill <row> <q>")
# AND the content growth inside the disk (tRSV1d census lesson: content vs
# flat field bg, never brightness). Scratch Xvfb :99, kill BY PID (host law).
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/trsv2p_shots}
DISP=${DISP:-:99}
PY=${PY:-$HOME/tools/revenv/bin/python}
rm -rf "$OUT"; mkdir -p "$OUT"
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
# NOTE: in --ui mode main.cpp:656 passes --campaign N as the UI TURN CAP
# (quit when played>=N; ui.cpp:1215). N=1 kills the app on the first NEXT
# TURN click — the tRS-V2p first-draft mystery death. Cap at 12.
DISPLAY=$DISP SDL_AUDIODRIVER=dummy "$BIN" --ui --campaign 30 --seed 5 >"$OUT/app.log" 2>&1 &
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
shot before
CENTER_LINE=$(grep "ui research center " "$OUT/app.log" | grep available | tail -1)
if [ -z "$CENTER_LINE" ]; then
  echo "FAIL  app logged no 'ui research center ... available' line"
  kill $APP 2>/dev/null; kill $XV 2>/dev/null
  echo VERDICT FAIL; exit 1
fi
# "ui research center <row> <x> <y> available" -> awk fields 4,5,6.
read -r CROW CX CY _ <<< "$(awk '{print $4, $5, $6, $7}' <<< "$CENTER_LINE")"
echo "target row=$CROW centre=($CX,$CY)"
X "$CX" "$CY"        # SELECT (the tRS-B1 hit square is centred on the word)
sleep 1
shot sliver
grep "ui research study" "$OUT/app.log" | tail -1
# Advance up to 15 turns (q grows once progress >= runtimeCost/18; seed-5
# accrual is a few RES/turn so 5 turns was under the threshold - first
# draft banked). NEXT TURN is a MAP control (ui.cpp kNextTurnBtn gated on
# kScreenMap), so LEAVE research via Escape first, advance, then re-enter.
X key Escape         # Escape -> back to the campaign map (gate.sh:623 recipe)
sleep 1
for i in $(seq 15); do X 511 67; sleep 1; done   # NEXT TURN x15
X 553 223            # RESEARCH rail re-entry
sleep 1
shot progressed
kill $APP 2>/dev/null
"$PY" scripts/tRSV2p_census.py "$OUT" "$CX" "$CY" "$CROW"
rc=$?
kill $XV 2>/dev/null
echo "VERDICT $([ $rc -eq 0 ] && echo PASS || echo FAIL)"
exit $rc
