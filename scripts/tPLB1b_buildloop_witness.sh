#!/usr/bin/env bash
# tPL-B1b witness: THE TWO-STEP BUILD LOOP (D26 "double-clicking a square
# doesn't do anything"). Law docs/re/_wip_tPLB1.md F1-F10 + ui/planetview.h.
# Seed 5 scratch game ONLY (protected saves untouched). Flow:
#   RESUME -> STATUS -> row 0 (home planet; log carries CB cell + geometry)
#   -> PLBUILD opens the list -> click row 0 (Factory) = PICK (no order)
#   -> click a NON-adjacent tile  => "rejected ... no active neighbour"
#   -> re-pick -> click an ADJACENT tile => "ordered"
# Tile centres computed from the B/C grid tables (python below) — never
# eyeballed. Screenshots -> $OUT for USER grading.
set -u
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=${OUT:-/tmp/tplb1b_shots}
DISP=${DISP:-:99}
rm -rf "$OUT"; mkdir -p "$OUT"
Xvfb $DISP -screen 0 640x480x24 >/dev/null 2>&1 &
XV=$!
sleep 1
DISPLAY=$DISP "$BIN" --ui --campaign 1 --seed 5 >"$OUT/app.log" 2>&1 &
APP=$!
sleep 3
shot() { DISPLAY=$DISP import -window root "$OUT/$1.png" 2>>"$OUT/app.log"; }
X() { DISPLAY=$DISP ./tools/xsend "Ascendancy" "$@"; sleep 1; }
X 318 335            # RESUME -> campaign map
X 553 145            # STATUS rail
sleep 1
X 300 100            # row 0 -> home planet view (log: home-cb cell C size S)
sleep 1
# --- derive tile pixels from the log line (grid law, not eyeballing) ------
read -r ADJX ADJY MISX MISY < <(python3 scripts/tPLB1b_tilepx.py "$OUT/app.log")
echo "tiles adjacent=$ADJX,$ADJY nonadjacent=$MISX,$MISY"
# --- step 1: pick Factory (list row 0) ------------------------------------
X 547 57             # PLBUILD panel -> list opens
sleep 0.5
X 200 135            # row 0 = Factory (table order, req 255) -> PICK
shot after-pick
grep -q "ui planet pick Factory" "$OUT/app.log" \
  && echo "PASS pick sets the project (no order yet)" \
  || { echo "FAIL no pick line"; pass=0; }
# --- step 2a: NON-adjacent tile refuses -----------------------------------
X "$MISX" "$MISY"
sleep 0.5
shot refuse
# --- step 2b: re-pick, ADJACENT tile orders -------------------------------
X 547 57             # PLBUILD re-open
sleep 0.5
X 200 135            # pick Factory again
X "$ADJX" "$ADJY"
sleep 0.5
shot ordered
kill $APP 2>/dev/null; kill $XV 2>/dev/null
echo "--- log:"
grep -E "ui planet (pick|project|home-cb)" "$OUT/app.log"
pass=1
grep -q "ui planet pick Factory" "$OUT/app.log" \
  || { echo "FAIL  pick leg"; pass=0; }
grep -q "ui planet project .*rejected, cell refuses: no active neighbour" "$OUT/app.log" \
  && echo "PASS  non-adjacent tile REFUSES (rule G, 0x386fc)" \
  || { echo "FAIL  non-adjacent tile did not refuse"; pass=0; }
grep -q "ui planet project .*ordered" "$OUT/app.log" \
  && echo "PASS  adjacent tile ORDERS (active neighbour legal, 0x386fe)" \
  || { echo "FAIL  adjacent tile did not order"; pass=0; }
[ $pass = 1 ] && echo VERDICT PASS || echo VERDICT FAIL
exit $((1-pass))
