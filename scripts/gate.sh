#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

# Quality gate for the Ascendancy RE goal loop. Deterministic, no network.
# Exit 0 = healthy. Output is fed verbatim to the agent on failure.
set -u
cd "$(dirname "$0")/.."
ROOT=$(pwd)
fail=0
note() { echo "[gate] $*"; }
err()  { echo "[gate FAIL] $*"; fail=1; }

# t373: --portable mode (public-tree / fresh-clone entry point). The published
# repo ships NO vendor data (docs/re/packaging.md S3) and a cloning machine may
# lack the RE toolchain (~/tools/revenv). Portable mode SKIPS vendor-dependent
# stages with a note instead of failing. Default (no flag) behaviour is
# UNCHANGED: on the loop tree a missing game/ is an error. ASCENDANCY_DATA=<dir>
# (optional) points at the user's own vendor install: if set and ROOT/game is
# absent, game/ becomes a symlink to it so the ROOT-relative probes all work.
# The gate never writes into game/ — P0 checksums it bidirectionally anyway.
PORTABLE=0
for _a in "$@"; do [ "$_a" = "--portable" ] && PORTABLE=1; done
if [ -n "${ASCENDANCY_DATA:-}" ]; then
  # User-supplied vendor install dir (ascend.exe + ascendNN.cob), READ-ONLY.
  # Probes hardcode ROOT-relative game/ paths, so the symlink is the only
  # uniform mechanism; the gate never writes into it (P0 checksums it
  # bidirectionally anyway). extracted/ is regenerated from the archives
  # (importer measured t373: ascend00 54 / ascend01 328 / ascend02 89 files,
  # diff -r clean vs the loop tree) — packaging.md S9(b) CLOSED by this.
  [ -e "$ROOT/game" ] || ln -s "${ASCENDANCY_DATA%/}" "$ROOT/game" \
    || err "--portable: cannot symlink $ROOT/game -> $ASCENDANCY_DATA"
  if [ ! -d "$ROOT/extracted/ascend00" ] && [ -f "$ROOT/game/ascend00.cob" ]; then
    for _a in ascend00 ascend01 ascend02; do
      /usr/bin/python3 "$ROOT/scripts/cob.py" extract "$ROOT/game/$_a.cob" \
        "$ROOT/extracted/$_a" >/dev/null 2>&1 \
        || err "--portable: cob.py extract $_a failed (ASCENDANCY_DATA incomplete?)"
    done
  fi
fi
VENDOR=0
if [ -f "$ROOT/game/ascend.exe" ] \
   && [ "$(ls "$ROOT/extracted/ascend00" 2>/dev/null | wc -l)" -ge 54 ]; then
  VENDOR=1
fi
if [ "$VENDOR" = 0 ]; then
  if [ "$PORTABLE" = 1 ]; then
    note "vendor corpus absent (game/ + extracted/ascend00): vendor stages SKIPPED; supply ASCENDANCY_DATA=<vendor install dir> for the full gate"
  else
    err "game/ vendor data absent (run with --portable on a clone that legitimately lacks it)"
  fi
fi

# 3v-invariant (t373, publish-filter): work/ must hold ZERO tracked files —
# the historical `git add -f` survivors (packaging.md S3 landmine) made a
# work/-dropping publish filter leak capture-corpus paths. Recurrence-proof.
if [ -n "$(git ls-files work/)" ]; then
  err "t373 invariant: tracked files under work/ exist again (publish filter would leak): $(git ls-files work/ | head -3)"
fi

# 1. Originals untouched (P0 invariant) — checksum manifest, BIDIRECTIONAL (t162).
# t162 audit (docs/re/stop-report.md SS55): the pre-t162 leg enumerated
# manifest->disk only. Measured on a scratch copy: DELETE of a listed file armed
# (sha256sum -c "FAILED open or read"), but an ADDED file produced zero signal
# (nothing compares disk->manifest), and an ABSENT manifest silently rebuilt
# itself from whatever was on disk, blessing a tampered tree forever.
# Manifest set == disk == 23 files verified on the real tree before landing.
MAN="$ROOT/docs/BASELINE.sha256"
if [ "$VENDOR" = 1 ]; then   # t373 portable-wrap: P0
if [ ! -f "$MAN" ]; then
  # docs/BASELINE.sha256 has been git-tracked since seed 3792dc5, so a healthy
  # tree can never legitimately lack it; absence = restore from git, NEVER
  # regenerate from disk (the regen path WAS the bless-the-tamper hole).
  err "P0: docs/BASELINE.sha256 missing — restore it (git checkout -- docs/BASELINE.sha256); NEVER regenerate the baseline from disk"
