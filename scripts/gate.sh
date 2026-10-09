#!/usr/bin/env bash
# Quality gate for the Ascendancy RE goal loop. Deterministic, no network.
# Exit 0 = healthy. Output is fed verbatim to the agent on failure.
set -u
cd "$(dirname "$0")/.."
ROOT=$(pwd)
fail=0
note() { echo "[gate] $*"; }
err()  { echo "[gate FAIL] $*"; fail=1; }

# 1. Originals untouched (P0 invariant) — checksum manifest
MAN="$ROOT/docs/BASELINE.sha256"
if [ ! -f "$MAN" ]; then
  (cd "$ROOT/game" && sha256sum * > "$MAN") && note "created baseline manifest"
fi
(cd "$ROOT/game" && sha256sum -c "$MAN" --quiet 2>&1) | grep -v ': OK' && err "game/ files modified!"

# 2. Extractor round-trip works
TMP=$(mktemp -d)
if /usr/bin/python3 "$ROOT/scripts/cob.py" extract "$ROOT/game/ascend00.cob" "$TMP/a0" >/dev/null 2>&1; then
  n=$(ls "$TMP/a0" | wc -l); [ "$n" -ge 50 ] || err "extractor regression: only $n files from ascend00 (expect >=50)"
else
  err "cob.py extract failed on ascend00.cob"
fi
rm -rf "$TMP"

# 3. Docs integrity
for f in docs/PLAN.md docs/STATE.md docs/FINDINGS.md; do
  [ -s "$ROOT/$f" ] || err "$f missing or empty"
done

# 3b. P1b invariant: .bin tables parse at stride 24, and the .cob extractor must
# emit ALL directory entries (it silently dropped the last file of every archive
# until 2026-10-03, so count is asserted, not trusted).
if /usr/bin/python3 "$ROOT/scripts/table_probe.py" --out /tmp/gate_tables.md >/tmp/gate_probe.log 2>&1; then
  [ "$(ls "$ROOT/extracted/ascend00" | wc -l)" -ge 54 ] || err "ascend00 extracted <54 files"
  [ "$(find "$ROOT/extracted/ascend02" -type f | wc -l)" -ge 89 ] || err "ascend02 extracted <89 files"
  [ -f "$ROOT/extracted/ascend02/data/intro65a.flc" ] || err "ascend02/data/intro65a.flc missing (last-entry regression)"
else
  tail -20 /tmp/gate_probe.log; err "table_probe.py failed (.bin stride invariant broken?)"
fi

# 3c. P1c invariant: every .shp container parses (magic 1.10, table size
# 8*(N+1), monotonic pointer slots, spans covering the data area). The probe
# aborts on any violation; here we additionally pin the corpus size so a
# silently-shrunk extracted/ tree cannot pass.
NSH=$(find "$ROOT/extracted" -name '*.shp' -type f | wc -l)
[ "$NSH" -ge 208 ] || err "only $NSH .shp files in extracted/ (expect >=208)"
if /usr/bin/python3 "$ROOT/scripts/shp_probe.py" --out /tmp/gate_shp.md >/tmp/gate_shp.log 2>&1; then
  grep -q 'parsed 208/208 libraries' /tmp/gate_shp.log \
    || { tail -20 /tmp/gate_shp.log; err "shp_probe did not parse all 208 libraries"; }
else
  tail -20 /tmp/gate_shp.log; err "shp_probe.py failed (.shp container invariant broken?)"
fi

# 3d. P2-input invariant: all 21 race*.dip parse with the SAME DIPVALUES key
# set (that identity is what makes per-race AI data-driven rather than 21
# bespoke scripts). Also pins the corpus size.
if /usr/bin/python3 "$ROOT/scripts/dip_probe.py" --out /tmp/gate_dip.md >/tmp/gate_dip.log 2>&1; then
  grep -q 'OK: 21/21 dips parsed' /tmp/gate_dip.log \
    || { tail -20 /tmp/gate_dip.log; err "dip_probe did not parse all 21 dips"; }
else
  tail -20 /tmp/gate_dip.log; err "dip_probe.py failed (.dip grammar broken?)"
fi

