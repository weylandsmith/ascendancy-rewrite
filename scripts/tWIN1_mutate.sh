#!/usr/bin/env bash
# tWIN-1 MUTATION CYCLE: three deviations from the single-window eject
# handoff, each must be CAUGHT by a NAMED pin in
# rewrite/tests/test_windowcount_tWIN1.cpp (or a sibling). Law: restore()
# COPIES BACK then md5-verifies (tPF-6 incident); never git-checkout
# mid-cycle (tPF-7a); run run_tests directly; a nonzero rc with no FAIL
# line counts CAUGHT (tPF-10); REBUILD before any later witness.
set -u
cd "$(dirname "$0")/.."
TITLE=rewrite/src/ui/title.cpp
MAIN=rewrite/src/main.cpp
cp "$TITLE" /tmp/twin1_title.bak; cp "$MAIN" /tmp/twin1_main.bak
TITLE_MD5=$(md5sum "$TITLE" | cut -d' ' -f1); MAIN_MD5=$(md5sum "$MAIN" | cut -d' ' -f1)
restore() { cp /tmp/twin1_title.bak "$TITLE"; cp /tmp/twin1_main.bak "$MAIN";
  [ "$(md5sum "$TITLE" | cut -d' ' -f1)" = "$TITLE_MD5" ] || { echo "RESTORE FAIL title"; exit 2; }
  [ "$(md5sum "$MAIN" | cut -d' ' -f1)" = "$MAIN_MD5" ] || { echo "RESTORE FAIL main"; exit 2; }; }
trap restore EXIT

verdict() { # $1 = mutation label
  cmake --build rewrite/build -j2 >/tmp/twin1_mut_build.log 2>&1 || { echo "$1 CAUGHT (build)"; tail -5 /tmp/twin1_mut_build.log; restore; return; }
  out=$(./rewrite/build/run_tests 2>&1); rc=$?
  name=$(echo "$out" | grep -m1 "FAILED" | head -1)
  [ -z "$name" ] && name=$(echo "$out" | grep " FAIL" | head -1)
  [ -z "$name" ] && name=$(echo "$out" | tail -1)
  if [ $rc -ne 0 ]; then echo "$1 CAUGHT by: $name"; else echo "$1 SURVIVED — PIN VACUOUS"; fi
  restore
}

# M1: THE ORIGINAL DEFECT — drop the 12th arg (windowIn) from the
# re-entry call (restores the exact pre-fix two-window shape). Matches
# '&newGame,' + the comment block + the bare 'handedWindow);' line.
perl -0pi -e 's/&newGame,\n(?:\s*\/\/[^\n]*\n)*\s*handedWindow\);/\&newGame);/' "$MAIN"
# Guard: the title call must now END at '&newGame);' (the campaign call
# still legitimately contains 'handedWindow);' — grep for that was a
# false-negative trap).
grep -q "&loreForUi(o), &newGame);" "$MAIN" || { echo "M1 NOT APPLIED"; exit 2; }
verdict M1
# M2: keep the slot but poison it — bare-line 'handedWindow);' becomes
# 'nullptr);' (compiles: void* param; recreates the bug at runtime while
# the arg COUNT stays 12). Anchored to the bare line so the runCampaignUi
# call ('&toTitle, &handedWindow);') is untouched.
perl -0pi -e 's/^(\s+)handedWindow\);/$1nullptr);/m' "$MAIN"
grep -qE "^\s+nullptr\);" "$MAIN" || { echo "M2 NOT APPLIED"; exit 2; }
grep -q "&toTitle, &handedWindow);" "$MAIN" || { echo "M2 OVERREACH (hit campaign call)"; exit 2; }
verdict M2
# M3: title creates UNCONDITIONALLY (winOwned gate neutered) — the cast
# stays, the single-window law dies.
perl -0pi -e 's/if \(winOwned\)\n(\s*)win = SDL_CreateWindow/if (true)\n$1win = SDL_CreateWindow/' "$TITLE"
grep -q "if (true)" "$TITLE" || { echo "M3 NOT APPLIED"; exit 2; }
verdict M3
echo "MUTATION CYCLE DONE"
