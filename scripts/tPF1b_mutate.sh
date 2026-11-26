#!/usr/bin/env bash
# tPF-1b MUTATION: prove the cap-line pins bite. Snapshot preflight, mutate
# ui.cpp, run ONLY the wiring pin, expect FAIL, restore, md5-verify.
# M1: cap latch removed (no capFired assignment) -> cBlock pin fails.
# M2: cap print moved BEFORE "ui ok" -> tail-window pin fails.
# M3: prefix dropped (plain printf) -> HARNESS-CAP tail pin fails.
set -u
cd /home/hrethric/projects/ascendancy
SRC=rewrite/src/ui/ui.cpp
SNAP=/tmp/tPF1b_ui.cpp.orig
BUILD=rewrite/build
md5sum "$SRC" | tee /tmp/tPF1b_md5.pre
cp "$SRC" "$SNAP"
md5sum "$SNAP" | awk '{print "snapshot md5",$1}'
PRE=$(md5sum "$SNAP" | awk '{print $1}')

runpin() { DISPLAY= "$BUILD/run_tests" 2>&1 | grep -E "timecont_wiring_tPF1" ; }

mutate() { # $1 python expr operating on text
  python3 - "$SRC" "$1" <<'EOF'
import sys
p, expr = sys.argv[1], sys.argv[2]
t = open(p).read()
t2 = eval(expr, {"t": t})
assert t2 != t, "mutation was a no-op"
open(p, "w").write(t2)
EOF
}

RESULT=""
for M in M1 M2 M3; do
  cp "$SNAP" "$SRC"
  case $M in
    M1) mutate "t.replace('capFired = turns;', '/*M1*/', 1)" ;;
    M2) mutate "t.replace('capFired = turns;', 'capFired = turns; std::printf(\"HARNESS-CAP: cap %d\\\\n\", turns);', 1)" ;;
    M3) mutate "t.replace('HARNESS-CAP: turn cap', 'turn cap', 1)" ;;
  esac
  if ! cmake --build "$BUILD" -j8 >/dev/null 2>&1; then echo "$M: BUILD FAILED (counts as caught: pin anchors reference broken)"; RESULT="$RESULT $M=BUILDFAIL"; continue; fi
  OUT=$(runpin)
  if echo "$OUT" | grep -q "FAIL"; then echo "$M: CAUGHT"; RESULT="$RESULT $M=CAUGHT";
  else echo "$M: SURVIVED — $OUT"; RESULT="$RESULT $M=SURVIVED"; fi
done

cp "$SNAP" "$SRC"
POST=$(md5sum "$SRC" | awk '{print $1}')
echo "restore md5 $POST pre $PRE"
[ "$POST" = "$PRE" ] && echo "MD5-VERIFIED RESTORE OK" || echo "MD5 MISMATCH — RESTORE MANUALLY FROM $SNAP"
cmake --build "$BUILD" -j8 >/dev/null 2>&1
echo "rebuild after restore: $?"
echo "RESULT:$RESULT"