# 3e. P1e invariant: FLIC chunk chains tile their files exactly; audio/font/
# hazard/tmp inventory regenerates.
if /usr/bin/python3 "$ROOT/scripts/media_probe.py" --out /tmp/gate_media.md >/tmp/gate_media.log 2>&1; then
  grep -q 'OK: 2 flic exact-tiled' /tmp/gate_media.log \
    || { tail -20 /tmp/gate_media.log; err "media_probe did not verify both FLICs"; }
else
  tail -20 /tmp/gate_media.log; err "media_probe.py failed (FLIC/audio inventory)"
fi

# 3f. P1d invariant: the golden save is byte-pinned by size and the measured
# stride-75 tech chain still resolves.
if /usr/bin/python3 "$ROOT/scripts/gam_probe.py" --out /tmp/gate_gam.md >/tmp/gate_gam.log 2>&1; then
  grep -q 'stride=75' /tmp/gate_gam.log \
    || { tail -20 /tmp/gate_gam.log; err "gam_probe stride changed (was 75)"; }
else
  tail -20 /tmp/gate_gam.log; err "gam_probe.py failed (resume.gam correlation)"
fi

# 3g. P1f invariant: ascend00 stays CP437-safe (few high bytes) and the exe
# still exposes its 34 module names (the P2 subsystem spine).
if /usr/bin/python3 "$ROOT/scripts/text_probe.py" --quiet >/dev/null 2>/tmp/gate_text.log; then
  grep -q 'modules=34' /tmp/gate_text.log \
    || { cat /tmp/gate_text.log; err "text_probe module count changed (was 34)"; }
else
  cat /tmp/gate_text.log; err "text_probe.py failed"
fi

# 3h. P2 loader-model invariant: docs/re/loader.md exists (it is the P2
# foundation every subsystem spec cites), the Ghidra bootstrap sources are
# tracked, and the base-refutation probes still RUN (exit 0 = a base was found
# later, which is an upgrade; exit 2 = refutation reproduced; anything else is
# a crash). These need capstone/venv python; skipped with a note if absent.
[ -s "$ROOT/docs/re/loader.md" ] || err "docs/re/loader.md missing (P2 foundation)"
[ -s "$ROOT/docs/BLOCKED.md" ] || err "docs/BLOCKED.md missing"
[ -s "$ROOT/scripts/ghidra/Seed2.java" ] || err "scripts/ghidra/Seed2.java missing"
VENV_PY="$HOME/tools/revenv/bin/python"
if [ -x "$VENV_PY" ] && [ -f "$ROOT/work/ascend_payload.bin" ] && [ -f "$ROOT/work/functions.tsv" ]; then
  "$VENV_PY" "$ROOT/scripts/vtable_base_test.py" >/tmp/gate_vtb.log 2>&1
  rc=$?
  [ "$rc" -le 2 ] || { tail -20 /tmp/gate_vtb.log; err "vtable_base_test.py crashed (rc=$rc)"; }
  "$VENV_PY" "$ROOT/scripts/c0_anchor_test.py" >/tmp/gate_c0.log 2>&1
  rc=$?
  [ "$rc" -le 2 ] || { tail -20 /tmp/gate_c0.log; err "c0_anchor_test.py crashed (rc=$rc)"; }
else
  note "venv/payload/functions.tsv not present: skipped loader-model probes"
fi

# 3i. P4 research invariant: docs/re/research.md exists and the probe
# reproduces its headline measurements on the shipped restree.txt (66 main
# rows + 40 ALL-CAPS variants, acyclic prereq graph). Pure stdlib.
[ -s "$ROOT/docs/re/research.md" ] || err "docs/re/research.md missing"
if /usr/bin/python3 "$ROOT/scripts/restree_probe.py" --out /tmp/gate_research.md --quiet; then
  grep -q 'data rows = \*\*106\*\* = \*\*66\*\*' /tmp/gate_research.md \
    || err "restree_probe: row counts drifted from 106=66+40"
  grep -q 'acyclic True' /tmp/gate_research.md \
    || err "restree_probe: prereq graph no longer acyclic"
else
  err "restree_probe.py crashed"
fi

