#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""t404 mutation campaign driver. Unlike r363r_mutate.py this REVERTS BY FILE
COPY from /tmp/t404-snap (the t404 edits are land-uncommitted — `git checkout
--` would destroy them; mutation-campaign skill rule 1).
Usage: t404_mutate.py <name> <src-rel> <old-file> <new-file>
"""
import shutil
import subprocess
import sys

ROOT = "/home/hrethric/projects/ascendancy"
SNAP = "/tmp/t404-snap"

name, src_rel, oldf, newf = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
src = f"{ROOT}/{src_rel}"
snap_name = src_rel.split("/")[-1]
s = open(src).read()
old = open(oldf).read()
new = open(newf).read()
n = s.count(old)
if n != 1:
    print(f"{name}: ANCHOR-ERROR count={n}")
    sys.exit(2)
open(src, "w").write(s.replace(old, new))
try:
    b = subprocess.run("cmake --build build -j2", shell=True, cwd=f"{ROOT}/rewrite",
                       capture_output=True, text=True)
    if b.returncode != 0:
        verdict, out = "CAUGHT (compile error)", ""
    else:
        r = subprocess.run("./build/run_tests", shell=True, cwd=f"{ROOT}/rewrite",
                           capture_output=True, text=True)
        out = r.stdout
        last = [l for l in out.splitlines() if "tests," in l]
        verdict = ("CAUGHT " + (last[-1] if last else "?")) if r.returncode != 0 or \
            (last and not last[-1].endswith("0 failed")) else "MISSED " + (last[-1] if last else "?")
finally:
    shutil.copy(f"{SNAP}/{snap_name}", src)
fails = [l.strip() for l in out.splitlines() if "FAIL" in l][:3]
print(f"{name}: {verdict}  {fails}")
