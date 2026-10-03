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
  fi
fi

if [ "$fail" = 0 ]; then echo "[gate] ALL CHECKS PASS (milestone=$MS)"; fi
exit $fail
