#!/usr/bin/env bash
# t407 mutation campaign: mutate fleetlist law sites one at a time; each MUST
# make run_tests fail with a NAMED line. Revert by FILE COPY (skill rule:
# never git-checkout mid-flight; snapshot first).
set -u
cd "$(dirname "$0")/.."
ROOT=$PWD
SRC=$ROOT/rewrite/src/ui/fleetlist.cpp
SNAP=/tmp/t407-snap/$(basename $SRC)
mkdir -p /tmp/t407-snap && cp "$SRC" "$SNAP"
cd "$ROOT/rewrite/build"
run() { ./run_tests 2>&1 | grep -E "fleetlist.*FAIL|fleetlist.*FAILED" | head -2; }
verdict() { # $1 name, $2 output
  if [ -n "$2" ]; then echo "M$1 CAUGHT: $2"; else echo "M$1 *** SURVIVED ***"; fails=1; fi; }
fails=0

mutate() { # $2=python expr file-wide
  cp "$SNAP" "$SRC"
  python3 - "$SRC" <<PYEOF
import sys
p=sys.argv[1]; s=open(p).read()
$2
open(p,'w').write(s)
PYEOF
  cmake --build . --target run_tests -j4 >/dev/null 2>&1 || { echo "build fail"; return; }
}

mutate 1 "s=s.replace('if (f[i].owner == owner) out.push_back','if (true) out.push_back')"
v=$(run); verdict 1 "$v"

mutate 2 "s=s.replace('const int s = std::clamp(scroll, 0, maxScroll);','const int s = scroll;')"
v=$(run); verdict 2 "$v"

mutate 3 "s=s.replace('inline constexpr int kFleetRowsRight = 605','inline constexpr int kFleetRowsRight = 639')"
# constant lives in the header:
cp "$SNAP" "$SRC"   # (no-op for cpp; header mutant applied below)
export ROOT
python3 - <<'PYEOF'
import os
p=os.environ['ROOT']+'/rewrite/src/ui/fleetlist.h'; s=open(p).read()
open('/tmp/t407-snap/fleetlist.h','w').write(s)
s=s.replace('kFleetRowsRight = 605','kFleetRowsRight = 639')
open(p,'w').write(s)
PYEOF
cmake --build . --target run_tests -j4 >/dev/null 2>&1
v=$(run); verdict 3 "$v"
cp /tmp/t407-snap/fleetlist.h "$ROOT/rewrite/src/ui/fleetlist.h"

mutate 4 "s=s.replace('return std::max(0, systems + 1 - ships);','return systems + 1 - ships;')"
v=$(run); verdict 4 "$v"

mutate 5 "s=s.replace('if (it && it->name == \"Ship\") return it->name;','if (it && it->name == \"Factory\") return it->name;')"
v=$(run); verdict 5 "$v"

mutate 6 "s=s.replace('h.kind = FleetHit::ArrowUp','h.kind = FleetHit::ArrowDown',1)"
v=$(run); verdict 6 "$v"

# restore + rebuild green
cp "$SNAP" "$SRC"
cp /tmp/t407-snap/fleetlist.h "$ROOT/rewrite/src/ui/fleetlist.h"
cmake --build . --target run_tests -j4 >/dev/null 2>&1
./run_tests 2>&1 | tail -1
echo "MUTATION CAMPAIGN DONE fails=$fails"