# 3i2. OQ-004 invariant: .cob container grammar (docs/re/datafiles.md S3) —
# TOC parse + strictly-increasing blob offsets + ascend00 full 54/54 md5
# round-trip against extracted/ascend00. Pure stdlib; skips if game/*.cob
# absent (checksums are gate-checked separately; this never writes game/).
[ -s "$ROOT/docs/re/datafiles.md" ] || err "docs/re/datafiles.md missing (OQ-004 spec)"
if [ -f "$ROOT/game/ascend00.cob" ]; then
  if /usr/bin/python3 "$ROOT/scripts/cob_probe.py"; then
    :
  else
    err "cob_probe.py: .cob container grammar drifted (see docs/re/datafiles.md)"
  fi
else
  note "game/ascend00.cob absent: .cob grammar probe skipped"
fi

# 3j. P4 gizmos/economy invariant: the probes' asserted invariants (76 gizmos,
# 39 items, REQUIRES cross-range, sentinel counts) run on every gate; docs
# must exist and keep the sentinel fact visible.
[ -s "$ROOT/docs/re/gizmos.md" ] || err "docs/re/gizmos.md missing"
[ -s "$ROOT/docs/re/economy.md" ] || err "docs/re/economy.md missing"
if ! /usr/bin/python3 "$ROOT/scripts/gizmo_probe.py" --quiet; then
  err "gizmo_probe.py failed its own invariants"
fi
grep -q 'Interstellar Trucking' "$ROOT/docs/re/economy.md" \
  || err "economy.md lost the 254-sentinel record"

# 3k. P4 UI/species/diplomacy invariant: ui_probe asserts 132 windows, 15-key
# DIPVALUES identity across 21 races, 15 DA_ templates, 21 species, unique
# SA_ tokens; docs must exist and keep the parse-trap + roster facts visible.
[ -s "$ROOT/docs/re/ui.md" ] || err "docs/re/ui.md missing"
[ -s "$ROOT/docs/re/species.md" ] || err "docs/re/species.md missing"
[ -s "$ROOT/docs/re/diplomacy.md" ] || err "docs/re/diplomacy.md missing"
if ! /usr/bin/python3 "$ROOT/scripts/ui_probe.py" --quiet; then
  err "ui_probe.py failed its own invariants"
fi
grep -q 'PARSE TRAP' "$ROOT/docs/re/diplomacy.md" \
  || err "diplomacy.md lost the negative-value parse-trap record"
grep -q 'SA_SuperMarines' "$ROOT/docs/re/species.md" \
  || err "species.md lost the ability roster"

# 3m. Species special abilities (docs/re/abilities.md): the three-source
# roster invariant (help.txt abil blocks == raceNN.dip header tokens, race02
# tokenless -> title match) and the 14/7 charge split, via
# scripts/ability_probe.py; plus the binary firing at least one SA_ event.
[ -s "$ROOT/docs/re/abilities.md" ] || err "docs/re/abilities.md missing"
if ! /usr/bin/python3 "$ROOT/scripts/ability_probe.py"; then
  err "ability_probe.py failed (roster/charge invariant broken?)"
fi
if [ -x "$ROOT/rewrite/build/ascendancy" ]; then
  timeout 120 "$ROOT/rewrite/build/ascendancy" --headless --campaign 40 \
    --seed 11 >/tmp/gate_ability.log 2>&1
  rc=$?
  # exit 1 = "no victory after 40 turns" (expected here); >1 = crash.
  [ "$rc" -le 1 ] || { tail -10 /tmp/gate_ability.log; err "ability smoke crashed (rc=$rc)"; }
  grep -q 'SA_HealShips' /tmp/gate_ability.log \
    || { tail -10 /tmp/gate_ability.log; err "charged ability never fired by turn 40 (charge 30)"; }
fi

# 3n. Option-C R1 harness invariants (docs/BLOCKED.md runbook): the attempt
# harness must exist, must be executable, must NEVER reference a mount of the
# pristine game/ tree (the 12 GB incident's sibling risk is corrupting the
# baseline), and must kill only by exact process name. Static checks only —
# running an R1 attempt is the LOOP's job (STATE.md NEXT ACTION cadence),
# never the gate's (the gate must stay fast and side-effect-free).
[ -s "$ROOT/scripts/r1_attempt.sh" ] || err "scripts/r1_attempt.sh missing (option C cadence)"
[ -s "$ROOT/scripts/r1_tracer.py" ] || err "scripts/r1_tracer.py missing (option C cadence)"
grep -vE '^[[:space:]]*#' "$ROOT/scripts/r1_attempt.sh" | grep -Eq 'pkill[ ]+-f' \
  && err "r1_attempt.sh uses pkill -f (matches its own cmdline — killed a gate shell once)"
