#!/usr/bin/env python3
"""t366 mutation campaign driver (r363r_mutate.py shape): apply one mutant to
shipsave.cpp, rebuild, run the suite, revert. CAUGHT = suite fails (good).
Usage: r366_mutate.py <name> <old-str> <new-str>
Checkpoint e7ca7a2 precedes this campaign (skill rule 1); revert via git
checkout is SAFE because all pre-campaign work is committed.
"""
import subprocess
import sys

SRC = "/home/hrethric/projects/ascendancy/rewrite/src/formats/shipsave.cpp"

name, old, new = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(SRC).read()
n = s.count(old)
if n != 1:
    print(f"{name}: ANCHOR-ERROR count={n}")
    sys.exit(2)
open(SRC, "w").write(s.replace(old, new))
b = subprocess.run("cmake --build build -j2", shell=True, cwd=
                   "/home/hrethric/projects/ascendancy/rewrite",
                   capture_output=True, text=True)
if b.returncode != 0:
    verdict = "CAUGHT (compile error)"
    out = ""
else:
    r = subprocess.run("./build/run_tests", shell=True, cwd=
                       "/home/hrethric/projects/ascendancy/rewrite",
                       capture_output=True, text=True)
    out = r.stdout
    last = [l for l in out.splitlines() if "tests," in l]
    verdict = ("CAUGHT " + (last[-1] if last else "?")) if r.returncode != 0 or \
        (last and not last[-1].endswith("0 failed")) else "MISSED " + (last[-1] if last else "?")
subprocess.run("git checkout -- rewrite/src/formats/shipsave.cpp", shell=True,
               cwd="/home/hrethric/projects/ascendancy")
fails = [l.strip() for l in out.splitlines() if "FAIL" in l][:3]
print(f"{name}: {verdict}  {fails}")
