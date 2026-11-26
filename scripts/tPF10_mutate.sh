#!/usr/bin/env bash
# tPF-10 mutation campaign (rules: snapshot+md5 preflight, restore COPY-BACK
# then md5-verify, anchors at DEFINITION sites with count==1 assert, one
# mutant per run — skeleton per scripts/tPF9_mutate.sh).
set -u
cd "$(dirname "$0")/.."
V=rewrite/src/ui/researchview.cpp
H=rewrite/src/ui/researchview.h
U=rewrite/src/ui/ui.cpp
D=/tmp/tpf10_mut
mkdir -p $D
cp "$V" "$D/researchview.cpp.snap"
cp "$H" "$D/researchview.h.snap"
cp "$U" "$D/ui.cpp.snap"
md5sum $D/*.snap
restore() {
  cp "$D/researchview.cpp.snap" "$V"
  cp "$D/researchview.h.snap" "$H"
  cp "$D/ui.cpp.snap" "$U"
  for f in "$V" "$H" "$U"; do
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
  ( cd rewrite/build && cmake --build . --target run_tests -j8 > /tmp/tpf10_mut/build.log 2>&1 )
  if [ $? -ne 0 ]; then echo "$name BUILD FAIL"; tail -5 /tmp/tpf10_mut/build.log; restore; return 1; fi
  # Run and count FAILs; a nonzero exit with NO "FAIL " line is a CRASH
  # (tPF-10 M3: substr(npos) threw mid-suite) — also CAUGHT, never SURVIVED.
  cd rewrite/build
  ./run_tests > /tmp/tpf10_mut/run.log 2>&1
  RC=$?
  cd ../..
  OUT=$( grep -c "FAIL " /tmp/tpf10_mut/run.log )
  if [ "$OUT" -ge 1 ]; then echo "$name CAUGHT (failing checks: $OUT)"
  elif [ "$RC" -ne 0 ]; then echo "$name CAUGHT (crash rc=$rc, rc=$RC — counted as caught)"
  else echo "$name SURVIVED"; fi
  restore
}

# M1: frame law broken at the DEFINITION — hover override dropped (D28 item
# 20's blue highlight can never paint).
run_mutant M1_hover_override_dropped "$V" \
'    if (hover) esi = 2;' \
'    if (false) esi = 2;'

# M2: hover word never clears off-disk (0xffff leg removed — the blue ring
# sticks to the last disk forever). ANCHOR AT THE INLINE DEFINITION (.h).
run_mutant M2_offdisk_leg_removed "$H" \
'    const int hit = (h.kind == ResHit::Node) ? h.row : -1;  // 0xffff leg' \
'    const int hit = (h.kind == ResHit::Node) ? h.row : prev;  // MUTANT'

# M3: motion wiring removed (wiring pin is load-bearing, tPF-7 M4 lesson).
run_mutant M3_motion_leg_unwired "$U" \
'                if (screen == kScreenResearch && camp.researchTree()) {
                    const auto nodes =
                        researchNodes(camp, *camp.researchTree(), ag::kPlayer);' \
'                if (false) {
                    const auto nodes =
                        researchNodes(camp, *camp.researchTree(), ag::kPlayer);'

# M4: pump leg removed (camera-slide re-hit dead; item 19 persistence half).
run_mutant M4_pump_leg_unwired "$U" \
'                    const int hv = resHoverWord(resSel, h);
                    if (hv != resSel) {
                        resSel = hv;
                        std::printf("ui research hover %d\n", resSel);
                        std::fflush(stdout);
                    }
                }
            }
        }' \
'                }
            }
        }'

# M5: click leg reverts to a bare latch (D28 item 19's original defect).
run_mutant M5_click_bare_latch "$U" \
'                            resSel = resHoverWord(resSel, h);' \
'                            resSel = h.row;  // vendor selection word'

# Final sanity: tree back at snapshot and suite green.
( cd rewrite/build && cmake --build . --target run_tests -j8 > /tmp/tpf10_mut/build.log 2>&1 ) || { echo FINAL BUILD FAIL; exit 2; }
OUT=$( cd rewrite/build && ./run_tests 2>/dev/null | tail -1 )
echo "FINAL: $OUT"
