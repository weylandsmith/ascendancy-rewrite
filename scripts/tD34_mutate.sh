#!/usr/bin/env bash
# tD34 mutation campaign: prove the capture-law pins are load-bearing.
# RESTORE LAW (tPF-6): restore() COPIES BACK then md5-verifies. NEVER
# git-checkout mid-cycle (tPF-7a). REBUILD before any runtime witness.
set -u
cd "$(dirname "$0")/.."
F=rewrite/src/game/campaign.cpp
BAK=/tmp/td34_campaign.cpp.bak
cp "$F" "$BAK"
MD5=$(md5sum "$F" | cut -d' ' -f1)
restore() { cp "$BAK" "$F"; NOW=$(md5sum "$F" | cut -d' ' -f1);
  [ "$NOW" = "$MD5" ] || { echo "RESTORE FAILED md5 $NOW != $MD5"; exit 3; }; }
trap restore EXIT

mutate() {
  python3 - "$F" "$1" "$2" <<'PY'
import sys
p, o, n = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(p).read()
assert s.count(o) == 1, f"occurrences {s.count(o)} for {o[:60]!r}"
open(p, "w").write(s.replace(o, n))
PY
}

run_case() {
  local out rc
  out=$(cmake --build rewrite/build --target run_tests -j8 2>&1 | tail -1)
  out=$(./rewrite/build/run_tests 2>&1); rc=$?
  if [ $rc -ne 0 ]; then
    echo "MUTANT $1: CAUGHT (rc=$rc)"
    echo "$out" | grep -E "FAIL" | head -4
  else
    echo "MUTANT $1: SURVIVED — PIN IS WEAK"
  fi
  restore
}

# M1: the success gate loses the count>shields operand (forced-only).
mutate 'invasionAttempt && (modules > shields || forced);' \
       'invasionAttempt && (forced);'
run_case M1_gate_drops_count

# M2: the gate loses the forced leg (Minions identity breaks).
mutate 'invasionAttempt && (modules > shields || forced);' \
       'invasionAttempt && (modules > shields);'
run_case M2_gate_drops_forced

# M3: no-module engagement captures again (the pre-tD34 pop decider).
mutate 'const bool invasionAttempt = modules > 0;' \
       'const bool invasionAttempt = true;'
run_case M3_attempt_drops_modules

# M4: repel no longer blocks the owner flip.
mutate 'if (!captured) continue;                   // 0x3a46a fail tail' \
       'if (captured && false) continue;           // mutated: repel passes'
run_case M4_repel_gate_removed

# M5: consumption removed (repelled invasions free).
mutate 'invModules_[a] -= forced ? 1 : std::min(modules, shields + 1);' \
       'invModules_[a] -= 0;'
run_case M5_consume_removed

# M6: producer ignores the research gate (modules from turn 1 -> t20 law dies).
mutate 'if (!moduleLegal) continue;
            ++invModules_[o];' \
       '++invModules_[o];'
run_case M6_producer_ungated

echo "DONE md5-check:"
md5sum "$F"
