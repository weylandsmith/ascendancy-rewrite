#!/usr/bin/env bash
# tESC-1 EJECT WITNESS (D31). Vendor law (docs/re/_wip_tESC1.md): Escape at
# the campaign screen-stack bottom ejects to the TITLE menu with the
# campaign ALIVE in RAM (ESC arm fn 0x54d18@0x54e96 -> pop FUN_00057020;
# no exit path; t285 live witness). The port must do EXACTLY that:
#   eject leg  : 'ui quit cause=escape-key-at-bottom' + 'ui to title' +
#                'main: campaign -> title (campaign alive turn N)' AND the
#                process is STILL ALIVE afterwards.
#   re-entry   : click RESUME (msg 1/1) -> campaign runs again on the SAME
#                Campaign object (turn counter never rewinds) and the SAME
#                window (t385 law: a swap would eat this first click).
#   real exit  : Escape ejects again, then EXITTODOS ends the process.
# Per-leg assertion law (tPF-9): every leg greps its own log line.
# Exit codes: 0 = all legs pass; 1 = a leg failed (port deviates);
#             2 = harness/nav failure.
set -u
cd "$(dirname "$0")/.."
BIN=${BIN:-./rewrite/build/ascendancy}
OUT=${OUT:-/tmp/tesc1_eject}
DISP=${DISP:-:97}
rm -rf "$OUT"; mkdir -p "$OUT"
rm -f /tmp/.X97-lock /tmp/.X11-unix/X97 2>/dev/null
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
trap 'kill $XV 2>/dev/null; pkill -f "rewrite/build/ascendancy --data" 2>/dev/null; true' EXIT
sleep 1
export DISPLAY=$DISP
"$BIN" --data "${DATA:-$PWD}" --ui >"$OUT/app.log" 2>&1 &
APP=$!
sleep 4
kill -0 $XV 2>/dev/null || { echo "HARNESS FAIL: Xvfb dead"; exit 2; }
kill -0 $APP 2>/dev/null || { echo "HARNESS FAIL: app died at boot"; cat "$OUT/app.log"; exit 2; }
X()  { ./tools/xsend "Ascendancy" click "$@" 2>>"$OUT/xsend.log"; sleep 1; }
KEY() { ./tools/xsend "Ascendancy" key "$@" 2>>"$OUT/xsend.log"; sleep 1; }
fail() { echo "LEG FAIL: $1"; tail -8 "$OUT/app.log"; exit 1; }

# --- Begin path to the map (tNGB4 law, same nav as tPF1d_soak) ---
X 320 60; X 318 295; X 566 422; sleep 2; X 320 450; sleep 1
grep -q "newgame live" "$OUT/app.log" || { echo "NAV FAIL: no newgame live line"; tail -5 "$OUT/app.log"; exit 2; }
grep -m1 "newgame live" "$OUT/app.log"

# --- LEG 1: one Escape at the bare map ejects WITHOUT killing the process
KEY Escape
sleep 1
alive() { kill -0 $APP 2>/dev/null; }
grep -q 'ui quit cause=escape-key-at-bottom' "$OUT/app.log" || fail "no escape cause line"
grep -q '^ui to title' "$OUT/app.log" || fail "no 'ui to title' handoff line"
grep -q 'main: campaign -> title (campaign alive turn' "$OUT/app.log" || fail "no main re-entry line"
alive || fail "process DIED on escape (port still exits at the bottom)"
echo "LEG1 ok: eject to title, process alive"

# --- LEG 2: RESUME re-enters the SAME campaign on the SAME window.
# The click itself is the window-law witness: on a swapped window the
# t385 law says this FIRST synthetic click is dropped -> no log line.
X 318 335
grep -q 'ui title click RESUME -> campaign' "$OUT/app.log" || fail "RESUME click did not re-enter campaign (window law broken?)"
alive || fail "process died on re-entry"
echo "LEG2 ok: RESUME re-entered campaign (click landed on reused window)"

# --- LEG 3: turn the resumed campaign (proves it is the live object) ---
X 511 67
grep -q 'ui click next-turn' "$OUT/app.log" || fail "resumed campaign inert"
echo "LEG3 ok: resumed campaign advances"

# --- LEG 4: eject again, then EXITTODOS ends the process for real ---
KEY Escape
sleep 1
grep -q 'main: campaign -> title' "$OUT/app.log"
[ "$(grep -c 'main: campaign -> title' "$OUT/app.log")" = 2 ] || fail "second eject missing"
alive || fail "process died on second eject"
X 318 455   # EXITTODOS
sleep 2
alive && fail "EXITTODOS did not end the process"
grep -q 'ui title exit' "$OUT/app.log" || fail "no title exit line"
echo "LEG4 ok: EXITTODOS exits; process gone"
echo "tESC-1 EJECT WITNESS: ALL LEGS PASS"