else
  (cd "$ROOT/game" && sha256sum -c "$MAN" --quiet 2>&1) | grep -v ': OK' && err "game/ files modified!"
  # Second direction: every file on disk must be named by the manifest.
  # substr($0,67): sha256sum prints 64-hex + 2 spaces + name (handles spaces).
  # LC_ALL=C on comm ITSELF (t162 fixture run): comm re-parses its inputs under
  # the CURRENT collation, so LC_ALL=C sorts + a UTF-8 locale comm disagree and
  # dump every line as unpaired (measured: 23 false entries, real delta buried).
  LC_ALL=C comm -3 <(awk '{print substr($0,67)}' "$MAN" | LC_ALL=C sort) \
              <(cd "$ROOT/game" && find . -maxdepth 1 -type f -printf '%f\n' | LC_ALL=C sort) \
    | grep . && err "P0: game/ file SET != manifest (file added/removed outside the baseline)"
fi
else note "P0 game/ checksums skipped (no vendor data)"; fi

# 2. Extractor round-trip works
if [ "$VENDOR" = 1 ]; then   # t373 portable-wrap: extract
TMP=$(mktemp -d)
if /usr/bin/python3 "$ROOT/scripts/cob.py" extract "$ROOT/game/ascend00.cob" "$TMP/a0" >/dev/null 2>&1; then
  n=$(ls "$TMP/a0" | wc -l); [ "$n" -ge 50 ] || err "extractor regression: only $n files from ascend00 (expect >=50)"
else
  err "cob.py extract failed on ascend00.cob"
fi
rm -rf "$TMP"
else note "ascend00 extractor round-trip skipped (no vendor data)"; fi

# 3. Docs integrity
for f in docs/PLAN.md docs/STATE.md docs/FINDINGS.md; do
  [ -s "$ROOT/$f" ] || err "$f missing or empty"
done

# 3-pre. BUILD FIRST (t343 fix). The build used to live at the bottom of this
# script, AFTER the build-dependent stages (3m ability smoke, 3l campaign,
# 4e pixel, 4c UI, 4d audio). Every one of those guards on
# `[ -x rewrite/build/ascendancy ]`, so on a FRESH CLONE they all silently
# self-skipped on the first gate run while the build then happened at the very
# end — a green first-run gate that had tested none of them (measured:
# t343 clone run1, work/r343/clone-run1-gate.out). The build is a hard
# prerequisite of the milestone>=3 contract, so the whole build/test/boot block
# moved here; every later stage now sees a real binary. (Side-effect-free gate
# rule: the build dir is gitignored scratch; the gate still never touches game/
# or work/ captures.)
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
if [ "$VENDOR" = 1 ]; then   # t373 portable-wrap: run_tests
    if [ -x "$ROOT/rewrite/build/run_tests" ]; then
      "$ROOT/rewrite/build/run_tests" >/tmp/gate_tests.log 2>&1 \
        || { tail -40 /tmp/gate_tests.log; err "unit tests failed"; }
    fi
else note "run_tests skipped (unit tests read extracted/ vendor tables)"; fi
    # 4b. Boot smoke test. Runs the REAL binary twice: once with the dummy
    # video driver and once under Xvfb with x11, because the completion
    # contract requires an Xvfb boot. Bounds are mandatory — see the DOSBOX
    # RULE in STATE.md about unbounded log growth.
if [ "$VENDOR" = 1 ]; then   # t373 portable-wrap: boot
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
else note "boot smokes skipped (binary needs user-supplied game data)"; fi
  fi
fi

