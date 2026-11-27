#!/usr/bin/env bash
# tESC-1 MUTATION CYCLE: three deviations from the eject law, each must be
# CAUGHT by a named pin. Law: restore() COPIES BACK then md5-verifies
# (tPF-6 incident); never git-checkout mid-cycle (tPF-7a); run_tests
# directly (ctest FAIL lines live in LastTest.log, tPF-6 ship note).
set -u
cd "$(dirname "$0")/.."
UI=rewrite/src/ui/ui.cpp
MAIN=rewrite/src/main.cpp
cp "$UI" /tmp/tesc1_ui.bak; cp "$MAIN" /tmp/tesc1_main.bak
UI_MD5=$(md5sum "$UI" | cut -d' ' -f1); MAIN_MD5=$(md5sum "$MAIN" | cut -d' ' -f1)
restore() { cp /tmp/tesc1_ui.bak "$UI"; cp /tmp/tesc1_main.bak "$MAIN";
  [ "$(md5sum "$UI" | cut -d' ' -f1)" = "$UI_MD5" ] || { echo "RESTORE FAIL ui"; exit 2; }
  [ "$(md5sum "$MAIN" | cut -d' ' -f1)" = "$MAIN_MD5" ] || { echo "RESTORE FAIL main"; exit 2; }; }
trap restore EXIT

verdict() { # $1 = mutation label
  cmake --build rewrite/build -j2 >/tmp/tesc1_mut_build.log 2>&1 || { echo "$1 CAUGHT (build)"; tail -5 /tmp/tesc1_mut_build.log; restore; return; }
  out=$(./rewrite/build/run_tests 2>&1); rc=$?
  name=$(echo "$out" | grep -m1 -B0 "FAILED\|.*FAIL" | head -1)
  [ -z "$name" ] && name=$(echo "$out" | grep -m1 -v "^$" | tail -1)
  if [ $rc -ne 0 ]; then echo "$1 CAUGHT by: $name"; else echo "$1 SURVIVED — PIN VACUOUS"; fi
  restore
}

# M1: eject leg stops setting the flag (old quit-at-bottom behaviour).
perl -0pi -e 's/\n(\s*)toTitle = true;/\n$1\/\/ toTitle = true;/' "$UI"
grep -q '// toTitle = true;' "$UI" || { echo "M1 NOT APPLIED"; exit 2; }
verdict M1
# M2: window destroyed even on the eject handoff.
perl -0pi -e 's/if \(owned && !handOff\) SDL_DestroyWindow/if (owned) SDL_DestroyWindow/' "$UI"
grep -q 'if (owned) SDL_DestroyWindow(win);' "$UI" || { echo "M2 NOT APPLIED"; exit 2; }
verdict M2
# M3: main() never re-enters (breaks unconditionally after campaign).
perl -0pi -e 's/if \(!toTitle\) break;/if (true) break;/' "$MAIN"
grep -q 'if (true) break;' "$MAIN" || { echo "M3 NOT APPLIED"; exit 2; }
verdict M3
echo "MUTATION CYCLE DONE"
