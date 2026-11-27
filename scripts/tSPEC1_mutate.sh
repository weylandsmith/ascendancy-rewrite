#!/usr/bin/env bash
# tSPEC-1 MUTATION ROUND — prove the pins actually catch the species-drop
# defect. M1 handoff drops the species arg (always 0); M2 Begin press feeds
# a constant instead of the RACELIST expression; M3 buildCampaign reverts to
# the CLI-only reading. Restore COPIES BACK and md5-VERIFIES (tPF-6 trap);
# NEVER git checkout mid-cycle (tPF-7a trap).
set -u
cd "$(dirname "$0")/.."
T=rewrite/tests/test_species_pick_tspec1.cpp
declare -A FILES=( [M1]=rewrite/src/ui/menulaw.h [M2]=rewrite/src/ui/title.cpp [M3]=rewrite/src/main.cpp )
BACKUP=/tmp/tspec1_mut_$$
mkdir -p "$BACKUP"
md5_of() { md5sum "${FILES[$1]}" | cut -d' ' -f1; }
ORIG=()
for k in M1 M2 M3; do
  cp "${FILES[$k]}" "$BACKUP/$k"
  ORIG+=("$(md5_of $k)")
done
restore() {
  local i=0
  for k in M1 M2 M3; do
    cp "$BACKUP/$k" "${FILES[$k]}"
    local now; now=$(md5sum "${FILES[$k]}" | cut -d' ' -f1)
    [ "$now" = "${ORIG[$i]}" ] || { echo "RESTORE FAIL $k (${ORIG[$i]} -> $now)"; exit 3; }
    i=$((i+1))
  done
  echo "restore md5-ok x3"
}
trap 'echo ABORT — restoring; restore() exit was $?; restore' EXIT

run_mut() { # $1 = key, $2 = sed program file applied to target
  local k=$1 prog=$2
  ~/tools/revenv/bin/python - "$prog" "${FILES[$k]}" <<'PY'
import sys, re
prog, path = sys.argv[1], sys.argv[2]
src = open(path).read()
old, dst = prog.split("\n@@\n")
assert src.count(old) == 1, f"anchor x{src.count(old)} in {path}"
open(path, "w").write(src.replace(old, dst))
PY
  cmake --build rewrite/build -j8 >/dev/null 2>&1
  if ./rewrite/build/run_tests 2>&1 | grep -q " 0 failed"; then
    echo "$k: NOT CAUGHT (suite green with mutation!)"; rc=1
  else
    echo "$k: CAUGHT"
    ./rewrite/build/run_tests 2>&1 | grep -E "tspec1 .*FAIL" | head -2
    rc=0
  fi
  cp "$BACKUP/$k" "${FILES[$k]}"
  return $rc
}

FAILURES=0
# M1: handoff stops copying the species arg
printf 's.species = playerSpecies;\n@@\n// mutated M1\n' > /tmp/tspec1_m1.prog
run_mut M1 "$(cat /tmp/tspec1_m1.prog)" || FAILURES=$((FAILURES+1))
# M2: Begin press feeds constant 0 (pre-fix shape: species never plumbed)
# Anchor spans the newline (the species-pick LOG line 'atmosphere, scrollOffset
# + selSlot);' is single-line, so it cannot collide).
printf 'atmosphere,\n                                scrollOffset + selSlot);\n@@\natmosphere,\n                                0);  /* mutated M2 */\n' > /tmp/tspec1_m2.prog
run_mut M2 "$(cat /tmp/tspec1_m2.prog)" || FAILURES=$((FAILURES+1))
# M3: buildCampaign ignores the handoff species
printf '(apply && apply->set) ? apply->species : o.playerSpecies\n@@\no.playerSpecies  /* mutated M3 */\n' > /tmp/tspec1_m3.prog
run_mut M3 "$(cat /tmp/tspec1_m3.prog)" || FAILURES=$((FAILURES+1))

trap - EXIT
restore
echo "MUTATION ROUND: $FAILURES not-caught of 3"
[ "$FAILURES" = 0 ]