grep -vE '^[[:space:]]*#' "$ROOT/scripts/r1_attempt.sh" | grep -q 'ascendancy/game' \
  && err "r1_attempt.sh references the pristine game/ tree for dosbox (mount the work/r1 copy)"
grep -q 'time-limit' "$ROOT/scripts/r1_attempt.sh" \
  || err "r1_attempt.sh lost the dosbox -time-limit bound"
# attempts, if any ran, must have stayed bounded: every recorded log <= 64 KB
for f in "$ROOT"/work/r1/attempt-*/tracer.log; do
  [ -f "$f" ] || continue
  [ "$(stat -c%s "$f")" -le 65536 ] || { tail -c 400 "$f"; err "R1 tracer log >64KB: $f"; }
done
# 2026-10-05: the SAVESTATE route (docs/re/r1-savestate.md) carries the SAME
# invariants (cadence window abolished; safety per-run is not optional).
[ -s "$ROOT/scripts/r1_savestate.sh" ] || err "scripts/r1_savestate.sh missing (R1 savestate route)"
[ -s "$ROOT/scripts/r1_sav_scan.py" ] || err "scripts/r1_sav_scan.py missing (R1 savestate route)"
grep -vE '^[[:space:]]*#' "$ROOT/scripts/r1_savestate.sh" | grep -Eq 'pkill[ ]+-f' \
  && err "r1_savestate.sh uses pkill -f (exact-name only)"
grep -vE '^[[:space:]]*#' "$ROOT/scripts/r1_savestate.sh" | grep -q 'ascendancy/game' \
  && err "r1_savestate.sh references the pristine game/ tree for dosbox (copy to work/r1 first)"
grep -q 'time-limit' "$ROOT/scripts/r1_savestate.sh" \
  || err "r1_savestate.sh lost the dosbox -time-limit bound"

# 3q. POINTER LAW confirmation (docs/re/r1-savestate.md, CLOSED 2026-10-05i):
# run the law battery against any captured slot present. Skips with a note
# when no captures exist (work/ is not committed) so a fresh clone still gates.
SAVDIR=""
for d in "$ROOT"/work/r1/r1sav-*/save; do
  [ -d "$d" ] && SAVDIR="$d"   # keep scanning: last existing wins
done
if [ -n "$SAVDIR" ] && ls "$SAVDIR"/*.sav >/dev/null 2>&1; then
  RUNBASE=$(dirname "$SAVDIR")
  if ! "$HOME/tools/revenv/bin/python" "$ROOT/scripts/r1_pointer_law.py" \
        --run-dir "$RUNBASE" >/dev/null 2>&1; then
    err "POINTER LAW battery failed on captured slots in $RUNBASE"
  fi
else
  echo "note: no R1 save-state captures present (work/r1/r1sav-*); pointer-law battery skipped"
fi

# 3s. STAR TABLE LAW (docs/re/r1-savestate.md 2026-10-06): stride-96 name-
# anchored star records, planet ptrs at name+0x2A targeting planet-name-0x24,
# single-owner law. Battery on captured slots; skips with a note when no
# captures exist (work/ is not committed).
STARSAV=""
for d in "$ROOT"/work/r1/r1sav-*/save; do
  [ -d "$d" ] && STARSAV="$d"
