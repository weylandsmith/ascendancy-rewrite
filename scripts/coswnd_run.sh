#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later

# coswnd_run.sh (t73) — decompile the 36 coswnd.cpp functions never covered by
# any prior batch (banked t72; work/attribution.tsv module==coswnd.cpp, est_func
# column). OQ-021 static route: the t72 scan placed the end-ctrl string pool
# (STARS CONTROLLED %d @0x83b16, PERCENT CONTROLLED %d @0x83b2a) inside a
# GAMEWND/..\coswnd.cpp pool, so the threshold comparator should live in this
# module. Fresh read-only-ish project ghp6/ascend6 (ghp4 may hold locks; we do
# NOT mutate banked projects). Same image + conventions as seed3 (base 0,
# full auto-analysis via -postScript pattern). Writes work/ghp6,
# work/coswnd_decomp/*.c, work/decomp_coswnd.out exclusively.
# Fresh project ghp6/ascend6: import base 0x100000 + FULL auto-analysis (the
# verified ghp5 recipe — 1,144 functions; base-0 full analysis on a raw binary
# is unproven here). DecompileCombat adds imgBase to file-offset targets, so
# work/coswnd_decomp_targets.txt stays file offsets == addresses in the
# base-0 restored image. ghp4/ghp5 are NOT touched.
set -u
cd "$(dirname "$0")/.."
GHIDRA_HOME=${GHIDRA_HOME:-$HOME/tools/ghidra}
[ -f work/ascend_restored.bin ] || { echo "work/ascend_restored.bin missing"; exit 2; }
[ -s work/coswnd_decomp_targets.txt ] || { echo "targets file missing/empty"; exit 2; }
rm -rf work/ghp6 && mkdir -p work/ghp6 work/coswnd_decomp
export DECOMP_TARGETS="$PWD/work/coswnd_decomp_targets.txt"
export DECOMP_OUT="$PWD/work/coswnd_decomp"
"$GHIDRA_HOME/support/analyzeHeadless" work/ghp6 ascend6 \
  -import work/ascend_restored.bin -processor x86:LE:32:default -cspec gcc \
  -postScript DecompileCombat.java -scriptPath scripts/ghidra \
  > work/decomp_coswnd.out 2>&1
RC=$?
tail -c 2000 work/decomp_coswnd.out
ls work/coswnd_decomp | wc -l
exit $RC
