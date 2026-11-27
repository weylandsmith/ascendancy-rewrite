#!/usr/bin/env bash
# tWIN-1 WINDOW-COUNT WITNESS (D32 third leg). Vendor law: ONE SDL window
# for the whole session (t385 single-window law; the title<->campaign
# handoff exists precisely so no second window is ever created). User
# symptom: escaping from the galaxy screen to the title OPENS A NEW WINDOW.
# Law + defect site: docs/re/_wip_tWIN1.md W1.
#
# Shape: --ui no --seed (tPF1d soak nav), Begin to the map, ONE Escape
# (tESC-1 eject leg), then assert the process still owns EXACTLY ONE
# Ascendancy window; then RESUME + NEXT TURN + second eject + final count.
# Window identity is read with `xwininfo -root -tree` (recursive; catches
# UNMAPPED zombie windows that a mapped-only search would miss) filtered to
# '"Ascendancy"' titles.
# Exit codes: 0 = one window at every checkpoint; 1 = a checkpoint saw != 1
#             (the defect); 2 = harness/nav failure.
set -u
cd "$(dirname "$0")/.."
BIN=${BIN:-./rewrite/build/ascendancy}
OUT=${OUT:-/tmp/twin1_windows}
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

# Count Ascendancy windows (recursive tree; every SDL window shows as a
# quoted title line). Filter '"Ascendancy' = opening quote + prefix, which
# matches BOTH window-title families the port uses: "Ascendancy" (title)
# and "Ascendancy rewrite (P5a)" (campaign) — an exact-close-quote grep
# would miss the zombie. Retries briefly so a just-created window has time
# to appear. Full tree banked per checkpoint for provenance.
ckpt() {  # ckpt <name> <expected>
    local n=0 i i=1
    for i in 1 2 3; do
        xwininfo -root -tree >"$OUT/tree_$1.txt" 2>/dev/null
        n=$(grep -c '"Ascendancy' "$OUT/tree_$1.txt")
        [ "$n" -ge "$2" ] && break
        sleep 1
    done
    echo "CHECKPOINT $1: windows=$n (expected $2)"
    grep '"Ascendancy' "$OUT/tree_$1.txt" | sed 's/^/    /'
    [ "$n" = "$2" ] || { echo "WINDOW-COUNT FAIL at $1: $n != $2"; return 1; }
    return 0
}

# --- Begin path to the map (tNGB4 law, same nav as tESC1_eject_witness) ---
X 320 60; X 318 295; X 566 422; sleep 2; X 320 450; sleep 2
grep -q "newgame live" "$OUT/app.log" || { echo "NAV FAIL: no newgame live line"; tail -5 "$OUT/app.log"; exit 2; }
ckpt "map" 1 || exit 1

# --- LEG 1: one Escape at the bare map ejects to title; ONE window only ---
KEY Escape; sleep 2
grep -q '^ui to title' "$OUT/app.log" || fail "no 'ui to title' handoff line"
grep -q 'main: campaign -> title (campaign alive turn' "$OUT/app.log" || fail "no main re-entry line"
kill -0 $APP 2>/dev/null || fail "process DIED on escape"
ckpt "title-after-eject" 1 || exit 1

# --- LEG 2: RESUME re-enters, still ONE window ---
X 318 335
grep -q 'ui title click RESUME -> campaign' "$OUT/app.log" || fail "RESUME click did not re-enter"
ckpt "campaign-after-resume" 1 || exit 1

# --- LEG 3: turn the live campaign, eject again, final count ---
X 511 67
grep -q 'ui click next-turn' "$OUT/app.log" || fail "resumed campaign inert"
KEY Escape; sleep 2
[ "$(grep -c 'main: campaign -> title' "$OUT/app.log")" = 2 ] || fail "second eject missing"
ckpt "title-after-second-eject" 1 || exit 1

# --- clean up via EXITTODOS ---
X 318 455; sleep 2
kill -0 $APP 2>/dev/null && fail "EXITTODOS did not end the process"
echo "tWIN-1 WINDOW WITNESS: ALL CHECKPOINTS PASS (one window the whole session)"
