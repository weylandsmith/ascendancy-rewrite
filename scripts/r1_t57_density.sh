#!/usr/bin/env bash
# r1_t57_density.sh — OQ-012(a) ONE-OBSERVATION probe driver (outer).
# One click of the new-game "Star^Density" control during the SETUP screen,
# timed between the inner's New Game tour click (t=75, opens setup) and the
# first start click (t>=100). Measurement = star count in the inner's
# entry-checkpoint RAM (fresh map after grid-hash change) vs the banked
# default 50. count!=50 => control works + value recorded; count==50 =>
# ambiguous, record once, stop (exit-1 discipline, no spiral).
# Geometry law: windows.txt coords are ABSOLUTE root coords (NEXTTURN
# 474..548/52..82 center == measured End-Turn (511,67); FRESHGAME
# 280..310 center == banked New-Game click y=293). GALAXY_MORE
# 7..122/381..472 -> center (65,427).
set -u
OUT="${OUT:?OUT required}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DISP="${DISPNO:-97}"

snap() {
  local newest
  newest=$(ls -t "$OUT"/save/*.sav 2>/dev/null | head -1)
  [ -n "$newest" ] && cp "$newest" "$OUT/setup/$1.sav" && echo "$(date +%T) snap $1" >>"$OUT/dens.log"
}
mkdir -p "$OUT/setup"

# wait for the New Game tour click to have fired (setup screen opening)
for i in $(seq 1 60); do
  grep -q "318 293" "$OUT/click.log" 2>/dev/null && break
  sleep 3
done
sleep 8
snap presetup
DISPLAY=":$DISP" "$ROOT/tools/xsend" "DOSBox-X" 65 427 >>"$OUT/dens.log" 2>&1
echo "$(date +%T) clicked density control 65,427 ONCE" >>"$OUT/dens.log"
sleep 12; snap postclick1
sleep 12; snap postclick2

# wait for campaign entry (inner logs 'campaign ENTERED' + entry checkpoint)
for i in $(seq 1 60); do
  grep -q "campaign ENTERED" "$OUT/click.log" 2>/dev/null && { echo "$(date +%T) entered" >>"$OUT/dens.log"; sleep 6; break; }
  sleep 4
done
echo "$(date +%T) t57 driver done" >>"$OUT/dens.log"