# 3b. P1b invariant: .bin tables parse at stride 24, and the .cob extractor must
# emit ALL directory entries (it silently dropped the last file of every archive
# until 2026-10-03, so count is asserted, not trusted).
if [ "$VENDOR" = 1 ]; then   # t373 portable-wrap: 3b
if /usr/bin/python3 "$ROOT/scripts/table_probe.py" --out /tmp/gate_tables.md >/tmp/gate_probe.log 2>&1; then
  [ "$(ls "$ROOT/extracted/ascend00" | wc -l)" -ge 54 ] || err "ascend00 extracted <54 files"
  [ "$(find "$ROOT/extracted/ascend02" -type f | wc -l)" -ge 89 ] || err "ascend02 extracted <89 files"
  [ -f "$ROOT/extracted/ascend02/data/intro65a.flc" ] || err "ascend02/data/intro65a.flc missing (last-entry regression)"
else
  tail -20 /tmp/gate_probe.log; err "table_probe.py failed (.bin stride invariant broken?)"
fi
else note "table_probe skipped (no extracted/)"; fi

# 3c. P1c invariant: every .shp container parses (magic 1.10, table size
# 8*(N+1), monotonic pointer slots, spans covering the data area). The probe
# aborts on any violation; here we additionally pin the corpus size so a
# silently-shrunk extracted/ tree cannot pass.
if [ "$VENDOR" = 1 ]; then   # t373 portable-wrap: 3c
NSH=$(find "$ROOT/extracted" -name '*.shp' -type f | wc -l)
[ "$NSH" -ge 208 ] || err "only $NSH .shp files in extracted/ (expect >=208)"
if /usr/bin/python3 "$ROOT/scripts/shp_probe.py" --out /tmp/gate_shp.md >/tmp/gate_shp.log 2>&1; then
  grep -q 'parsed 208/208 libraries' /tmp/gate_shp.log \
    || { tail -20 /tmp/gate_shp.log; err "shp_probe did not parse all 208 libraries"; }
else
  tail -20 /tmp/gate_shp.log; err "shp_probe.py failed (.shp container invariant broken?)"
fi
else note "shp corpus skipped (no extracted/)"; fi

# 3c-2. t197: unified record law pinned on the REWRITE-EXACT validator
# (span-free walk + both-components dims gate; shp.md S21). The X class
# (29 span-crossing full frames) must stay decodable and the dims-gate
# demotions (mouse k5, sg64expl k0) must not silently drift. ~0.2 s.
if [ "$VENDOR" = 1 ]; then   # t373 portable-wrap: 3c2
if /usr/bin/python3 "$ROOT/scripts/r1_shp_unifiedlaw.py" >/tmp/gate_shplaw.log 2>&1; then
  for TV in "record V: 196" "record A: 1288" "record X: 29" "record FAIL: 44" \
            "libraries passing EVERY record: 187/208"; do
    grep -qF "$TV" /tmp/gate_shplaw.log \
      || { tail -20 /tmp/gate_shplaw.log; err "shp unified law drift (missing '$TV')"; }
  done
else
  tail -20 /tmp/gate_shplaw.log; err "r1_shp_unifiedlaw.py crashed"
fi
else note "shp unified-law battery skipped (no extracted/)"; fi

# 3d. P2-input invariant: all 21 race*.dip parse with the SAME DIPVALUES key
# set (that identity is what makes per-race AI data-driven rather than 21
# bespoke scripts). Also pins the corpus size.
if [ "$VENDOR" = 1 ]; then   # t373 portable-wrap: 3d
if /usr/bin/python3 "$ROOT/scripts/dip_probe.py" --out /tmp/gate_dip.md >/tmp/gate_dip.log 2>&1; then
  grep -q 'OK: 21/21 dips parsed' /tmp/gate_dip.log \
    || { tail -20 /tmp/gate_dip.log; err "dip_probe did not parse all 21 dips"; }
else
  tail -20 /tmp/gate_dip.log; err "dip_probe.py failed (.dip grammar broken?)"
fi
else note "dip_probe skipped (no extracted/)"; fi

# 3e. P1e invariant: FLIC chunk chains tile their files exactly; audio/font/
# hazard/tmp inventory regenerates.
if [ "$VENDOR" = 1 ]; then   # t373 portable-wrap: 3e
if /usr/bin/python3 "$ROOT/scripts/media_probe.py" --out /tmp/gate_media.md >/tmp/gate_media.log 2>&1; then
  grep -q 'OK: 2 flic exact-tiled' /tmp/gate_media.log \
    || { tail -20 /tmp/gate_media.log; err "media_probe did not verify both FLICs"; }
