#!/usr/bin/env bash
# tNAME-1 MUTATION ROUND — prove the pins catch the per-game-seed defect.
# M1 handoff drops the seed term (always default 1); M2 Begin press feeds a
# constant instead of wheelBaseSeed+1; M3 buildCampaign drops the apply->seed
# lines (reverts to CLI-only); M4 clock draw drops the !seedExplicit guard
# (--seed stops being authority). Restore COPIES BACK and md5-VERIFIES
# (tPF-6 trap); NEVER git checkout mid-cycle (tPF-7a trap).
set -u
cd "$(dirname "$0")/.."
declare -A FILES=( [M1]=rewrite/src/ui/menulaw.h [M2]=rewrite/src/ui/title.cpp [M3]=rewrite/src/main.cpp [M4]=rewrite/src/main.cpp )
BACKUP=/tmp/tname1_mut_$$
mkdir -p "$BACKUP"
md5_of() { md5sum "${FILES[$1]}" | cut -d' ' -f1; }
ORIG=()
for k in M1 M2 M3 M4; do
  cp "${FILES[$k]}" "$BACKUP/$k"
  ORIG+=("$(md5_of $k)")
done
restore() {
  local i=0
  for k in M1 M2 M3 M4; do
    cp "$BACKUP/$k" "${FILES[$k]}"
    local now; now=$(md5sum "${FILES[$k]}" | cut -d' ' -f1)
    [ "$now" = "${ORIG[$i]}" ] || { echo "RESTORE FAIL $k (${ORIG[$i]} -> $now)"; exit 3; }
    i=$((i+1))
  done
  echo "restore md5-ok x4"
}
trap 'echo ABORT - restoring; restore' EXIT

run_mut() { # $1 = key, $2 = program text (old\n@@\nnew)
  local k=$1 prog=$2
  ~/tools/revenv/bin/python - "$prog" "${FILES[$k]}" <<'PY'
import sys
prog, path = sys.argv[1], sys.argv[2]
src = open(path).read()
old, dst = prog.split("\n@@\n")
assert src.count(old) == 1, f"anchor x{src.count(old)} in {path}"
open(path, "w").write(src.replace(old, dst))
PY
  cmake --build rewrite/build -j8 >/dev/null 2>&1
  if ./rewrite/build/run_tests 2>&1 | grep -q " 0 failed"; then
    echo "$k: NOT CAUGHT (suite green with mutation!)"
  else
    echo "$k: CAUGHT"
    ./rewrite/build/run_tests 2>&1 | grep -E "tname1 .*FAIL" | head -2
  fi
  cp "$BACKUP/$k" "${FILES[$k]}"
}

# M1: handoff stops copying the seed arg
run_mut M1 's.seed = seed;  // tNAME-1: per-game seed travels with the handoff
@@
// mutated M1: seed dropped from handoff'

# M2: Begin press feeds constant 1 (pre-fix shape: same world every game)
run_mut M2 'scrollOffset + selSlot, wheelBaseSeed + 1u);
@@
scrollOffset + selSlot, 1u);  /* mutated M2 */'

# M3: buildCampaign drops the apply->seed lines (CLI-only reading)
run_mut M3 '        cfg.seed = apply->seed;
        mc.seed = apply->seed;
@@
        // mutated M3: apply seed ignored'

# M4: clock draw drops the seedExplicit guard (--seed no longer authority)
run_mut M4 'if (o.ui && !o.seedExplicit) {
@@
    if (o.ui) {  // mutated M4'

restore
echo "TNAM1 MUTATION ROUND DONE"
