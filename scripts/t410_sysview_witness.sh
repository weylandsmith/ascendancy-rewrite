#!/usr/bin/env bash
# t410 witness: THE SYSTEM VIEW CHAIN (D13 "haven't found any way to pull up
# the system view screen, or planet view screen").
#   1. a STAR click on the map opens the System Display (state 16) — the
#      t338-measured entry law;
#   2. the state-16 console is live (TOGGRID toggles the grid line in the cam
#      log; ABANDON is REFUSED, never destructive);
#   3. clicking the COLONISED dot (orbit index 0 = centre + (60,0) at the
#      default systemCam zoom) opens the planet view (state 17) — planet.txt
#      info00 route one;
#   4. Escape unwinds ONE level per press: 17 -> 16 -> 1 (t252 law);
#   5. zero laser01 anywhere (t404 law holds through the new screen).
# The home-star pixel comes from the app's own diagnostic line
# ("ui home star <name> at X,Y") — display-only, zero rng.
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/t410_shots}
DISP=${DISP:-:97}
rm -rf "$OUT"; mkdir -p "$OUT"
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP SDL_AUDIODRIVER=dummy "$BIN" --ui --seed 5 --audio-trace >"$OUT/app.log" 2>&1 &
APP=$!
sleep 3
shot() { DISPLAY=$DISP import -window root "$OUT/$1.png" 2>>"$OUT/app.log"; sleep 1.2; }  # t408 SHOT-race law
X() { DISPLAY=$DISP ./tools/xsend "Ascendancy" "$@"; sleep 0.4; }  # t408 grep-race law
K() { DISPLAY=$DISP ./tools/xsend "Ascendancy" key "$1"; sleep 0.4; }

X 318 335            # RESUME -> campaign map
sleep 1
HS=$(grep -oE 'ui home star .* at [0-9]+,[0-9]+' "$OUT/app.log" | tail -1 | grep -oE '[0-9]+,[0-9]+$')
if [ -z "$HS" ]; then echo "NO HOME STAR DIAGNOSTIC"; fi
HX=${HS%,*}; HY=${HS#*,}
echo "home star pixel: $HX,$HY"

X "$HX" "$HY"        # STAR CLICK -> system view (state 16)
sleep 0.5
shot sys-open
X 572 418            # TOGGRID centre (557,403-587,433) -> grid toggles off
sleep 0.4
X 490 455            # ABANDON centre (479,442-548,472) -> REFUSED line
sleep 0.4
X 296 239            # colonised dot (index 0: centre 236,239 + (60,0)) -> state 17
sleep 0.5
shot planet-open
K Escape             # 17 -> 16
K Escape             # 16 -> 1
sleep 0.5
shot back-map

# ---- verdict ---------------------------------------------------------------
python3 - "$OUT/app.log" <<'PYEOF'
import sys
lines = open(sys.argv[1], errors='replace').read().splitlines()
def idx(pat, start=0):
    for i in range(start, len(lines)):
        if pat in lines[i]:
            return i
    return -1
fails = []
resume = idx("ui title click RESUME")
diag   = idx("ui home star", resume + 1 if resume >= 0 else 0)
entry  = idx("ui system view", diag + 1 if diag >= 0 else 0)
tog    = idx("grid 0", entry + 1 if entry >= 0 else 0)     # TOGGRID toggled OFF
aban   = idx("abandon refused", entry + 1 if entry >= 0 else 0)
planet = idx("-> planet view (state 17)", entry + 1 if entry >= 0 else 0)
esc1   = idx("Planet Display -> System Display (esc)", planet + 1 if planet >= 0 else 0)
esc2   = idx("System Display -> map (esc)", esc1 + 1 if esc1 >= 0 else 0)
laser  = [i for i, l in enumerate(lines) if "laser01" in l]
print("markers resume/diag/entry/toggrid/abandon/planet/esc1/esc2 at",
      resume, diag, entry, tog, aban, planet, esc1, esc2)
if resume < 0: fails.append("NO RESUME")
if diag < 0: fails.append("NO HOME-STAR DIAGNOSTIC")
if entry < 0: fails.append("STAR CLICK DID NOT OPEN SYSTEM VIEW")
if tog < 0: fails.append("TOGGRID DID NOT TOGGLE")
if aban < 0: fails.append("ABANDON DID NOT PRINT REFUSAL")
if planet < 0: fails.append("DOT CLICK DID NOT OPEN PLANET VIEW")
if esc1 < 0: fails.append("ESC FROM 17 DID NOT LAND ON 16")
if esc2 < 0: fails.append("ESC FROM 16 DID NOT LAND ON MAP")
if laser: fails.append("LASER01 PRESENT")
# ORDER law: the chain markers must appear in navigation order.
seq = [entry, tog, aban, planet, esc1, esc2]
if all(x >= 0 for x in seq) and seq != sorted(seq):
    fails.append("CHAIN MARKERS OUT OF ORDER")
for f in fails: print("FAIL:", f)
print("VERDICT", "FAIL" if fails else "PASS")
PYEOF

kill $APP 2>/dev/null; kill $XV 2>/dev/null
pkill -x ascendancy 2>/dev/null
echo DONE