else
  tail -20 /tmp/gate_media.log; err "media_probe.py failed (FLIC/audio inventory)"
fi
else note "media_probe skipped (no extracted/)"; fi

# 3f. P1d invariant: the golden save is byte-pinned by size and the measured
# stride-75 tech chain still resolves.
if [ "$VENDOR" = 1 ]; then   # t373 portable-wrap: 3f
if /usr/bin/python3 "$ROOT/scripts/gam_probe.py" --out /tmp/gate_gam.md >/tmp/gate_gam.log 2>&1; then
  grep -q 'stride=75' /tmp/gate_gam.log \
    || { tail -20 /tmp/gate_gam.log; err "gam_probe stride changed (was 75)"; }
else
  tail -20 /tmp/gate_gam.log; err "gam_probe.py failed (resume.gam correlation)"
fi
else note "gam_probe skipped (no vendor data)"; fi

# 3g. P1f invariant: ascend00 stays CP437-safe (few high bytes) and the exe
# still exposes its 34 module names (the P2 subsystem spine).
if [ "$VENDOR" = 1 ]; then   # t373 portable-wrap: 3g
if /usr/bin/python3 "$ROOT/scripts/text_probe.py" --quiet >/dev/null 2>/tmp/gate_text.log; then
  grep -q 'modules=34' /tmp/gate_text.log \
    || { cat /tmp/gate_text.log; err "text_probe module count changed (was 34)"; }
else
  cat /tmp/gate_text.log; err "text_probe.py failed"
fi
else note "text_probe skipped (no vendor data)"; fi

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
if [ "$VENDOR" = 1 ]; then   # t373 portable-wrap: 3i
if /usr/bin/python3 "$ROOT/scripts/restree_probe.py" --out /tmp/gate_research.md --quiet; then
  grep -q 'data rows = \*\*106\*\* = \*\*66\*\*' /tmp/gate_research.md \
    || err "restree_probe: row counts drifted from 106=66+40"
  grep -q 'acyclic True' /tmp/gate_research.md \
    || err "restree_probe: prereq graph no longer acyclic"
else
  err "restree_probe.py crashed"
fi
else note "restree_probe skipped (no extracted/)"; fi

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
if [ "$VENDOR" = 1 ]; then   # t373 portable-wrap: 3j
if ! /usr/bin/python3 "$ROOT/scripts/gizmo_probe.py" --quiet; then
  err "gizmo_probe.py failed its own invariants"
fi
else note "gizmo_probe skipped (no extracted/)"; fi
grep -q 'Interstellar Trucking' "$ROOT/docs/re/economy.md" \
  || err "economy.md lost the 254-sentinel record"

# 3k. P4 UI/species/diplomacy invariant: ui_probe asserts 132 windows, 15-key
# DIPVALUES identity across 21 races, 15 DA_ templates, 21 species, unique
# SA_ tokens; docs must exist and keep the parse-trap + roster facts visible.
[ -s "$ROOT/docs/re/ui.md" ] || err "docs/re/ui.md missing"
[ -s "$ROOT/docs/re/species.md" ] || err "docs/re/species.md missing"
[ -s "$ROOT/docs/re/diplomacy.md" ] || err "docs/re/diplomacy.md missing"
if [ "$VENDOR" = 1 ]; then   # t373 portable-wrap: 3k
if ! /usr/bin/python3 "$ROOT/scripts/ui_probe.py" --quiet; then
  err "ui_probe.py failed its own invariants"
fi
else note "ui_probe skipped (no extracted/)"; fi
grep -q 'PARSE TRAP' "$ROOT/docs/re/diplomacy.md" \
  || err "diplomacy.md lost the negative-value parse-trap record"
grep -q 'SA_SuperMarines' "$ROOT/docs/re/species.md" \
  || err "species.md lost the ability roster"

# 3m. Species special abilities (docs/re/abilities.md): the three-source
# roster invariant (help.txt abil blocks == raceNN.dip header tokens, race02
# tokenless -> title match) and the 14/7 charge split, via
# scripts/ability_probe.py; plus the binary firing at least one SA_ event.
[ -s "$ROOT/docs/re/abilities.md" ] || err "docs/re/abilities.md missing"
if [ "$VENDOR" = 1 ]; then   # t373 portable-wrap: 3m-probe
if ! /usr/bin/python3 "$ROOT/scripts/ability_probe.py"; then
  err "ability_probe.py failed (roster/charge invariant broken?)"
