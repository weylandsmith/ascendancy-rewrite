#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

# Regenerate docs/PLAYTHROUGH.md from REAL runs of the CURRENT binary.
# Every recorded block is actual captured output (head/tail-summarised
# turn lines are marked "(N more turns)"). Run after any change that
# affects campaign dynamics. Fails if any run misses its expected line.
set -eu
cd "$(dirname "$0")/.."
BIN=./rewrite/build/ascendancy
OUT=docs/PLAYTHROUGH.md
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

capture() { # capture <name> <expected-substring> <cmd...>
  local name=$1 expect=$2; shift 2
  if ! "$@" >"$TMP/$name.log" 2>&1; then
    echo "RUN FAILED: $name"; cat "$TMP/$name.log"; exit 1
  fi
  grep -q "$expect" "$TMP/$name.log" || { echo "MISSING '$expect' in $name"; cat "$TMP/$name.log"; exit 1; }
}

# T41: budgets 600 -> 1200. The faithful CB-only start (income-law.md T40)
# lengthened seed-2024 to Control t729 (CLI); all three seeds FINITE.
# t89 RE-VERIFY (deterministic combat, no hit roll — docs/re/combat.md S2j):
# 2024 Control t777, 42 Extinct t581, 13 Extinct t503; test seeds 1/2/2024
# also finite (Control t842 / t677 / t777, CLI --campaign 1200).
# t93 picker law re-measured: 2024 t737 / 42 t688 / 13 t503 / 1 t836 / 2 t657.
# t100 cadence law re-measured: IDENTICAL (2024 t737 / 42 t688 / 13 t503) —
# the FFA smoke seeds' AI abilities do not gate these seeds' victories.
# t291 BLAST-RADIUS RETRAP (cited two-thirds Control law, docs/re/_wip_t290.md
# S1 -> campaign.cpp end-ctrl arm): the bar moved from >1/2 owned to
# V >= floor(2T/3)+1 (=34/50) on the FLOOD metric, so Control wins land much
# later. CLI --campaign 1600 measured this session: seed 1 Control t1337,
# seed 2 Control t1427, seed 13 Extinct t747, seed 42 Extinct t979, and seed
# 2024 FLIPS Control t1255 -> EXTINCT t1555 (owner 3 wipes the player before
# V ever reaches 34 — 46% was never a vendor win). Budgets 1200 -> 1600
# (t202b precedent: pacing windows widen, the law never bends); run A is now
# seed 2024 at 1600 (documents the flip honestly) and run B seed 1 (the
# Control exemplar the gate greps for). All runs FINITE.
capture A "VICTORY"          "$BIN" --headless --campaign 1600 --seed 2024
capture B "VICTORY"          "$BIN" --headless --campaign 1600 --seed 23
capture C "VICTORY"          xvfb-run -a "$BIN" --campaign 1600 --seed 13
capture D "ui ok: turn 3"    xvfb-run -a "$BIN" --ui --resume --campaign 3 --autoplay --seed 9
capture E "audio ok: 85 sfx chunks, music 8191719 B" \
        env SDL_AUDIODRIVER=dummy xvfb-run -a "$BIN" --ui --resume --audio --campaign 1 --autoplay --seed 4
# F: real injected input (own Xvfb so xsend can find the window)
Xvfb :77 -screen 0 640x480x24 >/dev/null 2>&1 & XV=$!
sleep 1
DISPLAY=:77 "$BIN" --ui --campaign 1 --seed 5 >"$TMP/F.log" 2>&1 & APP=$!
sleep 2
# t385: title screen first — RESUME button (vendor 159,320-477,350)
DISPLAY=:77 ./tools/xsend "Ascendancy" 318 335 2>/dev/null || true
sleep 1
grep -q 'ui title click RESUME -> campaign' "$TMP/F.log" || { echo "F: title RESUME never routed"; cat "$TMP/F.log"; exit 1; }
DISPLAY=:77 ./tools/xsend "Ascendancy" 510 66 2>/dev/null || true
wait $APP
kill $XV 2>/dev/null
grep -q 'ui click next-turn' "$TMP/F.log" || { echo "F: injected click never reached app"; cat "$TMP/F.log"; exit 1; }
grep -q 'ui ok: turn 1' "$TMP/F.log" || { echo "F: click did not advance turn"; cat "$TMP/F.log"; exit 1; }

