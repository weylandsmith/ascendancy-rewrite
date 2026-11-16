#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""t402 mutation campaign: apply one mutant, rebuild, run suite, revert by
FILE COPY from /tmp/t402-snap (the files are uncommitted — git checkout
would destroy the land; mutation-campaign skill rule 1).

Usage: t402_mutate.py <name> <src-rel-path> <old-snippet-file> <new-snippet-file>
Anchor guard: old snippet must occur EXACTLY ONCE.
"""
import shutil
import subprocess
import sys

ROOT = "/home/hrethric/projects/ascendancy"
SNAP = "/tmp/t402-snap"

name, rel, oldf, newf = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
path = f"{ROOT}/{rel}"
snap = f"{SNAP}/{rel.split('/')[-1]}"

s = open(path).read()
old = open(oldf).read()
new = open(newf).read()
n = s.count(old)
if n != 1:
    print(f"{name}: ANCHOR-ERROR count={n}")
    sys.exit(2)
open(path, "w").write(s.replace(old, new))
b = subprocess.run("make run_tests -j8", shell=True, cwd=f"{ROOT}/rewrite/build",
                   capture_output=True, text=True)
if b.returncode != 0:
    verdict = "CAUGHT (compile error)"
    out = ""
else:
    r = subprocess.run("./run_tests", shell=True, cwd=f"{ROOT}/rewrite/build",
                       capture_output=True, text=True)
    out = r.stdout
    last = [l for l in out.splitlines() if "tests," in l]
    green = r.returncode == 0 and last and last[-1].endswith("0 failed")
    verdict = ("MISSED " + last[-1]) if green else ("CAUGHT " + (last[-1] if last else "?"))
shutil.copy(snap, path)  # revert by copy, never git checkout
fails = [l.strip() for l in out.splitlines() if "FAIL" in l][:3]
print(f"{name}: {verdict}  {fails}")