fi
else note "ability_probe skipped (no extracted/)"; fi
if [ "$VENDOR" = 1 ]; then   # t373 portable-wrap: 3m-bin
if [ -x "$ROOT/rewrite/build/ascendancy" ]; then
  timeout 120 "$ROOT/rewrite/build/ascendancy" --headless --campaign 65 \
    --seed 11 >/tmp/gate_ability.log 2>&1
  rc=$?
  # exit 1 = "no victory after 65 turns" (expected here); >1 = crash.
  [ "$rc" -le 1 ] || { tail -10 /tmp/gate_ability.log; err "ability smoke crashed (rc=$rc)"; }
  grep -q 'SA_HealShips' /tmp/gate_ability.log \
    || { tail -10 /tmp/gate_ability.log; err "charged ability never fired by turn 65 (cad[HealShips]==60, aicode.md §6.4)"; }
fi
else note "ability smoke skipped (no data)"; fi

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
# 3n2 (t163): the SAME invariants over a DERIVED audit set, because the two legs
# above name files by hand — {audited} was a copy of {the last file that broke},
# not {scripts that can launch dosbox}. Measured t163: 12 scripts/*.sh hold a
# comment-stripped "MOUNT" line (the autoexec mount is what actually touches the
# game tree); the hand list covered 2. Also refuted the hand leg's FORM:
# `grep 'ascendancy/game'` cannot fire for 10/12 launchers (the string appears
# nowhere in their code), so the invariant is stated positively instead — every
# MOUNT target is $SCRATCH and $SCRATCH is under work/. Static checks only, as
# above: running an emulator is the LOOP's job, never the gate's.
SDIR="${R1_SCRIPTS_DIR:-$ROOT/scripts}"
LAUNCH=""
for f in "$SDIR"/*.sh; do
  [ -f "$f" ] || continue
  grep -vE '^[[:space:]]*#' "$f" | grep -qE '^[[:space:]]*I?MOUNT ' && LAUNCH="$LAUNCH $f"
done
[ -n "$LAUNCH" ] || err "3n2: no launcher matched the MOUNT predicate in $SDIR (leg inert — inspect predicate)"
note "3n2: auditing $(echo $LAUNCH | wc -w) dosbox launcher(s) derived from the MOUNT predicate"
for f in $LAUNCH; do
  b=$(basename "$f")
  code=$(grep -vE '^[[:space:]]*#' "$f")
  echo "$code" | grep -Eq 'pkill[ ]+-f' \
    && err "3n2: $b uses pkill -f (exact-name only; self-match killed a gate shell once)"
  echo "$code" | grep -E '^[[:space:]]*I?MOUNT ' | grep -v '\$SCRATCH' | grep -q . \
    && err "3n2: $b has a MOUNT line that does not target \$SCRATCH (pristine game/ risk, docs/BLOCKED.md:122)"
  grep -E '^[[:space:]]*SCRATCH=' "$f" | head -1 | grep -q '/work/' \
    || err "3n2: $b SCRATCH= does not point under work/ (scratch copy required)"
  echo "$code" | grep -qE -- '-time-limit|timeout -s KILL' \
    || err "3n2: $b has no dosbox bound (-time-limit or timeout -s KILL)"
done

# 3n3 (t277): TL-expiry SOP invariants. MEASURED t277 (docs/re/selfplay.md t277
# block): 18 of 33 logged :9 sessions died at 28810-28820 s wall with exactly
# 2880 autosaves = TL 28800 / 10 s cadence — the "unexplained" deaths WERE the
# runaway guard firing mid-sitting, and dosbox-x prints NO farewell line on that
# exit (golden witness work/r1/selftest-t111-playcap/dosbox.out, TL=90, ends
# 'Active save slot: 1 [Empty]' at EOF; grep 'Shutting down' over the 290 MB
# production log = 0). So: the production launcher's guard must be >= 48 h, and
# the health checker's pre-expiry warn must exceed the loop's own worst realistic
# health-sampling interval (iteration gaps p95 8682 s, max 15156 s — journal.tsv
# n=198), else the warn can never be observed. Static checks only, as above.
grep -qE 'TL="\$\{TL:-172800\}"' "$ROOT/scripts/r1_playcap_vnc.sh" \
  || err "3n3: r1_playcap_vnc.sh lost the t277 TL=172800 default (28800 kills sittings; docs/re/selfplay.md t277)"
grep -qE 'WARN_AHEAD.*os.environ.get\("WARN_AHEAD", *"14400"\)' "$ROOT/scripts/r1_game_health.py" \
  || err "3n3: r1_game_health.py lost the t277 WARN_AHEAD=14400 default (600 s < the loop's sampling interval, so the warn never fires)"
grep -q 'r1_game_health.py' "$ROOT/scripts/loop_one_task.sh" \
  || err "3n3: loop_one_task.sh no longer samples game health every iteration (t267 self-heal)"

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
# core modules (flic/winmgr/gsystem/race, >=5 exact sites each). t343: the
# restored image is TRACKED at artifacts/ascend_restored.bin (payload derives
# from game/ascend.exe@0x2a50 inside attribution_scan.py), so this stage now
# runs on a fresh clone; work/ copy still honoured when present.
if [ "$VENDOR" = 1 ]; then   # t373 portable-wrap: 3r
if [ -s "$ROOT/work/ascend_restored.bin" ] || [ -s "$ROOT/artifacts/ascend_restored.bin" ]; then
  if [ ! -x "$HOME/tools/revenv/bin/python" ]; then
    echo "note: revenv python absent: attribution scan skipped (t373: ungated invocation used to hard-fail clones lacking ~/tools/revenv)"
  elif ! "$HOME/tools/revenv/bin/python" "$ROOT/scripts/attribution_scan.py" \
        >/tmp/gate_attr.log 2>&1; then
    tail -12 /tmp/gate_attr.log
    err "attribution_scan regressed (modules lost their >=5-site signal)"
  fi
else
  echo "note: work/ascend_restored.bin absent (run scripts/r1_restore_sites.py); attribution skipped"
fi
else note "attribution scan skipped (no vendor data / revenv)"; fi

# 3o. OQ-002 closure invariant: BOTH vendor FLC files must fully decode
# (stock Autodesk chunks; zero-residue + OOB asserted per chunk). Fast path:
# --decode-only skips the 50s golden hashing; the golden cross-check against
# the C++ port lives in run_tests (flc_logic_golden / flc_intro_golden).
if [ "$VENDOR" = 1 ]; then   # t373 portable-wrap: 3o
if /usr/bin/python3 "$ROOT/scripts/flc_probe.py" --decode-only --quiet; then
  :
else
  err "flc_probe.py decode failed (OQ-002 regressed?)"
fi
else note "FLIC decode skipped (no vendor data)"; fi
[ -s "$ROOT/docs/re/flc.md" ] || err "docs/re/flc.md missing"
[ -s "$ROOT/rewrite/tests/data/flc_golden.tsv" ] || err "flc_golden.tsv missing (C++ cross-check data)"

# 3p. OQ-017 closure invariant: the .fnt law (1B/px, slot==4+w*h, EOF tiling,
# per-font ink alphabet) must hold on all 384 vendor glyphs (docs/re/fnt.md).
if [ "$VENDOR" = 1 ]; then   # t373 portable-wrap: 3p
if /usr/bin/python3 "$ROOT/scripts/fnt_probe.py" --quiet; then
  :
else
  err "fnt_probe.py failed (OQ-017 regressed?)"
fi
else note ".fnt law skipped (no extracted/)"; fi
[ -s "$ROOT/docs/re/fnt.md" ] || err "docs/re/fnt.md missing"

# 4e. Pixel proof the C++ path renders what the decoder says: play the intro
# under Xvfb, capture the screen, demand an EXACT 640x480 match against the
# Python-decoded frame (scripts/intro_pixelcheck.sh; verified 2026-10-04i:
# frame 19 at (192,144)).
if [ "$VENDOR" = 1 ]; then   # t373 portable-wrap: 4e
if [ ! -x "$ROOT/rewrite/build/ascendancy" ]; then
  note "rewrite binary absent (build stage failed/skipped): skipped intro pixel check"
elif ! command -v Xvfb >/dev/null 2>&1 || ! command -v import >/dev/null 2>&1 || [ ! -x "$HOME/tools/revenv/bin/python" ]; then
  note "Xvfb/ImageMagick(revenv) unavailable: skipped intro pixel check"
elif ! bash "$ROOT/scripts/intro_pixelcheck.sh" 40 1.5 91 >/tmp/gate_intro.log 2>&1; then
  tail -20 /tmp/gate_intro.log; err "intro pixel check failed (window != decoded frame)"
fi
else note "intro pixel check skipped (no data)"; fi

# 3l. Victory-condition grammar + CONTRACT smoke: end-*.txt blocks assert
# (scripts/endtext_probe.py), and the rewrite binary must actually reach a
# victory condition on a seeded headless campaign run (docs/PLAYTHROUGH.md).
[ -s "$ROOT/docs/re/turnloop.md" ] || err "docs/re/turnloop.md missing"
if [ "$VENDOR" = 1 ]; then   # t373 portable-wrap: 3l-endtext
if ! /usr/bin/python3 "$ROOT/scripts/endtext_probe.py"; then
  err "endtext_probe.py failed (end-*.txt grammar changed?)"
fi
else note "endtext_probe skipped (no extracted/)"; fi
grep -q 'VICTORY Control' "$ROOT/docs/PLAYTHROUGH.md" \
  || err "PLAYTHROUGH.md lost the control-victory run"
grep -q 'VICTORY Extinct' "$ROOT/docs/PLAYTHROUGH.md" \
  || err "PLAYTHROUGH.md lost the extinction run"
if [ "$VENDOR" = 1 ]; then   # t373 portable-wrap: 3l-campaign
if [ -x "$ROOT/rewrite/build/ascendancy" ]; then
  # T37: budget 600 -> 900 (class-cell channel law). T40: 900 -> 1200 — the
  # faithful CB-only start (docs/re/income-law.md T40) moved the seed-2024
  # finite resolve to Control t961 (CLI verified: --headless --campaign 1500
  # --seed 2024; seeds 1/2 resolve Control t979/t826). T202B: 1200 -> 1600 —
  # the measured usedPopFor (item-UPOP sum, _wip_t202 S11) activates the
  # 0x3f220 no-free-pop law, so AI builds serialize behind pop growth and
  # seed 2024 now resolves Control at t1255 (CLI --headless --campaign 1500
  # --seed 2024 — FINITE, verified this session; the guard's target remains
  # stall/deadlock; exit-0 + '^VICTORY ' assertions stay intact).
  if ! timeout 240 "$ROOT/rewrite/build/ascendancy" --headless --campaign 1600 \
       --seed 2024 >/tmp/gate_campaign.log 2>&1; then
    tail -20 /tmp/gate_campaign.log; err "seeded campaign did not reach victory"
  fi
  grep -q '^VICTORY ' /tmp/gate_campaign.log \
    || { tail -20 /tmp/gate_campaign.log; err "campaign log has no VICTORY line"; }
fi
else note "victory campaign skipped (no data)"; fi

# 4c. UI smoke: the P5a window must boot under Xvfb, play N turns driven by
# the autoplay path, and exit 0 printing 'ui ok:' (docs/re/ui-runtime.md §5).
# t343: notes split by cause (binary absent vs toolchain absent) — the old
# single note blamed xvfb-run for a missing binary on fresh clones.
if [ "$VENDOR" = 1 ]; then   # t373 portable-wrap: 4c
if [ ! -x "$ROOT/rewrite/build/ascendancy" ]; then
  note "rewrite binary absent (build stage failed/skipped): skipped UI smoke"
elif ! command -v xvfb-run >/dev/null 2>&1; then
  note "xvfb-run unavailable: skipped UI smoke"
else
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
fi
else note "UI smoke skipped (no data)"; fi

# 4f. Reference-capture comparison: screenshots of the ORIGINAL game running
# under dosbox-x (produced by scripts/ref_capture.sh, pinned in
# docs/assets/refcap/) must obey the intro65a union-palette law on movie
# shots and its negation on the title-menu control (scripts/refcap_match.py;
# law + measurements + refuted alternatives in docs/re/refcap.md). Fast path:
# scored from pinned PNGs, no emulator. Refresh pins via refcap_gate.sh.
if [ "$VENDOR" = 1 ] \
   && command -v "$HOME/tools/revenv/bin/python" >/dev/null 2>&1 \
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
# t343: notes split by cause (see 4c).
if [ "$VENDOR" = 1 ]; then   # t373 portable-wrap: 4d
if [ ! -x "$ROOT/rewrite/build/ascendancy" ]; then
  note "rewrite binary absent (build stage failed/skipped): skipped audio smoke"
elif ! command -v xvfb-run >/dev/null 2>&1; then
  note "xvfb-run unavailable: skipped audio smoke"
else
  if ! timeout 180 env SDL_AUDIODRIVER=dummy xvfb-run -a \
       "$ROOT/rewrite/build/ascendancy" --ui --audio --campaign 1 \
       --autoplay --seed 4 >/tmp/gate_audio.log 2>&1; then
    tail -20 /tmp/gate_audio.log; err "audio boot failed"
  fi
  grep -q 'audio ok: 85 sfx chunks, music 8191719 B' /tmp/gate_audio.log \
    || { cat /tmp/gate_audio.log; err "audio load line wrong (expect 85 chunks, theme00)"; }
  grep -q 'ui ok: turn 1' /tmp/gate_audio.log \
    || { cat /tmp/gate_audio.log; err "audio run did not complete a turn"; }
fi
else note "audio smoke skipped (no data)"; fi

# 3t. LEDGER CONSISTENCY (t158) — the two ledger checks run HERE, not in prose.
# Why: t157 found STATE.md's fast index had drifted 6 rows from the record while
# every existing check passed, then fixed it with a checker the prose told humans
# to run by hand. A checker nobody is forced to run is a suggestion: gate.sh had
# 0 references to ledger_index_check.py and loop_one_task.sh only ran
# ledger_audit.py. gate.sh is the one command both the harness post-flight and
# every iteration's finish sequence already run, so wiring it here makes the
# invariant automatic instead of discipline-dependent.
#   audit : record's own contract (CLOSED rows name evidence + code site; OPEN
#           set == triaged set). t158 also tightened EVIDENCE to require a
#           specific handle (address / FUN_ / DAT_ / md5 / run dir / N-of-M /
#           probe path / banked section) instead of accepting the words
#           "measured"/"verified"/"law".
#   index : STATE.md's `ledger:` block vs the record, same classifier — the menu
#           a fresh session is told to resume from must be truthful.
if ! /usr/bin/python3 "$ROOT/scripts/ledger_audit.py" >/tmp/gate_ledger.log 2>&1; then
  cat /tmp/gate_ledger.log; err "ledger audit failed (see docs/OPEN-QUESTIONS.md rows above)"
fi
if ! /usr/bin/python3 "$ROOT/scripts/ledger_index_check.py" >/tmp/gate_ledger_index.log 2>&1; then
  cat /tmp/gate_ledger_index.log
  err "STATE ledger index != record: re-derive the block from docs/OPEN-QUESTIONS.md (the record wins)"
fi

# 3u. IDLE-GATE B2 REGRESSION (t186). The probe's prompt-delta leg armed the
# loop on ITS OWN previous report (echo of the loop's commit subject) for nine
# straight iterations before it was diagnosed. The replay script asserts on the
# real prompt history that (a) the fix strictly reduces arms and (b) every
# delta the fix ignores is provably inside a loop-authored region. Runs in ~1s;
# SKIPs (rc 0) if work/r1/loop is ever rotated away.
if ! /usr/bin/python3 "$ROOT/scripts/r1_t186_b2_regression.py" >/tmp/gate_b2_regression.log 2>&1; then
  cat /tmp/gate_b2_regression.log
  err "idle-gate B2 regression failed: the probe could arm on loop echo again (see docs/STATE.md t186 LANDED block)"
fi

# (t343) The build/test/boot block that used to sit here now runs at "3-pre"
# near the top, so the build-dependent smokes below see a real binary on a
# fresh clone's FIRST gate run. MS is computed there.

if [ "$fail" = 0 ]; then echo "[gate] ALL CHECKS PASS (milestone=$MS)"; fi
exit $fail
