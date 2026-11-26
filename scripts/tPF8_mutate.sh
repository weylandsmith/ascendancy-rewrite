#!/usr/bin/env bash
# tPF-8 mutation campaign (rules: snapshot+md5 preflight, restore COPY-BACK
# then md5-verify, pgrep liveness n/a (run_tests is foreground), one mutant
# per run, never trust a sweep that did not finish).
set -u
cd "$(dirname "$0")/.."
C=rewrite/src/game/campaign.cpp
R=rewrite/src/ui/researchview.cpp
U=rewrite/src/ui/ui.cpp
D=/tmp/tpf8_mut
mkdir -p $D
for f in $C $R $U; do cp "$f" "$D/$(basename $f).snap"; done
md5sum $D/*.snap
# preflight: working tree must equal snapshots
for f in $C $R $U; do
  a=$(md5sum "$f" | cut -d' ' -f1); b=$(md5sum "$D/$(basename $f).snap" | cut -d' ' -f1)
  [ "$a" = "$b" ] || { echo "PREFLIGHT FAIL $f"; exit 2; }
done
restore() {
  for f in $C $R $U; do cp "$D/$(basename $f).snap" "$f"; done
  for f in $C $R $U; do
    a=$(md5sum "$f" | cut -d' ' -f1); b=$(md5sum "$D/$(basename $f).snap" | cut -d' ' -f1)
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
  ( cd rewrite/build && cmake --build . --target run_tests -j8 > /tmp/tpf8_mut/build.log 2>&1 )
  if [ $? -ne 0 ]; then echo "$name BUILD FAIL"; tail -5 /tmp/tpf8_mut/build.log; restore; return 1; fi
  OUT=$( cd rewrite/build && ./run_tests 2>&1 | grep -c "FAIL " )
  if [ "$OUT" -ge 1 ]; then echo "$name CAUGHT (failing checks: $OUT)"; else echo "$name SURVIVED"; fi
  restore
}

# M1: re-introduce the retired uncited opening grant (definition site).
run_mutant M1_grant_restored "$C" \
'    // tPF-8 OPENING-RESEARCH LAW: the vendor starts EVERY race with ZERO' \
'    for (auto& techSet : ownedTech)
        if (techSet.size() > 2) { techSet[0] = true; techSet[1] = true; techSet[2] = true; }
    // tPF-8 OPENING-RESEARCH LAW: the vendor starts EVERY race with ZERO'

# M2: state-law polarity — Blocked rows counted as frontier (0x46d3c bypass).
run_mutant M2_blocked_available "$R" \
'        s.legal = nd.state != TechNodeState::Blocked;  // 0x46d3c (P10)' \
'        s.legal = true;  // MUTANT'

# M3: drop the prereq-endpoint visibility gate in the ui edge loop.
run_mutant M3_edge_prereq_gate "$U" \
'                            if (!centres[size_t(pr)].visible) continue;' \
'                            ;'

# M4: roots frame law — Y viewport centre moved off-field (240 -> 640).
run_mutant M4_viewport_centre "$R" \
'                    resVendorRound(focal * vY / vZ + 0.5) + 240);' \
'                    resVendorRound(focal * vY / vZ + 0.5) + 640);' || true

echo "--- post-campaign green check ---"
( cd rewrite/build && cmake --build . --target run_tests -j8 > /tmp/tpf8_mut/build.log 2>&1 && ./run_tests 2>&1 | tail -1 )
