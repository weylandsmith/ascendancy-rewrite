#!/usr/bin/env bash
# tPF-1d mutation campaign: prove the quit-cause pins are load-bearing.
# RESTORE LAW (tPF-6 incident): restore() COPIES BACK then md5-verifies;
# verify-only leaves mutations on disk. NEVER git-checkout mid-cycle (tPF-7a).
# Verdict law: run_tests prints per-test FAIL; a nonzero rc with no FAIL line
# still counts CAUGHT (harness CHECK does not return).
set -u
cd "$(dirname "$0")/.."
F=rewrite/src/ui/ui.cpp
BAK=/tmp/tpf1d_ui.cpp.bak
cp "$F" "$BAK"
MD5=$(md5sum "$F" | cut -d' ' -f1)
restore() { cp "$BAK" "$F"; NOW=$(md5sum "$F" | cut -d' ' -f1);
  [ "$NOW" = "$MD5" ] || { echo "RESTORE FAILED md5 $NOW != $MD5"; exit 3; }; }
trap restore EXIT

mutate() { # $1=old $2=new  (python for exact single-occurrence replace)
  python3 - "$F" "$1" "$2" <<'PY'
import sys
p, o, n = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(p).read()
assert s.count(o) == 1, f"occurrences {s.count(o)} for {o[:40]!r}"
open(p, "w").write(s.replace(o, n))
PY
}

run_case() { # $1=name
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

# M1: victory cause loses the enum name (hardcoded word) -> names_enum pin
mutate 'std::string("victory:") + ag::victoryName(camp.victory());' 'std::string("victory");'
run_case M1_victory_no_enum

# M2: cause print moved AFTER ui ok (swap the two printf statements)
mutate 'std::printf("ui quit cause=%s turn=%d\n", quitCause.c_str(),
                camp.turn());
    std::printf("ui ok: turn %d\n", camp.turn());' 'std::printf("ui ok: turn %d\n", camp.turn());
    std::printf("ui quit cause=%s turn=%d\n", quitCause.c_str(),
                camp.turn());'
run_case M2_print_after_uiok

# M3: sdl-window-close leg neutered (back to bare quit=true) -> census pin
mutate 'if (ev.type == SDL_QUIT) {
                quitCause = "sdl-window-close";  // tPF-1d
                quit = true;
            }' 'if (ev.type == SDL_QUIT) quit = true;'
run_case M3_sdl_leg_neutered

echo "MUTATION DONE; after-restore md5: $(md5sum "$F")"
