#!/usr/bin/env bash
# t404 witness: CLICK-SFX LAW (D13 "clicking anywhere in the galaxy map makes
# a laser-fire sound"). Runs the campaign UI on Xvfb with --audio-trace (the
# t388b wiring instrument: one "sfx <name>" line per played sound), then:
#   map click (empty area)      -> logs "ui click map" with NO sfx line after
#   STATUS rail press           -> "sfx click08" adjacent to the screen switch
#   NEXT TURN press             -> "sfx click08" right after "ui click next-turn"
# and laser01 appears ZERO times in the whole log. The census decides.
# t437 UPDATE: the expected press sound is "button" (soundfx manifest[0]) —
# the windows.txt SOUNDCHANNEL value the vendor's press handler plays
# (store 0x57e7a -> record+0x59 = HIWORD dword+0x57; 0 on all 119 file lines;
# docs/re/_wip_t437.md F1-F6, audio.md S6.9). click08 was off-manifest and a
# silent no-op, so the click08 expectation here could never have proven sound
# actually played; "button" is the cited sample (audio.md S6.9).
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/t404_shots}
DISP=${DISP:-:97}
rm -rf "$OUT"; mkdir -p "$OUT"
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
# Silent-degrade law nulls the AudioEngine if the device fails to open, and
# the trace rides on the engine — force SDL's dummy driver so the wiring
# instrument always exists (no real sound needed; hearing stays the user's).
SDL_AUDIODRIVER=dummy DISPLAY=$DISP "$BIN" --ui --campaign 1 --seed 5 --audio-trace >"$OUT/app.log" 2>&1 &
APP=$!
sleep 3
X() { DISPLAY=$DISP ./tools/xsend "Ascendancy" "$@"; sleep 1; }
X 318 335            # RESUME -> campaign map (title click08 expected)
X 100 240            # EMPTY map click (inside COSMOSWnd, no other rect)
X 553 145            # STATUS rail button centre -> screen switch + click08
X key Escape         # back to map
X 511 67             # NEXT TURN centre -> advance + click08 (map-only gate;
                     # seed 5 ends the campaign after turn 1 — exit is fine,
                     # the census reads the log after kill)
kill $APP 2>/dev/null; kill $XV 2>/dev/null
sleep 1

python3 - "$OUT/app.log" <<'EOF'
import sys
lines = open(sys.argv[1], errors="replace").read().splitlines()
fails = []

def idx(prefix, start=0):
    for i in range(start, len(lines)):
        if lines[i].startswith(prefix):
            return i
    return -1

resume = idx("ui title click RESUME")
mapc = idx("ui click map", resume + 1 if resume >= 0 else 0)
rail = idx("ui screen map ->", mapc + 1 if mapc >= 0 else 0)  # "... (STATUS)"
nt = idx("ui click next-turn", rail + 1 if rail >= 0 else 0)
print("markers resume/map/rail/nt at", resume, mapc, rail, nt)
if min(resume, mapc, rail, nt) < 0:
    print("VERDICT FAIL INTERACTIONS DID NOT ROUTE (see log)"); sys.exit(1)

def sfx_at(i):
    return lines[i] if 0 <= i < len(lines) and lines[i].startswith("sfx ") else None

# printf/play ORDER law (read from ui.cpp): the map-click and rail branches
# play BEFORE their printf; next-turn prints BEFORE playing. So a map-click
# sound would sit on the line BEFORE "ui click map", the rail's click on the
# line BEFORE the switch line, and next-turn's click AFTER its marker.
# 1) MAP CLICK SILENT.
before_map = sfx_at(mapc - 1)
print("sfx line before map click:", before_map)
if before_map: fails.append("MAP CLICK PLAYED " + before_map)
stray = [l for l in lines[mapc + 1:rail - 1] if l.startswith("sfx ")]
print("stray sfx between markers:", stray)
if stray: fails.append("STRAY SOUND DURING MAP->RAIL WINDOW")
# 2) RAIL PRESS click08.
r = sfx_at(rail - 1)
print("sfx before rail switch:", r)
if r != "sfx button": fails.append("RAIL PRESS NOT button")
# 3) NEXT TURN click08.
n = sfx_at(nt + 1)
print("sfx after next-turn:", n)
if n != "sfx button": fails.append("NEXTTURN NOT button")
# 4) laser01 anywhere = the D13 regression is still alive.
laser = [l for l in lines if l.startswith("sfx ") and "laser" in l]
print("laser lines:", laser)
if laser: fails.append("LASER01 STILL PLAYED")
print("VERDICT", "FAIL " + "; ".join(fails) if fails else "PASS")
EOF
echo DONE
