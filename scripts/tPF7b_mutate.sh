#!/usr/bin/env bash
# tPF-7b mutation campaign. RULES (banked tPF-5/6/7): restore() COPY BACKS
# from /tmp snapshots THEN md5-verifies; pgrep is the only liveness test;
# stdout block-buffered; ANCHOR AT THE DEFINITION (M1 is the constant's own
# definition line in cam3d.h — the pattern tPF-7 M5's failure taught).
set -u
cd "$(dirname "$0")/.."
H=rewrite/src/ui/cam3d.h
UI=rewrite/src/ui/ui.cpp
BUILD=rewrite/build

restore() {
  cp /tmp/tpf7b_cam3d.h.bak "$H"
  cp /tmp/tpf7b_ui.cpp.bak "$UI"
  a=$(md5sum "$H" | cut -d' ' -f1); b=$(md5sum "$UI" | cut -d' ' -f1)
  [ "$a" = d61649139e342c36bc2735a068005e0d ] && [ "$b" = 9db07a9acaeb85ea8c626ff189528390 ] \
    || { echo "RESTORE FAILED md5 h=$a ui=$b — ABORT, fix by hand"; exit 9; }
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

# M1: cadence back to the poll-limited misread (at the DEFINITION)
run_mutant M1 "$H" "static constexpr int kFireLoopMs = 34;" "static constexpr int kFireLoopMs = 1000;"
# M2: cosmos gate re-anchored on a stale 1000 literal (defect-shape mutant:
# the constant survives but a gate no longer uses it -> wiring pin must fire)
run_mutant M2 "$UI" "if (cam.moving() && nowMs - lastPumpMs >= (Uint32)Camera3d::kFireLoopMs) {" "if (cam.moving() && nowMs - lastPumpMs >= 1000u) {"
# M3: systemCam gate unwired to the constant (same shape, second gate)
run_mutant M3 "$UI" "nowMs - lastSysPumpMs >= (Uint32)Camera3d::kFireLoopMs" "nowMs - lastSysPumpMs >= 1000u"
# M4: witness instruments removed (pins must catch: census law needs them)
run_mutant M4 "$UI" "std::printf(\"ui cosmos pump yaw %.3f\\n\", cam.yawLog());" "/* mutant: instrument removed */"
# M5: cadence mutated to a value OUTSIDE the measured band but still < 100
# (kills a pin that only checked the magnitude, not the measured bands)
run_mutant M5 "$H" "static constexpr int kFireLoopMs = 34;" "static constexpr int kFireLoopMs = 60;"

echo "== FINAL STATE"
./rewrite/build/run_tests 2>/dev/null | tail -1
