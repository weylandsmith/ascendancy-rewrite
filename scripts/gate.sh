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
