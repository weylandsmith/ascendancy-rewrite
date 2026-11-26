#!/usr/bin/env bash
# tPF-11 mutation campaign (rules: snapshot+md5 preflight, restore COPY-BACK
# then md5-verify, anchors at DEFINITION sites with count==1 assert; a
# nonzero exit with no FAIL line = crash = CAUGHT, tPF-10 trap).
set -u
cd "$(dirname "$0")/.."
B=rewrite/src/ui/statusbg.cpp
H=rewrite/src/ui/statusbg.h
U=rewrite/src/ui/ui.cpp
D=/tmp/tpf11_mut
mkdir -p $D
cp "$B" "$D/statusbg.cpp.snap"
cp "$H" "$D/statusbg.h.snap"
cp "$U" "$D/ui.cpp.snap"
md5sum $D/*.snap
restore() {
  cp "$D/statusbg.cpp.snap" "$B"
  cp "$D/statusbg.h.snap" "$H"
  cp "$D/ui.cpp.snap" "$U"
  for f in "$B" "$H" "$U"; do
    s=$D/$(basename "$f").snap
    a=$(md5sum "$f" | cut -d' ' -f1); b=$(md5sum "$s" | cut -d' ' -f1)
    [ "$a" = "$b" ] || { echo "RESTORE VERIFY FAIL $f"; exit 2; }
  done
}
run_mutant() { # <name> <file> <old> <new>
  local name=$1 file=$2 old=$3 new=$4
  python3 - "$file" "$old" "$new" <<'EOF'
import sys
p, old, new = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(p).read()
n = s.count(old)
assert n == 1, f"anchor count {n} != 1 in {p}"
open(p, "w").write(s.replace(old, new))
EOF
  if [ $? -ne 0 ]; then echo "$name ANCHOR FAIL"; restore; return 1; fi
  ( cd rewrite/build && cmake --build . --target run_tests -j8 > /tmp/tpf11_mut/build.log 2>&1 )
  if [ $? -ne 0 ]; then echo "$name BUILD FAIL" && tail -5 /tmp/tpf11_mut/build.log && restore && return 1; fi
  cd rewrite/build
  ./run_tests > /tmp/tpf11_mut/run.log 2>&1
  RC=$?
  cd ../..
  OUT=$( grep -c "FAIL " /tmp/tpf11_mut/run.log )
  if [ "$OUT" -ge 1 ]; then echo "$name CAUGHT (failing checks: $OUT)"
  elif [ "$RC" -ne 0 ]; then echo "$name CAUGHT (crash rc=$RC)"
  else echo "$name SURVIVED"; fi
  restore
}

# M1: band membership dead at the DEFINITION (no chrome pixel anywhere).
run_mutant M1_band_membership_dropped "$B" \
'        if (x >= r.x0 && x <= r.x1 && y >= r.y0 && y <= r.y1) return true;' \
'        if (false) return true;'

# M2: ramp y43 research mode swapped for the STATUS mode (per-screen split
# broken — the measured (33,56,57) 118 / (24,48,41) 114 becomes the wrong
# one; pin 3 asserts exact RGB).
run_mutant M2_ramp43_status_mode "$B" \
'        case 43: *out = RGB{33, 56, 57}; return true;   // 118 vs (24,48,41) 114' \
'        case 43: *out = RGB{24, 48, 41}; return true;   // MUTANT'

# M3: research paint arm unwired (wiring pin load-bearing, tPF-7 M4 lesson).
run_mutant M3_paint_arm_unwired "$U" \
'        if (screen == kScreenResearch) {
            SDL_Rect black{0, 0, kDisplayW, kDisplayH};' \
'        if (false) {
            SDL_Rect black{0, 0, kDisplayW, kDisplayH};'

# M4: ramp loop extended to the status tail (y46 measured BLACK 580/580 —
# the per-screen split must not leak).
run_mutant M4_ramp_loop_leaks_y46 "$U" \
'            for (int y = 38; y <= 45; y++) {
                RGB c;
                if (!resRampColourAt(y, &c)) continue;' \
'            for (int y = 38; y <= 46; y++) {
                RGB c;
                if (!resRampColourAt(y, &c)) continue;'

# M5: bottom band moved up to y472 (the measured tree-field flush-black row
# — census + pin 1 edge case). ANCHOR AT THE .h INLINE TABLE (tPF-10 M2
# lesson: constexpr tables live with their declaration).
run_mutant M5_bottom_band_y472 "$H" \
'    {0, 473, 639, 479},  // bottom rows 473..479 (y472 measured BLACK)' \
'    {0, 472, 639, 479},  // MUTANT'

echo "--- post-campaign green check ---"
cd rewrite/build && cmake --build . --target run_tests -j8 >/dev/null 2>&1 && ./run_tests 2>&1 | tail -1
