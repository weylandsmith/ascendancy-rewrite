#!/usr/bin/env bash
# tPF-9 mutation campaign (rules: snapshot+md5 preflight, restore COPY-BACK
# then md5-verify, anchors at DEFINITION sites with count==1 assert, one
# mutant per run — skeleton per scripts/tPF8_mutate.sh).
set -u
cd "$(dirname "$0")/.."
U=rewrite/src/ui/ui.cpp
D=/tmp/tpf9_mut
mkdir -p $D
cp "$U" "$D/ui.cpp.snap"
md5sum $D/*.snap
a=$(md5sum "$U" | cut -d' ' -f1); b=$(md5sum "$D/ui.cpp.snap" | cut -d' ' -f1)
[ "$a" = "$b" ] || { echo "PREFLIGHT FAIL $U"; exit 2; }
restore() {
  cp "$D/ui.cpp.snap" "$U"
  a=$(md5sum "$U" | cut -d' ' -f1); b=$(md5sum "$D/ui.cpp.snap" | cut -d' ' -f1)
  [ "$a" = "$b" ] || { echo "RESTORE VERIFY FAIL $U"; exit 2; }
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
  ( cd rewrite/build && cmake --build . --target run_tests -j8 > /tmp/tpf9_mut/build.log 2>&1 )
  if [ $? -ne 0 ]; then echo "$name BUILD FAIL"; tail -5 /tmp/tpf9_mut/build.log; restore; return 1; fi
  OUT=$( cd rewrite/build && ./run_tests 2>&1 | grep -c "FAIL " )
  if [ "$OUT" -ge 1 ]; then echo "$name CAUGHT (failing checks: $OUT)"; else echo "$name SURVIVED"; fi
  restore
}

# M1: re-introduce the idle "click: set project" label (guard bypassed).
run_mutant M1_idle_hint_restored "$U" \
'                    if (projectOpen || planetPick >= 0)' \
'                    txt.draw(ren, pb.x0 + 6, pb.y1 - 14, "click: set project", false, kDim); if (projectOpen || planetPick >= 0)'

# M2: deletion overshoot — transient feedback killed too (anti-vacuity).
run_mutant M2_feedback_killed "$U" \
'                    if (projectOpen || planetPick >= 0)' \
'                    if (false)'

# M3: Escape ROUTING broken (label law must not eat the behaviour).
run_mutant M3_escape_routing_broken "$U" \
'ev.key.keysym.sym == SDLK_ESCAPE' \
'ev.key.keysym.sym == SDLK_TAB'

# M4: re-introduce the "Esc: return to galaxy" chrome label.
run_mutant M4_esc_label_restored "$U" \
'            // tPF-9 (D28 item 13 USER RULING + vendor-cited): the
            // "Esc: return to galaxy" chrome label is DELETED for ALL' \
'            if (interior.x1 > interior.x0) txt.draw(ren, interior.x0 + 8, interior.y1 - 16, "Esc: return to galaxy", false, kDim);
            // tPF-9 (D28 item 13 USER RULING + vendor-cited): the
            // "Esc: return to galaxy" chrome label is DELETED for ALL'

# Final sanity: tree back at snapshot and suite green.
a=$(md5sum "$U" | cut -d' ' -f1); b=$(md5sum "$D/ui.cpp.snap" | cut -d' ' -f1)
[ "$a" = "$b" ] || { echo "FINAL MD5 FAIL"; exit 2; }
( cd rewrite/build && cmake --build . --target run_tests -j8 > /tmp/tpf9_mut/build.log 2>&1 ) && \
  ( cd rewrite/build && ./run_tests 2>&1 | tail -1 )
echo MUTATE_DONE
