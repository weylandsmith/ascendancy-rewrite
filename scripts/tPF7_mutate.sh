#!/usr/bin/env bash
# tPF-7 mutation campaign. RULES (banked tPF-5/tPF-6): restore() COPY BACKS
# from /tmp snapshots THEN md5-verifies; pgrep is the only liveness test;
# stdout is block-buffered (no death inference from empty logs).
set -u
cd "$(dirname "$0")/.."
UI=rewrite/src/ui/ui.cpp
RV=rewrite/src/ui/researchview.h
BUILD=rewrite/build
T=tests/test_rescontrols_tpf7

restore() {
  cp /tmp/tpf7_ui.cpp.bak "$UI"
  cp /tmp/tpf7_rv.h.bak "$RV"
  cp /tmp/tpf7_rvc.cpp.bak rewrite/src/ui/researchview.cpp
  a=$(md5sum "$UI" | cut -d' ' -f1); b=$(md5sum "$RV" | cut -d' ' -f1)
  c=$(md5sum rewrite/src/ui/researchview.cpp | cut -d' ' -f1)
  [ "$a" = 698b3771e41698d332b854fdb55119df ] && [ "$b" = 248a97f86e85ac046cb17cdbc03c9796 ] \
    && [ "$c" = 2ac4d33cab69c50118ddc181e8f3f25a ] \
    || { echo "RESTORE FAILED md5 ui=$a rv=$b rvc=$c — ABORT, fix by hand"; exit 9; }
  (cd $BUILD && make -j8 run_tests >/dev/null 2>&1)
  ./rewrite/build/run_tests 2>/dev/null | tail -1
}

run_mutant() { # name, file, old, new
  echo "== MUTANT $1"
  python3 - "$2" "$2" "$3" "$4" <<'PYEOF'
import sys
p = sys.argv[1]
old, new = sys.argv[3], sys.argv[4]
s = open(p).read()
assert s.count(old) == 1, f"anchor count {s.count(old)} != 1 for {old[:40]!r}"
open(p, "w").write(s.replace(old, new))
PYEOF
  [ $? -ne 0 ] && { echo "ANCHOR FAIL $1"; restore; return; }
  (cd $BUILD && make -j8 run_tests >/dev/null 2>&1)
  OUT=$(./rewrite/build/run_tests 2>/dev/null | tail -1)
  echo "  $1 -> $OUT"
  case "$OUT" in *"0 failed"*) echo "SURVIVED $1 — pin gap!";; *) echo "CAUGHT $1";; esac
  restore
}

# M1: cadence back to the misread 1000 ms
run_mutant M1 "$RV" "static constexpr int kPumpMs = 34;" "static constexpr int kPumpMs = 1000;"
# M2: release no-ops (the pre-tPF-7 state of the law fns)
run_mutant M2 "$RV" "    void releaseRot() { latchRot = 0; }
    void releaseMove() { latchMove = 0; }" "    void releaseRot() {}
    void releaseMove() {}"
# M3: release bleeds across pairs (rot release also kills move)
run_mutant M3 "$RV" "    void releaseRot() { latchRot = 0; }" "    void releaseRot() { latchRot = 0; latchMove = 0; }"
# M4: button-up wiring removed (strings gone -> wiring pin must fire; the
# pure pins CANNOT see this, so the source-text pin is load-bearing here)
run_mutant M4 "$UI" "                if (resHold == 1) resCam.releaseRot();
                else resCam.releaseMove();" "                /* mutant: release leg removed */"
# M5: press law polarity flipped (pairA start/stop swapped) — pressPair is
# in researchview.cpp, NOT .h (first draft anchored the wrong file and died
# on the count==1 assert; re-run against the .cpp caught it, 22 fails)
run_mutant M5 rewrite/src/ui/researchview.cpp "        switch (state) { case 0: return 1; case 1: return 0;
                         case 2: return 3; default: return 1; }" "        switch (state) { case 0: return 0; case 1: return 1;
                         case 2: return 3; default: return 1; }"
echo "== FINAL (restored) =="
(cd $BUILD && make -j8 run_tests >/dev/null 2>&1)
./rewrite/build/run_tests 2>/dev/null | tail -1
