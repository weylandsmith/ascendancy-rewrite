#!/usr/bin/env python3
"""t363R mutation campaign driver: apply one mutant to shipsim.cpp, rebuild,
run the suite, revert. Prints CAUGHT (suite fails) / MISSED (suite green —
bad: the pins do not cover the law). Usage: mutate.py <name> <old-file> <new-file>
"""
import subprocess
import sys

SRC = "/home/hrethric/projects/ascendancy/rewrite/src/game/shipsim.cpp"

name, oldf, newf = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(SRC).read()
old = open(oldf).read()
new = open(newf).read()
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
subprocess.run("git checkout -- rewrite/src/game/shipsim.cpp", shell=True,
               cwd="/home/hrethric/projects/ascendancy")
fails = [l.strip() for l in out.splitlines() if "FAIL" in l][:3]
print(f"{name}: {verdict}  {fails}")
