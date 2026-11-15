#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""t401 mutation campaign: one mutant at a time on menulaw.cpp/h pure law,
rebuild + run_tests, revert. Prints CAUGHT/MISSED + first FAIL line."""
import subprocess, subprocess as sp, sys

ROOT = "/home/hrethric/projects/ascendancy/rewrite"
SRC = ROOT + "/src/ui/menulaw.cpp"

MUTANTS = [
    ("M1 density-offladder-accept",
     "            if (rank < 0) return -1;  // off-ladder: refuse, never clamp",
     "            if (rank < 0) return 0;  // MUT"),
    ("M2 density-topshare",
     "            return rank >= 3 ? 3 : rank;  // top-two share = named seam",
     "            return rank;  // MUT"),
    ("M3 species-anchor",
     "            return 2 + value;",
     "            return 1 + value;  // MUT"),
    ("M4 atmosphere-swap",
     "            return value == 2 ? 11 : 10;",
     "            return value == 2 ? 10 : 11;  // MUT"),
    ("M5 portrait-clamp",
     "    if (specnum < 0 || specnum > 20) return std::string();  // refuse",
     "    if (specnum < 0) specnum = 0; if (specnum > 20) specnum = 20;  // MUT"),
    ("M6 portrait-nopad",
     '    std::snprintf(buf, sizeof(buf), "smrace%02d.shp", specnum);',
     '    std::snprintf(buf, sizeof(buf), "smrace%d.shp", specnum);  // MUT'),
]

results = []
for name, old, new in MUTANTS:
    s = open(SRC).read()
    n = s.count(old)
    if n != 1:
        print(f"{name}: ANCHOR-ERROR count={n}")
        results.append((name, "ANCHOR-ERROR"))
        continue
    open(SRC, "w").write(s.replace(old, new))
    b = sp.run("cmake --build build -j8", shell=True, cwd=ROOT, capture_output=True, text=True)
    if b.returncode != 0:
        verdict, first = "CAUGHT (compile error)", ""
    else:
        r = sp.run("./build/run_tests", shell=True, cwd=ROOT, capture_output=True, text=True)
        fails = [l for l in r.stdout.splitlines() if "FAIL" in l]
        verdict = "CAUGHT" if r.returncode != 0 else "MISSED"
        first = fails[0] if fails else (r.stdout.splitlines()[-1] if r.stdout else "")
    open(SRC, "w").write(s)  # revert
    print(f"{name}: {verdict}  {first[:90]}")
    results.append((name, verdict))

caught = sum(1 for _, v in results if v.startswith("CAUGHT"))
print(f"SUMMARY {caught}/{len(MUTANTS)} CAUGHT")
sys.exit(0 if caught == len(MUTANTS) else 1)
