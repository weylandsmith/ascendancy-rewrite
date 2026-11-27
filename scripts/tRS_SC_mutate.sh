#!/usr/bin/env bash
# tRS-SC MUTATION CYCLE — proves the scroll pins catch regressions.
# M1: tick reverts to the posZ dolly (the ORIGINAL D32-L4 defect)
# M2: resClampPosY neutered (returns posY unclamped)
# M3: the ui.cpp paint-site clamp commented out
# M4: projection drops -cam.posY from vY (scroll invisible)
# Law: every mutant must FAIL the suite; restore + md5-verify after each.
set -u
cd "$(dirname "$0")/.."
RV=rewrite/src/ui/researchview.cpp
RH=rewrite/src/ui/researchview.h
UI=rewrite/src/ui/ui.cpp
BK=$(mktemp -d /tmp/tRS-SC-mut.XXXXXX)
cp "$RV" "$RH" "$UI" "$BK/"
md5_orig() { md5sum "$RV" "$RH" "$UI" | awk '{print $1}'; }
restore() { cp "$BK/researchview.cpp" "$RV"; cp "$BK/researchview.h" "$RH"; cp "$BK/ui.cpp" "$UI"; }
verify() {
  if [ "$(md5_orig)" != "$( (md5sum "$BK/researchview.cpp" "$BK/researchview.h" "$BK/ui.cpp" | awk '{print $1}') | tr '\n' ' ' | sed 's/ $//' )"; then
    # compare in same order
    a=$(md5sum "$BK/researchview.cpp" | awk '{print $1}')
    b=$(md5sum "$BK/researchview.h" | awk '{print $1}')
    c=$(md5sum "$BK/ui.cpp" | awk '{print $1}')
    x=$(md5sum "$RV" | awk '{print $1}'); y=$(md5sum "$RH" | awk '{print $1}'); z=$(md5sum "$UI" | awk '{print $1}')
    if [ "$a" != "$x" ] || [ "$b" != "$y" ] || [ "$c" != "$z" ]; then
      echo "RESTORE MD5 MISMATCH"; return 1
    fi
  fi
  echo "restore md5-ok"
}
run_suite_fails() {
  cmake --build rewrite/build -j4 >/dev/null 2>&1
  rewrite/build/run_tests 2>&1 | grep -c 'FAIL' || true
}

apply_m1() {
  python3 - "$RV" <<'EOF'
import sys
p=sys.argv[1]; s=open(p).read()
old="""    if (latchMove == 1) posY -= kScrollStep;
    else if (latchMove == 2) posY += kScrollStep;"""
new="""    if (latchMove == 1) posZ -= kScrollStep;
    else if (latchMove == 2) posZ += kScrollStep;"""
assert old in s, "M1 NOT APPLIED"
open(p,"w").write(s.replace(old,new))
EOF
}
apply_m2() {
  python3 - "$RV" <<'EOF'
import sys
p=sys.argv[1]; s=open(p).read()
old="""    if (posY < double(lo)) return double(lo);  // 0x47f89..0x47fa2
    if (posY > double(hi)) return double(hi);  // 0x47fa4..0x47fbd
    return posY;"""
new="""    return posY;"""
assert old in s, "M2 NOT APPLIED"
open(p,"w").write(s.replace(old,new))
EOF
}
apply_m3() {
  python3 - "$UI" <<'EOF'
import sys
p=sys.argv[1]; s=open(p).read()
old="                    resCam.posY = resClampPosY(resGeom, nodes, resCam.posY);"
new="                    // resCam.posY = resClampPosY(resGeom, nodes, resCam.posY);"
assert old in s, "M3 NOT APPLIED"
open(p,"w").write(s.replace(old,new))
EOF
}
apply_m4() {
  python3 - "$RV" <<'EOF'
import sys
p=sys.argv[1]; s=open(p).read()
old="            const double vY = double(w.y) - cam.posY;"
new="            const double vY = double(w.y);"
assert old in s, "M4 NOT APPLIED"
open(p,"w").write(s.replace(old,new))
EOF
}

overall=0
for m in M1 M2 M3 M4; do
  restore
  fn="apply_$(echo $m | tr 'A-Z' 'a-z')"
  if ! $fn; then echo "$m NOT APPLIED"; overall=1; continue; fi
  n=$(run_suite_fails)
  if [ "$n" -ge 1 ]; then echo "$m CAUGHT ($n FAIL lines)"; else echo "$m SURVIVED"; overall=1; fi
  restore; verify || overall=1
done
cmake --build rewrite/build -j4 >/dev/null 2>&1
echo "OVERALL=$overall"
rm -rf "$BK"
exit $overall
