#!/usr/bin/env bash
# tPL-V1f census MUTATION witness: re-introduce the t418 transposed law in
# tileCenter (planetview.cpp), rebuild, re-run witness+capture, and assert the
# census FAILS (the census is not vacuous). ALWAYS restores + rebuilds green.
set -u
cd "$(dirname "$0")/.."
SRC=rewrite/src/ui/planetview.cpp
SNAP=/tmp/tplv1f_planetview.snapshot
MOUT=/tmp/tplv1_shots_m1
md5sum "$SRC"
cp "$SRC" "$SNAP"
trap 'cp "$SNAP" "$SRC"; touch "$SRC"; (cd rewrite && cmake --build build -j4 >/tmp/tplv1f_rebuild.log 2>&1); md5sum "$SRC"; echo RESTORED' EXIT
# mutant M-T1: transposed cursors (the pre-tPL-V1 law A)
python3 - <<'EOF'
p = "rewrite/src/ui/planetview.cpp"
s = open(p).read()
old = "return Pt{410 + col * 34 - row * 34, 127 + col * 17 + row * 17};"
new = "return Pt{110 + col * 34 + row * 17, 410 + col * 17 - row * 34};"
assert s.count(old) == 1, s.count(old)
open(p, "w").write(s.replace(old, new))
EOF
echo "MUTANT applied"
(cd rewrite && cmake --build build -j4 >/tmp/tplv1f_build_mut.log 2>&1); echo BUILD_EXIT=$?
OUT=$MOUT DISP=:99 timeout 100 bash scripts/tplv1_port_witness.sh >/tmp/tplv1f_witness_mut.log 2>&1; echo WITNESS_EXIT=$?
ls -la "$MOUT"/*.png 2>/dev/null | wc -l
SHOT=$MOUT/planet-open.png ~/tools/revenv/bin/python scripts/tplv1f_census_v2.py
CENSUS_EXIT=$?
echo "MUTANT CENSUS_EXIT=$CENSUS_EXIT (want nonzero = census catches the transposition)"
