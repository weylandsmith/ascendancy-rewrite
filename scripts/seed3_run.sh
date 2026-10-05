#!/usr/bin/env bash
# seed3_run.sh — headless Ghidra bootstrap + data-xref export on the
# POINTER-LAW-restored image (docs/re/r1-savestate.md 2026-10-05i).
#   input  : work/ascend_restored.bin  (regenerate: scripts/r1_restore_sites.py)
#   outputs: work/functions3.tsv, work/code2data.tsv, work/seed3.out
# Safety: ghidra-only; writes work/ exclusively; log bounded by caller.
set -u
cd "$(dirname "$0")/.."
GHIDRA_HOME=${GHIDRA_HOME:-$HOME/tools/ghidra}
[ -f work/ascend_restored.bin ] || { echo "work/ascend_restored.bin missing (run scripts/r1_restore_sites.py)"; exit 2; }
rm -rf work/ghp4 && mkdir -p work/ghp4
"$GHIDRA_HOME/support/analyzeHeadless" work/ghp4 ascend4 \
  -import work/ascend_restored.bin -processor x86:LE:32:default -cspec gcc \
  -noanalysis -scriptPath scripts/ghidra -postScript Seed3.java \
  > work/seed3.out 2>&1
RC=$?
tail -c 3000 work/seed3.out
exit $RC
