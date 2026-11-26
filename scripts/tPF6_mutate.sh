#!/usr/bin/env bash
# tPF-6 mutation campaign: prove the armed-cell pins are load-bearing.
# Traps honoured (mutation-campaign rules 9/10): pgrep is the ONLY liveness
# test; never touch target files until the run is done; verify the build ran
# before trusting any survival verdict; md5-verified restore after each.
set -u
cd /home/hrethric/projects/ascendancy
SRC=rewrite/src/ui/planetview.cpp
SRC2=rewrite/src/ui/ui.cpp
SNAP=/tmp/tpf6_snap_$(basename $SRC).md5
md5sum $SRC $SRC2 > /tmp/tpf6_snap.md5
BUILD=rewrite/build
run_case() { # run_case <label>
  (cd $BUILD && cmake --build . -j4 --target run_tests > /tmp/tpf6_mut_build_$1.log 2>&1)
  local brc=$?
  if [ $brc -ne 0 ]; then echo "$1 BUILD FAILED (not a survival)"; tail -3 /tmp/tpf6_mut_build_$1.log; return 2; fi
  local out; out=$($BUILD/run_tests 2>&1 | tail -1)
  echo "$1: $out"
}
restore() {
  while pgrep -f "run_tests" > /dev/null; do sleep 1; done
  cp /tmp/tpf6_pv.orig $SRC; cp /tmp/tpf6_ui.orig $SRC2
  python3 - "$SRC" "$SRC2" <<'PY'
import sys, hashlib
want = {}
for line in open('/tmp/tpf6_snap.md5'):
    h, p = line.split()
    want[p.strip()] = h
for p in sys.argv[1:]:
    got = hashlib.md5(open(p,'rb').read()).hexdigest()
    print('restore', p, 'OK' if got == want.get(p) else 'MISMATCH got '+got)
PY
}
# baseline
cp $SRC /tmp/tpf6_pv.orig; cp $SRC2 /tmp/tpf6_ui.orig
run_case baseline
# M1: drop the filter block (armedCell ignored)
python3 - <<'PY'
s=open('rewrite/src/ui/planetview.cpp').read()
old="""        if (armedCell >= 0 &&
            placementBlock(camp, star, id, armedCell) != PlacementBlock::None)
            continue;  // the vendor's Build button never appears for this
                       // (item, cell) — so the row never appears either"""
assert old in s
open('rewrite/src/ui/planetview.cpp','w').write(s.replace(old,"        // M1 mutant: filter dropped"))
PY
run_case M1_drop_filter
restore
# M2: polarity inversion (keep ONLY refused items)
python3 - <<'PY'
s=open('rewrite/src/ui/planetview.cpp').read()
old="placementBlock(camp, star, id, armedCell) != PlacementBlock::None)"
assert old in s
open('rewrite/src/ui/planetview.cpp','w').write(s.replace(old,"placementBlock(camp, star, id, armedCell) == PlacementBlock::None)  // M2"))
PY
run_case M2_invert_polarity
restore
# M3: wiring — one call site drops the armed argument (wiring pin is
# source-text; still rebuild so the binary matches the tree)
python3 - <<'PY'
s=open('rewrite/src/ui/ui.cpp').read()
old="""                    const auto opts = projectOptionsFor(
                        camp, planetStar,
                        planetCellArmed ? planetCell : -1);"""
assert old in s
open('rewrite/src/ui/ui.cpp','w').write(s.replace(old,"                    const auto opts = projectOptionsFor(camp, planetStar);  // M3",1))
PY
run_case M3_unwire_painter
restore
run_case after_restore
echo MUTATION-DONE