summarize() { # keep first 5 .. last 4 lines of stdin, mark the elision
  awk '{l[NR]=$0} END{
    if(NR>9){ for(i=1;i<=5;i++) print l[i]; printf "  ... (%d lines elided)\n", NR-9; for(i=NR-3;i<=NR;i++) print l[i] }
    else for(i=1;i<=NR;i++) print l[i]
  }'
}

{
echo "# Headless playthrough record"
echo
echo "Regenerated $(date -Iseconds) by scripts/record_playthrough.sh from the"
echo "current binary. Victory conditions and their vendor files: docs/re/turnloop.md §1."
echo
for r in A B C; do
  case $r in
    A) title="Run A — headless, seed 2024 (t295 home draw: Extinct t285 — uniform homes put real lethal neighbours on the player; the old spread-BFS never could)"; cmd="$BIN --headless --campaign 1600 --seed 2024";;
    B) title="Run B — headless, seed 23 (Control exemplar t1406 under the t295 home draw; t291's seed-1 exemplar re-drew to Extinct t266)";   cmd="$BIN --headless --campaign 1600 --seed 23";;
    C) title="Run C — Xvfb/X11, seed 13";   cmd="xvfb-run -a $BIN --campaign 1600 --seed 13";;
  esac
  echo "## $title"
  echo
  echo '```'
  echo "\$ $cmd"
  summarize < "$TMP/$r.log"
  echo '```'
  echo
done
echo "## Run D — UI under Xvfb, autoplay 3 turns (gate 4c)"
echo
echo '```'
echo "\$ xvfb-run -a $BIN --ui --campaign 3 --autoplay --seed 9"
grep -E 'archives|SDL|ui ok' "$TMP/D.log"
echo '```'
echo
echo "## Run E — audio boot (gate 4d): all 86 vendor SFX + theme00 via SDL2_mixer"
echo
echo '```'
echo "\$ SDL_AUDIODRIVER=dummy xvfb-run -a $BIN --ui --audio --campaign 1 --autoplay --seed 4"
grep -E 'archives|SDL|audio ok|ui ok' "$TMP/E.log"
echo '```'
echo
echo "## Run F — injected X input drives a real turn (gate 4c-b)"
echo
echo '```'
echo "\$ $BIN --ui --campaign 1 --seed 5 &"
echo "\$ ./tools/xsend \"Ascendancy\" 510 66   # NEXT TURN button rect"
grep -E 'archives|SDL|ui click|ui ok' "$TMP/F.log"
echo '```'
echo "No --autoplay in F: the ONLY way the turn count advances is the injected click."
echo
cat <<'NOTES'
## What this shows / does not show

- SHOWS: seeded turn loop advances; mapgen, economy, research, production
  (planitem items incl. Shipyard), ship launch (gated on Shipyard +
  researched drive, docs/re/ships.md), combat-capture, diplomacy war
  table, victory files end-ctrl/end-xtnc both fire on real runs; same
  seed => byte-identical trace; boots under Xvfb x11; UI takes real
  injected input; audio loads every vendor sample.
- DOES NOT SHOW: original combat arithmetic (OQ-010 — capture model is
  documented-inferred), alliance-victory end-unit / home-world-capture
  end-capt (need R1 accept/capture bookkeeping), original AI build order,
  original sprites (OQ-005) and font (OQ-017), headerless sample-rate
  ground truth (OQ-006). Those stay open in docs/OPEN-QUESTIONS.md.
NOTES
} > "$OUT"
echo "wrote $OUT ($(wc -l < "$OUT") lines)"
