#!/usr/bin/env bash
# t407 mutation campaign: mutate fleetlist law sites one at a time; each MUST
# make the fleetlist tests fail with a NAMED line. Revert by FILE COPY (skill
# rule: never git-checkout mid-flight; snapshot first).
#
# t408 FIX (two bugs, both measured — docs/re/fleet-screen.md F13):
#  (1) VACUOUS VERDICT: run() grepped "fleetlist.*FAIL" but harness.h:52
#      prints "FAIL <file>:<line>" — FAIL comes FIRST, so the pattern could
#      never match and every mutant read SURVIVED. Verdict is now the filtered
#      run_tests EXIT CODE (run_tests supports a substring filter:
#      `./run_tests fleetlist` -> 8 tests), with the FAIL lines printed.
#  (2) CWD: every consumer now uses absolute paths ($ROOT/...); the build dir
#      is created if absent so a fresh clone cannot silently no-op the build.
set -u
cd "$(dirname "$0")/.."
ROOT=$PWD
SRC=$ROOT/rewrite/src/ui/fleetlist.cpp
HDR=$ROOT/rewrite/src/ui/fleetlist.h
BUILD=$ROOT/rewrite/build
SNAP=/tmp/t407-snap
mkdir -p "$SNAP" "$BUILD"
cp "$SRC" "$SNAP/fleetlist.cpp"
cp "$HDR" "$SNAP/fleetlist.h"

fails=0
run() { (cd "$BUILD" && ./run_tests fleetlist 2>&1); }
verdict() { # $1 name, $2 exit code, $3 output
  local named
  v_named=$(printf '%s\n' "$3" | grep -E '^ *FAIL ' | head -3)
  if [ "$2" -ne 0 ]; then
    echo "M$1 CAUGHT (rc=$2): $(printf '%s' "$v_named" | tr '\n' '|')"
  else
    echo "M$1 *** SURVIVED *** (rc=0, no FAIL line)"
    fails=1
  fi
}
build() { cmake -S "$ROOT/rewrite" -B "$BUILD" >/dev/null 2>&1; cmake --build "$BUILD" --target run_tests -j4 >/dev/null 2>&1; }

mutate() { # $1=name, $2=file, $3=python expr on `s`
  cp "$SNAP/fleetlist.cpp" "$SRC"
  cp "$SNAP/fleetlist.h" "$HDR"
  python3 - "$2" <<PYEOF
import sys
p=sys.argv[1]; s=open(p).read()
$3
open(p,'w').write(s)
PYEOF
  build || { echo "M$1 BUILD FAIL"; fails=1; }
}

mutate 1 "$SRC" "s=s.replace('if (f[i].owner == owner) out.push_back','if (true) out.push_back')"
out=$(run); verdict 1 $? "$out"

mutate 2 "$SRC" "s=s.replace('const int s = std::clamp(scroll, 0, maxScroll);','const int s = scroll;')"
out=$(run); verdict 2 $? "$out"

mutate 3 "$HDR" "s=s.replace('kFleetRowsRight = 605','kFleetRowsRight = 639')"
out=$(run); verdict 3 $? "$out"

mutate 4 "$SRC" "s=s.replace('return std::max(0, systems + 1 - ships);','return systems + 1 - ships;')"
out=$(run); verdict 4 $? "$out"

mutate 5 "$SRC" "s=s.replace('it->name == \"Ship\"','it->name == \"Factory\"')"
out=$(run); verdict 5 $? "$out"

mutate 6 "$SRC" "s=s.replace('h.kind = FleetHit::ArrowUp','h.kind = FleetHit::ArrowDown',1)"
out=$(run); verdict 6 $? "$out"

# restore + rebuild green
cp "$SNAP/fleetlist.cpp" "$SRC"
cp "$SNAP/fleetlist.h" "$HDR"
build
(cd "$BUILD" && ./run_tests 2>&1 | tail -1)
echo "MUTATION CAMPAIGN DONE fails=$fails"