done
if [ -n "$STARSAV" ] && ls "$STARSAV"/*.sav >/dev/null 2>&1; then
  if ! "$HOME/tools/revenv/bin/python" "$ROOT/scripts/r1_star_table.py" \
        --run-dir "$(dirname "$STARSAV")" >/dev/null 2>&1; then
    err "STAR TABLE battery failed on captured slots in $(dirname "$STARSAV")"
  fi
else
  echo "note: no R1 save-state captures present; star-table battery skipped"
fi

# 3r. MODULE ATTRIBUTION invariant (docs/re/r1-savestate.md 2026-10-05j):
# the restored image must keep yielding debug-string attributions for the
# core modules (flic/winmgr/gsystem/race, >=5 exact sites each). Needs the
# restored artifact; skips with a note when no captures exist.
if [ -s "$ROOT/work/ascend_restored.bin" ]; then
  if ! "$HOME/tools/revenv/bin/python" "$ROOT/scripts/attribution_scan.py" \
        >/tmp/gate_attr.log 2>&1; then
    tail -12 /tmp/gate_attr.log
    err "attribution_scan regressed (modules lost their >=5-site signal)"
  fi
else
  echo "note: work/ascend_restored.bin absent (run scripts/r1_restore_sites.py); attribution skipped"
fi

# 3o. OQ-002 closure invariant: BOTH vendor FLC files must fully decode
# (stock Autodesk chunks; zero-residue + OOB asserted per chunk). Fast path:
# --decode-only skips the 50s golden hashing; the golden cross-check against
# the C++ port lives in run_tests (flc_logic_golden / flc_intro_golden).
if /usr/bin/python3 "$ROOT/scripts/flc_probe.py" --decode-only --quiet; then
  :
else
  err "flc_probe.py decode failed (OQ-002 regressed?)"
fi
[ -s "$ROOT/docs/re/flc.md" ] || err "docs/re/flc.md missing"
[ -s "$ROOT/rewrite/tests/data/flc_golden.tsv" ] || err "flc_golden.tsv missing (C++ cross-check data)"

# 3p. OQ-017 closure invariant: the .fnt law (1B/px, slot==4+w*h, EOF tiling,
# per-font ink alphabet) must hold on all 384 vendor glyphs (docs/re/fnt.md).
if /usr/bin/python3 "$ROOT/scripts/fnt_probe.py" --quiet; then
  :
else
  err "fnt_probe.py failed (OQ-017 regressed?)"
fi
[ -s "$ROOT/docs/re/fnt.md" ] || err "docs/re/fnt.md missing"

# 4e. Pixel proof the C++ path renders what the decoder says: play the intro
# under Xvfb, capture the screen, demand an EXACT 640x480 match against the
# Python-decoded frame (scripts/intro_pixelcheck.sh; verified 2026-10-04i:
# frame 19 at (192,144)).
if [ -x "$ROOT/rewrite/build/ascendancy" ] && command -v Xvfb >/dev/null 2>&1 \
   && command -v import >/dev/null 2>&1 && [ -x "$HOME/tools/revenv/bin/python" ]; then
  if ! bash "$ROOT/scripts/intro_pixelcheck.sh" 40 1.5 91 >/tmp/gate_intro.log 2>&1; then
    tail -20 /tmp/gate_intro.log; err "intro pixel check failed (window != decoded frame)"
  fi
else
  note "Xvfb/ImageMagick/revenv unavailable: skipped intro pixel check"
fi

# 3l. Victory-condition grammar + CONTRACT smoke: end-*.txt blocks assert
# (scripts/endtext_probe.py), and the rewrite binary must actually reach a
# victory condition on a seeded headless campaign run (docs/PLAYTHROUGH.md).
[ -s "$ROOT/docs/re/turnloop.md" ] || err "docs/re/turnloop.md missing"
if ! /usr/bin/python3 "$ROOT/scripts/endtext_probe.py"; then
  err "endtext_probe.py failed (end-*.txt grammar changed?)"
fi
grep -q 'VICTORY Control' "$ROOT/docs/PLAYTHROUGH.md" \
  || err "PLAYTHROUGH.md lost the control-victory run"
grep -q 'VICTORY Extinct' "$ROOT/docs/PLAYTHROUGH.md" \
  || err "PLAYTHROUGH.md lost the extinction run"
if [ -x "$ROOT/rewrite/build/ascendancy" ]; then
  # T37: budget 600 -> 900. The class-cell channel law (docs/re/
  # income-law.md T37) lengthened the seed-2024 timeline to a FINITE
  # resolve (CLI verified: --campaign 1500 --seed 2024 -> VICTORY
  # Extinct t683); the guard's target is stall/deadlock, and the exit-0
  # + '^VICTORY ' assertions stay intact.
  if ! timeout 180 "$ROOT/rewrite/build/ascendancy" --headless --campaign 900 \
       --seed 2024 >/tmp/gate_campaign.log 2>&1; then
    tail -20 /tmp/gate_campaign.log; err "seeded campaign did not reach victory"
  fi
  grep -q '^VICTORY ' /tmp/gate_campaign.log \
    || { tail -20 /tmp/gate_campaign.log; err "campaign log has no VICTORY line"; }
fi

# 4c. UI smoke: the P5a window must boot under Xvfb, play N turns driven by
# the autoplay path, and exit 0 printing 'ui ok:' (docs/re/ui-runtime.md §5).
if [ -x "$ROOT/rewrite/build/ascendancy" ] && command -v xvfb-run >/dev/null 2>&1; then
  if ! timeout 120 xvfb-run -a "$ROOT/rewrite/build/ascendancy" --ui \
       --campaign 3 --autoplay --seed 9 >/tmp/gate_ui.log 2>&1; then
    tail -20 /tmp/gate_ui.log; err "ui boot failed under xvfb"
  fi
  grep -q 'ui ok: turn 3' /tmp/gate_ui.log \
    || { tail -20 /tmp/gate_ui.log; err "ui did not complete 3 turns"; }

  # 4c-b. Real input: an X client (tools/xsend, libX11 XSendEvent + XWarpPointer
  # -- SDL re-reads the pointer for synthetic Button events) must drive the
  # NEXT TURN button. The app is run WITHOUT --autoplay so a turn can ONLY
  # come from injected input; 'ui ok: turn 1' proves it advanced.
  if [ ! -x "$ROOT/tools/xsend" ] && command -v gcc >/dev/null 2>&1; then
    gcc -O1 -o "$ROOT/tools/xsend" "$ROOT/tools/xsend.c" -lX11 \
      || err "could not build tools/xsend"
  fi
  if [ -x "$ROOT/tools/xsend" ]; then
    Xvfb :77 -screen 0 640x480x24 >/dev/null 2>&1 &
    GATE_XV=$!
    sleep 1
    DISPLAY=:77 "$ROOT/rewrite/build/ascendancy" --ui --campaign 1 \
      --seed 5 >/tmp/gate_ui_in.log 2>&1 &
    GATE_APP=$!
    sleep 2
    DISPLAY=:77 "$ROOT/tools/xsend" "Ascendancy" 510 66 || err "xsend failed"
    wait $GATE_APP || err "ui app exited non-zero with input"
    kill $GATE_XV 2>/dev/null
    grep -q 'ui click next-turn' /tmp/gate_ui_in.log \
      || { cat /tmp/gate_ui_in.log; err "injected click never reached the app"; }
    grep -q 'ui ok: turn 1' /tmp/gate_ui_in.log \
      || { cat /tmp/gate_ui_in.log; err "click did not advance the campaign"; }
  else
    note "tools/xsend not built: skipped real-input UI check"
  fi
else
  note "xvfb-run unavailable: skipped UI smoke"
fi

# 4f. Reference-capture comparison: screenshots of the ORIGINAL game running
# under dosbox-x (produced by scripts/ref_capture.sh, pinned in
# docs/assets/refcap/) must obey the intro65a union-palette law on movie
# shots and its negation on the title-menu control (scripts/refcap_match.py;
# law + measurements + refuted alternatives in docs/re/refcap.md). Fast path:
# scored from pinned PNGs, no emulator. Refresh pins via refcap_gate.sh.
if command -v "$HOME/tools/revenv/bin/python" >/dev/null 2>&1 \
   && [ -f "$ROOT/docs/assets/refcap/original-title-menu.png" ]; then
  RC_PY="$HOME/tools/revenv/bin/python"
  "$RC_PY" "$ROOT/scripts/refcap_match.py" \
    "$ROOT/docs/assets/refcap/original-title-menu.png" --expect not-movie \
    >/tmp/gate_refcap.log 2>&1 \
    || { cat /tmp/gate_refcap.log; err "refcap control (title menu) violated the law"; }
  for PIN in original-intro-movie.png original-intro-caption.png original-intro-galaxy.png; do
    "$RC_PY" "$ROOT/scripts/refcap_match.py" \
      "$ROOT/docs/assets/refcap/$PIN" --expect movie \
      >>/tmp/gate_refcap.log 2>&1 \
      || { cat /tmp/gate_refcap.log; err "refcap movie pin $PIN not recognised as the reference intro"; }
  done
  note "refcap: 3 original movie shots obey the decode palette law, title-menu control does not"
else
  note "revenv or pinned refcap shots absent: skipped reference-capture comparison"
fi

# 4d. Audio: SDL2_mixer must load ALL 86 manifest samples (85 unique — the
# manifest lists 'shield' twice) + theme00 from the REAL vendor files, with
# a dummy audio device (docs/re/audio.md §5). Any load failure aborts init
# with exit 1, so grepping the ok line IS the load test.
if [ -x "$ROOT/rewrite/build/ascendancy" ] && command -v xvfb-run >/dev/null 2>&1; then
  if ! timeout 180 env SDL_AUDIODRIVER=dummy xvfb-run -a \
       "$ROOT/rewrite/build/ascendancy" --ui --audio --campaign 1 \
       --autoplay --seed 4 >/tmp/gate_audio.log 2>&1; then
    tail -20 /tmp/gate_audio.log; err "audio boot failed"
  fi
  grep -q 'audio ok: 85 sfx chunks, music 8191719 B' /tmp/gate_audio.log \
    || { cat /tmp/gate_audio.log; err "audio load line wrong (expect 85 chunks, theme00)"; }
  grep -q 'ui ok: turn 1' /tmp/gate_audio.log \
    || { cat /tmp/gate_audio.log; err "audio run did not complete a turn"; }
else
  note "xvfb-run unavailable: skipped audio smoke"
fi

# 4-5. Build & tests of rewrite/ once the project exists (milestone >= 3)
MS=$(sed -n 's/^milestone:[ ]*\([0-9]*\).*/\1/p' "$ROOT/docs/STATE.md" | head -1)
MS=${MS:-0}
if [ "$MS" -ge 3 ] && [ -d "$ROOT/rewrite" ]; then
  if [ ! -d "$ROOT/rewrite/build" ]; then
    cmake -S "$ROOT/rewrite" -B "$ROOT/rewrite/build" -DCMAKE_BUILD_TYPE=Debug >/tmp/gate_cmake.log 2>&1 \
      || { tail -30 /tmp/gate_cmake.log; err "cmake configure failed"; }
  fi
  if [ -d "$ROOT/rewrite/build" ]; then
    cmake --build "$ROOT/rewrite/build" -j2 >/tmp/gate_build.log 2>&1 \
      || { tail -40 /tmp/gate_build.log; err "build failed"; }
    if [ -x "$ROOT/rewrite/build/run_tests" ]; then
      "$ROOT/rewrite/build/run_tests" >/tmp/gate_tests.log 2>&1 \
        || { tail -40 /tmp/gate_tests.log; err "unit tests failed"; }
    fi
    # 4b. Boot smoke test. Runs the REAL binary twice: once with the dummy
    # video driver and once under Xvfb with x11, because the completion
    # contract requires an Xvfb boot. Bounds are mandatory — see the DOSBOX
    # RULE in STATE.md about unbounded log growth.
    if [ -x "$ROOT/rewrite/build/ascendancy" ]; then
      timeout 60 "$ROOT/rewrite/build/ascendancy" --headless --turns 3 >/tmp/gate_boot.log 2>&1 \
        || { tail -20 /tmp/gate_boot.log; err "headless boot failed"; }
      grep -q '(.bin tables parsed: 7)' /tmp/gate_boot.log \
        || { tail -20 /tmp/gate_boot.log; err "boot did not parse all 7 .bin tables"; }
      grep -q '^ok$' /tmp/gate_boot.log || err "headless boot did not complete the turn loop"
      if command -v xvfb-run >/dev/null 2>&1; then
        timeout 60 xvfb-run -a "$ROOT/rewrite/build/ascendancy" --turns 2 >/tmp/gate_xvfb.log 2>&1 \
          || { tail -20 /tmp/gate_xvfb.log; err "xvfb boot failed"; }
        grep -q 'video driver: x11' /tmp/gate_xvfb.log \
          || { tail -20 /tmp/gate_xvfb.log; err "xvfb boot did not use the x11 driver"; }
      else
        note "xvfb-run unavailable: skipped x11 boot"
      fi
    fi
  fi
fi

if [ "$fail" = 0 ]; then echo "[gate] ALL CHECKS PASS (milestone=$MS)"; fi
exit $fail
